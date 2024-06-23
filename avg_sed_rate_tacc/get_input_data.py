# File to get the input data given a lat, lon input
# Combining a few other files that I had earlier so I only have to run one script

import numpy as np
import netCDF4
import warnings
import sys

warnings.filterwarnings('ignore', category=DeprecationWarning)


# FindLocation_netCDF4.py
# laty and lonx are strings for "lat"/"y" or "lon"/"x" depending on how the netCDF file is set up
def find_location(filename_nc, lat_check, lon_check, laty='lat', lonx='lon'):
    fp = filename_nc  # your file name with the eventual path
    nc = netCDF4.Dataset(fp)  # reading the nc file and creating Dataset

    lat = nc[f'{laty}'][:]
    lon = nc[f'{lonx}'][:]
    z = nc['z'][:]

    lat_calculated_diff = np.abs(lat_check - lat)
    lat_min_index = np.argmin(lat_calculated_diff)

    lon_calculated_diff = np.abs(lon_check - lon)
    lon_min_index = np.argmin(lon_calculated_diff)

    return z[lat_min_index][lon_min_index]


def depth_and_slope(filename_csv, lat_check, lon_check):
    data = np.genfromtxt(filename_csv, delimiter=',')
    data_loc = np.argmin(abs(lat_check - data[:, 0]) + abs(lon_check- data[:, 1]))
    depth = data[data_loc, 2]
    slope = data[data_loc, 3]
    return depth, slope


# Polynomial fit from Daigle to get temperature with depth
def get_temp(depth):
    depth = abs(depth)
    temp = 5.44983556e-16 * depth**6 \
           - 1.64076731e-12 * depth**5 \
           + 1.76273627e-09 * depth**4 \
           - 7.74644090e-07 * depth**3 \
           + 1.07505928e-04 * depth**2 \
           - 8.60566355e-03 * depth \
           + 1.25040556e+01
    return temp


# # I hardcoded my data files in here but you can just change them or add it as an input
def get_all_data(lat, lon, time, period, cycles):
    input_path = '~/{input_folder_path}'  # edit to be path containing the "input_files" folder

    lat = float(lat)
    lon = float(lon)

    TOC = find_location(f'{input_path}/input_files/TOC.nc', lat, lon, laty='lat', lonx='lon')
    depth, slope = depth_and_slope(f'{input_path}/avg_sed_rate_tacc/locations_to_run.csv', lat, lon)  # for standard res locations
    temp = get_temp(depth)
    porosity = find_location(f'{input_path}/input_files/porosity.nc', lat, lon)

    print(f'\n',
          f'LATITUDE: {lat}\n',
          f'LONGITUDE: {lon}')

    with open('aa_run_inputs.yaml', 'w') as myfile:
        myfile.write(f'\n')
        myfile.write(f'Latitude: {lat}\n')
        myfile.write(f'Longitude: {lon}\n')
        myfile.write(f'Water Depth (m): {depth}\n')
        myfile.write(f'Seafloor Temp (C): {temp}\n')
        myfile.write(f'Heat Flux (mW/m^2): 48\n')
        myfile.write(f'Heat Flux St Dev (mW/m^2): 2\n')
        myfile.write(f'\n')
        myfile.write(f'Years: {time}\n')
        myfile.write(f'Periodic: {period}\n')
        myfile.write(f'Cycles: {cycles}\n')
        myfile.write(f'Seed: 1234\n')
        myfile.write(f'\n')
        myfile.write(f'TOC (percent dry weight): {TOC}\n')
        myfile.write(f'Porosity (%): {porosity}\n')
        myfile.write(f'\n')
        myfile.write(f'Slope: {slope}\n')


if __name__ == '__main__':
    # Map command line arguments to function arguments.
    get_all_data(*sys.argv[1:])

