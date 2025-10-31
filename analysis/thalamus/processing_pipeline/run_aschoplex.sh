#!/bin/bash

export ASCHOPLEXDIR=/home/srs-9/git-repos/aschoplex

dataroot=$1
work_dir=/mnt/h/srs-9/aschoplex/test1/work_dir

python $ASCHOPLEXDIR/launching_tool.py \
	--dataroot "$dataroot" \
	--work_dir "$work_dir" \
	--finetune no --prediction ft

