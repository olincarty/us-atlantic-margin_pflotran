import yaml
import numpy as np
import scipy.stats as stats
import h5py as h5
import subprocess
import os

# import sys
# sys.path.append('/work/07208/orc323/ls6/avg_sed_rate')
# sys.path.append('/Users/olincarty/Documents/methane_hydrate_work/gpsm_pflotran_dakota_setup/avg_sed_rate_tacc')
from generate_pflotran import *


# ================= Collect variables for PFLOTRAN Input Deck ================= #

# get data from the yaml file created earlier
with open('aa_run_inputs.yaml') as f:
    inputs = yaml.full_load(f)
Lat = inputs['Latitude']
Lon = inputs['Longitude']
seafloor_depth = abs(inputs['Water Depth (m)'])
seafloor_temp = inputs['Seafloor Temp (C)']
testTime = inputs['Years']
periodicTime = inputs['Periodic']
cycles = inputs['Cycles']

v_cm_yr = 0.063202419  # sed_rates_ODP1073.xlsx
q_mW = inputs['Heat Flux (mW/m^2)']
c_pct = inputs['TOC (percent dry weight)']
por_0_pct = inputs['Porosity (%)']


# calculating variables in correct units
year_sec = 60*60*24*365.25
percent = 100
org_carbon_frac = c_pct/percent
heat_flux = q_mW/1000
pScale = por_0_pct/percent
methanogenesis_rate = 5e-14


# More set values
therm_cond = 1.0
smt_depth = 15
sed_thick = 1000  # Thickness in meters


# Decay portion of porosity curve from Kominz et al. 2011
Phi = np.zeros(int(sed_thick))
for i in range(int(sed_thick)):
    Phi[-i - 1] = np.exp(-i / 1251)
porosity = pScale * Phi

# Permeability curve based off of porosity (Dugan and Flemings 2002)
perm_I = -16.553
perm_B = 0.2832
perm = 10**(perm_I + perm_B * porosity)


# Use porosity to calculate composite thermal conductivity
# Calculate composite thermal conductivity 06/24/2020
kDry = 1.0
kWater = 0.59
K_hm = stats.hmean(porosity) * kWater + kDry

# Calculate gradient from heat flux and composite conductivity 6/11/2020
geothermal_gradient = -heat_flux/K_hm


# ################################################### #

# path to sf_depth, temperature, and sed_rate files
data_path = f'/work/07208/orc323/ls6/avg_sed_rate_tacc'
# data_path = f'/Users/olincarty/Documents/methane_hydrate_work/gpsm_pflotran_dakota_setup/avg_sed_rate_tacc'

# changing pressure at different times
sf_file = np.genfromtxt(f'{data_path}/aa_sf_depth.txt', delimiter='\t')
if np.shape(sf_file)[1] == 2:  # sets up array of arrays so loop works properly
    pass
else:
    np.array([sf_file])
year_list_p = sf_file[:, 0]
sf_pm = sf_file[:, 1]
sf_pres_list = (seafloor_depth + sf_pm) * 9.8 * 1024  # density is 1024 for seawater
seafloor_pressure = sf_pres_list[0]

# setting temperature over time
t_file = np.genfromtxt(f'{data_path}/aa_temperature.txt', delimiter='\t')
if np.shape(t_file)[1] == 2:  # sets up array of arrays so loop works properly
    pass
else:
    np.array([t_file])
year_list_t = t_file[:, 0]
sf_temp = t_file[:, 1]
sf_temp_list = seafloor_temp + sf_temp
seafloor_temperature = sf_temp_list[0]

sed_rate_m_s = v_cm_yr * (1/100) / year_sec  # convert cm/y to m/s


# get new dictionaries of dictionaries of pressure and temperature lists
# format: {run_val (start at 0): {time_0: value_0, time_1: value_1, etc.}
# where time_0 = 0 is the initial condition i.e. NOT present time
p_data = dict(zip(year_list_p, sf_pres_list))
t_data = dict(zip(year_list_t, sf_temp_list))


# ################################################### #


# Ensure all_data values are zero or positive 02/13/2020
if org_carbon_frac < 0.0:  # seafloor TOC
    org_carbon_frac = 0.0
if sed_rate_m_s < 0.0:  # sedimentation rate
    sed_rate_m_s = 0.0
if heat_flux < 0.0:
    heat_flux = 0.0
if seafloor_temp < 0.0:  # seafloor temperature
    seafloor_temp = 0.0
for key in t_data:  # other temperature values
    if t_data[key] < 0:
        t_data[key] = 0
