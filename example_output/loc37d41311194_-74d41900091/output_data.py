import numpy as np
from scipy import integrate
import yaml

# import time
# start_time = time.time()

# constants
rho_w = 1024  # kg/m**3 - from internet
rho_s = 2700  # kg/m**3
rho_h = 925
gravity = 9.8  # m/s**2


def u_h_from_sf_Pa(p_0, depth, depth_0):
    u_h = p_0 + (depth - depth_0) * rho_w * gravity
    return u_h


# changing this because we are calculating porosity based on the 0.5 m depth
def porosity_kominz_step(depth, depth_0, phi0):
    porosity = phi0 * np.exp(-(depth - depth_0) / 1251)
    return porosity


def bulk_density(depth, depth_0, rho_l, rho_g, s_l, s_g, s_h, phi0):
    phi = porosity_kominz_step(depth, depth_0, phi0)
    rho_b = (1 - phi) * rho_s + phi * (s_l * rho_l + s_g * rho_g * s_h * rho_h)
    return rho_b


def sig_v_from_sf_Pa(p_0, z_sed, rho_l, rho_g, s_l, s_g, s_h, phi0):
    sig_v_Pa = p_0 + gravity * integrate.quad(bulk_density, 0, z_sed, args=(rho_l, rho_g, s_l, s_g, s_h, phi0))[0]
    return sig_v_Pa


def factor_of_safety(eff_stress_mpa, u_over_mpa, theta=4):
    # theta is sf_slope angle
    c = 0  # sediment cohesion
    phi_f = 32  # internal friction angle
    F_eq = 0  # earthquake acceleration shear stress parallel to the slope
    fs_top = c + ((eff_stress_mpa * np.cos(np.deg2rad(theta)) ** 2) - u_over_mpa) * np.tan(np.deg2rad(phi_f))
    fs_bot = eff_stress_mpa * np.cos(np.deg2rad(theta)) * np.sin(np.deg2rad(theta)) + F_eq
    fs = fs_top / fs_bot
    return fs


# shortened list of header names
headers_short = {'z': 2,
                 't': 3,
                 'u_l': 4,
                 'u_g': 5,
                 's_l': 6,
                 's_g': 7,
                 's_h': 8,
                 'rho_l': 9,
                 'rho_g': 10,
                 'perm': 11,
                 'por': 12}


with open('all_tec_files/file_list.txt') as f:
    tec_files = f.read().splitlines()
tec_files = tec_files[1:]
tec_num = len(tec_files)


with open('aa_run_inputs.yaml') as f:
    inputs = yaml.full_load(f)
end_time = inputs['Years']
dt = inputs['Periodic']
cycles = inputs['Cycles']
lat = inputs['Latitude']
lon = inputs['Longitude']
slope = inputs['Slope']
toc_pct = inputs['TOC (percent dry weight)']
water_depth_base = inputs['Water Depth (m)']  # new line
sf_temp_base = inputs['Seafloor Temp (C)']  # new line
time_list_full = np.arange(dt, end_time+dt, dt)  # starting at whatever dt is rather than 0

base_depth = 1000  # depth of bottom of model zone
# need data for fs_min_depth, fs_min, eff_v, overpressure
depth_data_full = np.zeros([tec_num, 12])  # full 0-1000 m
depth_data_full[:,0] = time_list_full
depth_data_no_sf = np.zeros([tec_num, 12])  # 5-1000 m
depth_data_no_sf[:,0] = time_list_full
depth_data_200 = np.zeros([tec_num, 12])  # 5-200 m
depth_data_200[:,0] = time_list_full
depth_data_500 = np.zeros([tec_num, 12])  # 5-500 m
depth_data_500[:,0] = time_list_full
depth_data_350 = np.zeros([tec_num, 12])  # 5-500 m
depth_data_350[:,0] = time_list_full


