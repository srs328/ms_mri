fsleyes render --outfile test.png --size 800 600 --scene ortho \
    -xh -yh --voxelLoc 105 141 176 --hideCursor --hideLabels \
    t1.nii.gz -ot volume \
    thomasfull_L.nii.gz -ot label -l freesurfercolorlut -o thomasfull_R.nii.gz -ot label -l freesurfercolorlut -o