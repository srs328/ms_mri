#!/bin/bash

subid=$1
script=/home/shridhar.singh9-umw/Projects/ms_mri/longitudinal_pipeline/two_point/get_thomas_deformations.py

echo "Calling $script with $subid"
python $script $subid || exit 1
echo "Called $script with $subid"