for tec in range(tec_num):
    tec_count = tec + 1
    arrays = np.genfromtxt(f'all_tec_files/pflotran_cycle_{cycles}-{str(tec_count).zfill(3)}.tec', skip_header=3)
    data = {i: arrays[:, headers_short[i]] for key, i in enumerate(headers_short)}
    # sets up depth array so it is in same order as the data table.
    depth = data['z'][::-1]
    depth_0 = depth[-1]  # depth of first value under the sf

    # solve for stresses/pressures (u_g, pi term, u_h, etc)
    u_g = data['u_g']
    u_g = np.where(data['s_g'] == 0, 0, u_g)  # gas pressure is 0 when there is no gas
    pi_term = (1 - data['s_g']) * data['u_l'] + data['s_g'] * data['u_g']
    u_h = u_h_from_sf_Pa(data['u_l'][-1], depth, depth_0)

    rho_b = bulk_density(depth, depth_0,
                         data['rho_l'], data['rho_g'],
                         data['s_l'], data['s_g'], data['s_h'],
                         phi0=data['por'][-1]
                         )
    # sum backwards and then reverse again
    rho_b_cumsum = integrate.cumulative_trapezoid(rho_b[::-1], depth[::-1], initial=0)[::-1]
    # vertical stress is now the (cumulative sum at each point) * gravity + seafloor pressure)
    sig_v = rho_b_cumsum * gravity + data['u_l'][-1]

    # everything above here is done in Pa units so we need to switch to MPa to calculate fs
    # Factor of safety calculation
    eff_stress_mpa = (sig_v - pi_term) / 1e6
    u_over_mpa = (pi_term - u_h) / 1e6  # overpressure term (MPa)
    fs = factor_of_safety(eff_stress_mpa, u_over_mpa, slope)

    s_h = data['s_h']
    s_g = data['s_g']

    # create table of values at all depths (will make grabbing the minimums within certain ranges easier)
    # depth is depth of minimum fs for a given tech file
    stress_data = np.array([depth, fs, eff_stress_mpa, u_over_mpa, sig_v, s_h, s_g]).T
    s_h_data = np.array([s_h, depth]).T
    s_g_data = np.array([s_g, depth]).T

    # now calculate the fs_min and create arrays with fs_min_depth, eff_v, overpressure
    # looking at all depths (nanmin ignores nan at sf)
    loc_full = np.nanargmin(fs)
    depth_data_full[tec, 1:8] = stress_data[loc_full]
    depth_data_full[tec, 8:10] = s_h_data[np.argmax(s_h)]
    depth_data_full[tec, 10:12] = s_g_data[np.argmax(s_g)]

    # full depth with no sf (5-1000 m)
    loc_no_sf = np.nanargmin(fs[:-5])
    depth_data_no_sf[tec, 1:8] = stress_data[:-5][loc_no_sf]
    depth_data_no_sf[tec, 8:10] = s_h_data[:-5][np.argmax(s_h[:-5])]
    depth_data_no_sf[tec, 10:12] = s_g_data[:-5][np.argmax(s_g[:-5])]

    # up to 500 m (5-500 m)
    loc_500 = np.nanargmin(fs[-500:-5])
    depth_data_500[tec, 1:8] = stress_data[-500:-5][loc_500]
    depth_data_500[tec, 8:10] = s_h_data[-500:-5][np.argmax(s_h[-500:-5])]
    depth_data_500[tec, 10:12] = s_g_data[-500:-5][np.argmax(s_g[-500:-5])]

    # up to 200 m (5-200 m)
    loc_200 = np.nanargmin(fs[-200:-5])
    depth_data_200[tec, 1:8] = stress_data[-200:-5][loc_200]
    depth_data_200[tec, 8:10] = s_h_data[-200:-5][np.argmax(s_h[-200:-5])]
    depth_data_200[tec, 10:12] = s_g_data[-200:-5][np.argmax(s_g[-200:-5])]
    
    # up to 350 m (5-200 m)
    loc_350 = np.nanargmin(fs[-350:-5])
    depth_data_350[tec, 1:8] = stress_data[-350:-5][loc_350]
    depth_data_350[tec, 8:10] = s_h_data[-350:-5][np.argmax(s_h[-350:-5])]
    depth_data_350[tec, 10:12] = s_g_data[-350:-5][np.argmax(s_g[-350:-5])]


