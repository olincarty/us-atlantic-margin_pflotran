from aaa_runProfile import *
from multiprocessing.pool import Pool
import numpy as np

import time
start_time = time.time()

file = '~/{path_to_file}/avg_sed_rate_tacc/locations_to_run.csv'  # change path_to_file so this location exists

data_to_run = np.genfromtxt(file, delimiter=',')
#print(len(data_to_run))
if __name__ == "__main__":
    with Pool(64) as pool:
        locations = [(i[0], i[1]) for i in data_to_run[:]]
        pool.starmap(run_profile, locations)


print("--- %s seconds ---" % (time.time() - start_time))
