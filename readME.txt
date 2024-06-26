[avg_sed_rate_tacc] contains the files to run the code from the submitted paper to Marine Geology.

[input_files] contains seafloor data used for the PFLOTRAN simulation:

[example_output] contains the output file for "Location 1" from figures 8 and 10. Due to the quantity of files being created, outputs for other simulations could not be uploaded. However these simulations can be run using the code in [avg_sed_rate_tacc]. A summary of the simulations that were run and used for the maps presented in the associated paper are included in [avg_sed_rate_tacc]/[output].


To run these simulations, PFLOTRAN must be installed. PFLOTRAN is an open source software.


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[avg_sed_rate_tacc]

To run, either run [multi_test.py] with the current data which will run all the locations listed in [locations_to_run.csv] or run an individual location in [aaa_runProfile]. 

Seafloor depth data (Spratt and Lisiecki, 2016) and temperature data (Sosdian and Rosenthal, 2009) over the last 120,000 years is available in the files [aa_sf_depth.txt] and [aa_temperature] respectively.


Files to look at:

run_no_sampling.sh: uncomment out last line "rm -R $output_dir if you want to run all locations (or a lot of locations) or your computer will run out of hard drive space.
	-- be careful as this is a recursive removal

get_input_data.py: change data path in line 54

multi_test.py: change data path in line 8

pflotran_run.py: change data path in line 73

[output] - Output grids for minimum/maximum along entire profile, entire profile minus the seafloor, and profiles going to sediment depths of 200, 350, and 500 mbsf (excluding the seafloor).


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


[input_files]

porosity.nc: 5 arc-minute resolution seafloor porosity data from Carty and Daigle, 2022.
TOC.nc: 5 arc-minute resolution seafloor total organic carbon data from Carty and Daigle, 2022.