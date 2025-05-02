#!/bin/bash

z=$1
savepath=$2

export FS_FREESURFERENV_NO_OUTPUT=true
export FREESURFER_HOME=$HOME/freesurfer
source $FREESURFER_HOME/SetUpFreeSurfer.sh

t1="/media/smbshare/srs-9/thalamus_project/data/sub1001-20170215/t1.nii.gz"
overlay=/media/smbshare/srs-9/thalamus_project/data/sub1001-20170215/hipsthomas-edss_betamap.nii.gz

freeview -v $t1 -v $overlay:colormap=heat:heatscale=0,-0.15,-0.31 \
    -colorscale -slice 181 168 $z \
    --viewport axial --layout 1 --viewsize 1920 1080 \
    --ss $savepath