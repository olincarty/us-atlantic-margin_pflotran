#!/bin/bash

profile_name=${1}
lat=${2}
lon=${3}
time=${4}
period=${5}
cycles=${6}

output_dir=loc$profile_name

mkdir $output_dir


cp pflotran_run.py clean_up_tec.sh output_data.py failure_test.py generate_pflotran.py $output_dir/
cp aa_sf_depth.txt aa_temperature.txt $output_dir/


cd $output_dir || { echo 'my_command failed' ; exit 1; }  # exits if command fail (although it never should)

python3 ../get_input_data.py $lat $lon $time $period $cycles  # using local path here to run python
python3 pflotran_run.py
sh clean_up_tec.sh

FILE=./all_tec_files/pflotran_cycle_2-1200.tec
if test -f "$FILE"; then
  python3 output_data.py
else
  python3 failure_test.py
fi

cd ..

# this can be commented out to keep the output directory but should stay in if you are running multiple files in parallel or you will run out of room on your computer.
# be careful here as there is a remove command
# rm -R $output_dir
