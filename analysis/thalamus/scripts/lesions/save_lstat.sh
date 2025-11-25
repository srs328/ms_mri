#!/bin/bash

t1=$1
seg=$2
out=$3

c3d "$t1" "$seg" -lstat | python3 -c "
import sys
import csv
writer = csv.writer(sys.stdout)
for line in sys.stdin:
    writer.writerow(line.split())
" > $out