# finding timing of min_fs (max_sh, and max_sg) to print out
data_full_a = depth_data_full[np.argmin(depth_data_full[:, 2])]
data_full_116000 = depth_data_full[1159]  # new addition to look at time 116000
s_h_full_a = depth_data_full[np.argmax(depth_data_full[:, 8])]
s_g_full_a = depth_data_full[np.argmax(depth_data_full[:, 10])]

data_no_sf_a = depth_data_no_sf[np.argmin(depth_data_no_sf[:, 2])]
data_no_sf_116000 = depth_data_no_sf[1159]  # new addition to look at time 116000
s_h_no_sf_a = depth_data_no_sf[np.argmax(depth_data_no_sf[:, 8])]
s_g_no_sf_a = depth_data_no_sf[np.argmax(depth_data_no_sf[:, 10])]

data_500_a = depth_data_500[np.argmin(depth_data_500[:, 2])]
data_500_116000 = depth_data_500[1159]  # new addition to look at time 116000
s_h_500_a = depth_data_500[np.argmax(depth_data_500[:, 8])]
s_g_500_a = depth_data_500[np.argmax(depth_data_500[:, 10])]

data_200_a = depth_data_200[np.argmin(depth_data_200[:, 2])]
data_200_116000 = depth_data_200[1159]  # new addition to look at time 116000
s_h_200_a = depth_data_200[np.argmax(depth_data_200[:, 8])]
s_g_200_a = depth_data_200[np.argmax(depth_data_200[:, 10])]

data_350_a = depth_data_350[np.argmin(depth_data_350[:, 2])]
data_350_116000 = depth_data_350[1159]  # new addition to look at time 116000
s_h_350_a = depth_data_350[np.argmax(depth_data_350[:, 8])]
s_g_350_a = depth_data_350[np.argmax(depth_data_350[:, 10])]


# columns are:  lat, lon, toc, base water depth, base temperature, slope
#               time, depth (below sf),
#               fs, effective vertical stress [MPa], overpressure [MPa],  sig_v,
#               sh, sg,
#               sh_max, sh_max_depth, sh_max_time,
#               sg_max, sg_max_depth, sg_max_time
#               above stuff but for time at 116000
# NOTE!! time is NOT before present. It is based off the start time counting forward
# append data to final files
with open('../output/data_full.csv', 'a') as myfile:
    myfile.write('\n')
    myfile.write(f'{lat}, {lon}, {toc_pct}, {water_depth_base}, {sf_temp_base}, {slope},'
                 f'{data_full_a[0]},{data_full_a[1]},'
                 f'{data_full_a[2]}, {data_full_a[3]}, {data_full_a[4]}, {data_full_a[5]},'
                 f'{data_full_a[6]}, {data_full_a[7]},'
                 f'{s_h_full_a[8]}, {s_h_full_a[9]}, {s_h_full_a[0]},'
                 f'{s_g_full_a[10]}, {s_g_full_a[11]}, {s_g_full_a[0]},'
                 f'{data_full_116000[1]},'
                 f'{data_full_116000[2]}, {data_full_116000[3]}, {data_full_116000[4]}, {data_full_116000[5]},'
                 f'{data_full_116000[6]}, {data_full_116000[7]},'
                 f'{data_full_116000[8]}, {data_full_116000[9]},'
                 f'{data_full_116000[10]}, {data_full_116000[11]}')

