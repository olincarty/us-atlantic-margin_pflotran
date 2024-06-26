import numpy as np
import yaml


with open('aa_run_inputs.yaml') as f:
    inputs = yaml.full_load(f)
lat = inputs['Latitude']
lon = inputs['Longitude']
slope = inputs['Slope']
toc_pct = inputs['TOC (percent dry weight)']
water_depth_base = inputs['Water Depth (m)']  # new line
sf_temp_base = inputs['Seafloor Temp (C)']  # new line

with open('../output/data_full.csv', 'a') as myfile:
    myfile.write('\n')
    myfile.write(f'{lat}, {lon}, {toc_pct}, {water_depth_base}, {sf_temp_base}, {slope},'
                 f'{np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan}, {np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan}, {np.nan},'
                 f'{np.nan},'
                 f'{np.nan}, {np.nan}, {np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan}')

with open('../output/data_no_sf.csv', 'a') as myfile:
    myfile.write('\n')
    myfile.write(f'{lat}, {lon}, {toc_pct}, {water_depth_base}, {sf_temp_base}, {slope},'
                 f'{np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan}, {np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan}, {np.nan},'
                 f'{np.nan},'
                 f'{np.nan}, {np.nan}, {np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan}')

with open('../output/data_500.csv', 'a') as myfile:
    myfile.write('\n')
    myfile.write(f'{lat}, {lon}, {toc_pct}, {water_depth_base}, {sf_temp_base}, {slope},'
                 f'{np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan}, {np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan}, {np.nan},'
                 f'{np.nan},'
                 f'{np.nan}, {np.nan}, {np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan}')

with open('../output/data_200.csv', 'a') as myfile:
    myfile.write('\n')
    myfile.write(f'{lat}, {lon}, {toc_pct}, {water_depth_base}, {sf_temp_base}, {slope},'
                 f'{np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan}, {np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan}, {np.nan},'
                 f'{np.nan},'
                 f'{np.nan}, {np.nan}, {np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan}')
    
with open('../output/data_350.csv', 'a') as myfile:
    myfile.write('\n')
    myfile.write(f'{lat}, {lon}, {toc_pct}, {water_depth_base}, {sf_temp_base}, {slope},'
                 f'{np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan}, {np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan}, {np.nan},'
                 f'{np.nan},'
                 f'{np.nan}, {np.nan}, {np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan},'
                 f'{np.nan}, {np.nan}')
