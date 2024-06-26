#!/bin/bash

mkdir all_tec_files

# added next to in to make looping data manipulation easier
rm pflotran_cycle_1-001.tec
#rm pflotran_cycle_2-001.tec
#mv pflotran_cycle_2-001.tec pflotran_cycle_3-000.tec

mv pflotran_*.tec all_tec_files

# go into the all_tec_files folder and make a list file of documents
cd all_tec_files
ls > file_list.txt