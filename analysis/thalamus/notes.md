# Notes

apptainer run docker://anagrammarian/sthomas -it --rm --name sthomas -v ${PWD}:/data -w /data --user ${UID}:$(id -g) anagrammarian/sthomas hipsthomas.sh -t1 -i t1.nii.gz