if seafloor_pressure < 0.0:  # seafloor pressure
    seafloor_pressure = 0.0
for key in p_data:  # other pressure values
    if p_data[key] < 0:
        p_data[key] = 0


# ################################################### #


org_carbon_frac = 0.75 * org_carbon_frac  # Assume 75% of TOC available 02/04/2020

# Create HDF5 file of data for the PFLOTRAN run
# Here we have only done porosity and permeability data
with h5.File('./phi_k_dataset.h5', 'w') as f:
    f.create_group('porosity')
    f['porosity'].create_dataset('Data', data=porosity)
    # Follow group attributes for cell-centered example
    f['porosity'].attrs.create('Dimension', ['Z'], dtype='|S2')
    f['porosity'].attrs.create('Discretization', [1.0])  # 1 meter
    f['porosity'].attrs.create('Origin', [0.0])
    f['porosity'].attrs.create('Cell Centered', [True])

with h5.File('./perm_dataset.h5', 'w') as f:
    f.create_group('perm')
    f['perm'].create_dataset('Data', data=perm)
    # Follow group attributes for cell-centered example
    f['perm'].attrs.create('Dimension', ['Z'], dtype='|S2')
    f['perm'].attrs.create('Discretization', [1.0])  # 1 meter
    f['perm'].attrs.create('Origin', [0.0])
    f['perm'].attrs.create('Cell Centered', [True])


# ################################################### #

# First we will create all the .in files for a single run. Later we will run them
# From above, the length of the dictionaries "t_data" and "p_data" are equal to len(sed_rate_m_s)
# We will have a number of files equal to this length

# The lists/dictionaries we have to work with are:
#     t_data - dictionary of temperature data for each run
#     p_data - dictionary of pressure data for each runm
#     sed_rate_m_s - sedimentation rate for each run
#     test_time - the time (years) for each run -- this array should add up to the total test time
#     run_number - a list from 0 to n of numbers to append for checkpoint purposes



# need to set up each simulation start differently
for cyc in range(1, cycles+1):

    if cyc == 1:  # first run
        simulation = gen_simulation_first()
        if cyc == cycles:
            output = gen_output(periodicTime)  # use the same periodic time for results of each run if one cycle
        else:
            output = gen_output(testTime)  # want to run through quickly on the first cycle

    # #
    else:  # other runs
        dir_path = os.path.dirname(os.path.realpath(__file__))
        restart_name = f'pflotran_cycle_{cyc-1}-restart.chk'
        simulation = gen_simulation_other(restart_name)
        if cyc == cycles:
            output = gen_output(periodicTime)  # use the same periodic time for results of each run for final cycle
        else:
            output = gen_output(testTime)  # want to run through quickly on the middle cycles

    # #
    # the rest of the input data will be the same
    datasets = gen_datasets()  # can choose to rename the porosity data (above)
    grid = gen_grid(sed_thick)
    region = gen_region(sed_thick)
    hydrate = gen_hydrate(org_carbon_frac, methanogenesis_rate, sed_rate_m_s, smt_depth)
    fluid_prop = gen_fluid_prop()
    mat_prop = gen_mat_prop(therm_cond)
    char_curves = gen_char_curves()
    strata = gen_strata()
    time = gen_time(testTime)  # need test time to be run specific

    # may need to edit flow_cond to change seafloor_pressure, seafloor_temperature but we will see
    flow_cond = gen_flow_cond(sed_thick, geothermal_gradient, seafloor_pressure, seafloor_temperature,
                              p_data, t_data, heat_flux)
    init_cond = gen_init_cond()

    # all parts of file labeled
    file_prefix = f'pflotran_cycle_{cyc}'
    with open(f'{file_prefix}.in', 'w') as f:
        f.write(simulation)
        f.write(grid)
        f.write(datasets)
        f.write(region)
        f.write(hydrate)
        f.write(fluid_prop)
        f.write(mat_prop)
        f.write(char_curves)
        f.write(strata)
        f.write(time)
        f.write(output)
        f.write(flow_cond)
        f.write(init_cond)
        f.write("\nEND_SUBSURFACE\n\n")

    # #
    # we now have all the files created as well as a list of all the file prefixes so we can run everything!
    # run all files

    bashCommand = f'ibrun -n 1 pflotran -input_prefix {file_prefix}'
    # bashCommand = f'mpirun -n 1 pflotran -input_prefix {file_prefix}'
    subprocess.run(bashCommand.split(), stdout=subprocess.DEVNULL)


print(f'Simulation done')
