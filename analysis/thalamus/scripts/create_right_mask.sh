#!/bin/bash

image=$1
halfx=$2
out=$3

fslmaths "$image" -roi 0 "$halfx" 0 -1 0 -1 0 -1 "$out"