with open('../output/data_no_sf.csv', 'a') as myfile:
    myfile.write('\n')
    myfile.write(f'{lat}, {lon}, {toc_pct}, {water_depth_base}, {sf_temp_base}, {slope},'
                 f'{data_no_sf_a[0]}, {data_no_sf_a[1]},'
                 f'{data_no_sf_a[2]}, {data_no_sf_a[3]}, {data_no_sf_a[4]}, {data_no_sf_a[5]},'
                 f'{data_no_sf_a[6]}, {data_no_sf_a[7]},'
                 f'{s_h_no_sf_a[8]}, {s_h_no_sf_a[9]}, {s_h_no_sf_a[0]},'
                 f'{s_g_no_sf_a[10]}, {s_g_no_sf_a[11]}, {s_g_no_sf_a[0]},'
                 f'{data_no_sf_116000[1]},'
                 f'{data_no_sf_116000[2]}, {data_no_sf_116000[3]}, {data_no_sf_116000[4]}, {data_no_sf_116000[5]},'
                 f'{data_no_sf_116000[6]}, {data_no_sf_116000[7]},'
                 f'{data_no_sf_116000[8]}, {data_no_sf_116000[9]},'
                 f'{data_no_sf_116000[10]}, {data_no_sf_116000[11]}')

with open('../output/data_500.csv', 'a') as myfile:
    myfile.write('\n')
    myfile.write(f'{lat}, {lon}, {toc_pct}, {water_depth_base}, {sf_temp_base}, {slope},'
                 f'{data_500_a[0]}, {data_500_a[1]},'
                 f'{data_500_a[2]}, {data_500_a[3]}, {data_500_a[4]}, {data_500_a[5]},'
                 f'{data_500_a[6]}, {data_500_a[7]},'
                 f'{s_h_500_a[8]}, {s_h_500_a[9]}, {s_h_500_a[0]},'
                 f'{s_g_500_a[10]}, {s_g_500_a[11]}, {s_g_500_a[0]},'
                 f'{data_500_116000[1]},'
                 f'{data_500_116000[2]}, {data_500_116000[3]}, {data_500_116000[4]}, {data_500_116000[5]},'
                 f'{data_500_116000[6]}, {data_500_116000[7]},'
                 f'{data_500_116000[8]}, {data_500_116000[9]},'
                 f'{data_500_116000[10]}, {data_500_116000[11]}')

with open('../output/data_200.csv', 'a') as myfile:
    myfile.write('\n')
    myfile.write(f'{lat}, {lon}, {toc_pct}, {water_depth_base}, {sf_temp_base}, {slope},'
                 f'{data_200_a[0]}, {data_200_a[1]},'
                 f'{data_200_a[2]}, {data_200_a[3]}, {data_200_a[4]}, {data_200_a[5]},'
                 f'{data_200_a[6]}, {data_200_a[7]},'
                 f'{s_h_200_a[8]}, {s_h_200_a[9]}, {s_h_200_a[0]},'
                 f'{s_g_200_a[10]}, {s_g_200_a[11]}, {s_g_200_a[0]},'
                 f'{data_200_116000[1]},'
                 f'{data_200_116000[2]}, {data_200_116000[3]}, {data_200_116000[4]}, {data_200_116000[5]},'
                 f'{data_200_116000[6]}, {data_200_116000[7]},'
                 f'{data_200_116000[8]}, {data_200_116000[9]},'
                 f'{data_200_116000[10]}, {data_200_116000[11]}')

with open('../output/data_350.csv', 'a') as myfile:
    myfile.write('\n')
    myfile.write(f'{lat}, {lon}, {toc_pct}, {water_depth_base}, {sf_temp_base}, {slope},'
                 f'{data_350_a[0]}, {data_350_a[1]},'
                 f'{data_350_a[2]}, {data_350_a[3]}, {data_350_a[4]}, {data_350_a[5]},'
                 f'{data_350_a[6]}, {data_350_a[7]},'
                 f'{s_h_350_a[8]}, {s_h_350_a[9]}, {s_h_350_a[0]},'
                 f'{s_g_350_a[10]}, {s_g_350_a[11]}, {s_g_350_a[0]},'
                 f'{data_350_116000[1]},'
                 f'{data_350_116000[2]}, {data_350_116000[3]}, {data_350_116000[4]}, {data_350_116000[5]},'
                 f'{data_350_116000[6]}, {data_350_116000[7]},'
                 f'{data_350_116000[8]}, {data_350_116000[9]},'
                 f'{data_350_116000[10]}, {data_350_116000[11]}')

# print("--- %s seconds ---" % (time.time() - start_time))
