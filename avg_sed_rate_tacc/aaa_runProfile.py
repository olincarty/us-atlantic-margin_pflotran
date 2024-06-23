import os

# naming convention: instead of Profile12345 use lat72d1234_lon-37d1234


def run_profile(lat, lon, time=120000, period=100, cycles=2):

    lat_string = str(lat)
    lon_string = str(lon)
    latlon = f'{lat_string}_{lon_string}'
    profile_latlon = latlon.replace('.', 'd')

    os.system(f'sh run_no_sampling.sh {profile_latlon} {lat} {lon} {time} {period} {cycles}')

# run_profile(37.41311194, -74.41900091)

# check the "run_no_sampling.sh" file if you switch cycles away from 2
# line 25: "FILE=./all_tec_files/pflotran_cycle_2-1200.tec"
