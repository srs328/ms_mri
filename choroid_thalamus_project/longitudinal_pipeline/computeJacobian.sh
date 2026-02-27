#!/bin/bash

warp=$1
jacobian_svname=$2

CreateJacobianDeterminantImage 3 "$warp" "$jacobian_svname" 0 0

CreateJacobianDeterminantImage 3 sub1046_input0002-t1_brain_wmn_20220224-1InverseWarp.nii.gz sub1046_input0002-t1_brain_wmn_20220224-1InverseWarp-Jacobian00.nii.gz
CreateJacobianDeterminantImage 3 sub1046_input0002-t1_brain_wmn_20220224-1Warp.nii.gz sub1046_input0002-t1_brain_wmn_20220224-1Warp-Jacobian00.nii.gz