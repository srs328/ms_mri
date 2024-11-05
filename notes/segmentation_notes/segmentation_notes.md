# Segmentation Notes

## Choroid Plexus

### Choroid 1

- 30 in training data
- Input 2 channels (t1, flair)

- sub-ms1003 may be under-labeled
- sub-ms1007 missing a sliver?

### Choroid Resegment

## Pituitary

- sub-ms1005 has discontinuities in a slice (e.g. coronal)

## Pineal

- ms1010 good besides extraneous region
- ms1029 got the pineal, but got large extraneous region too
- ms1188 got pineal but underlabeled

## Inference Notes

### choroid_resegment2

#### sub-ms1001
`itksnap -g $dataroot/sub-ms1001/ses-20170215/flair.nii.gz -o $dataroot/sub-ms1001/ses-20170215/t1.nii.gz -s $inference_root/sub-ms1001/ses-20170215/flair.t1_choroid_resegment2_pred.nii.gz`

Good

#### sub-ms1002
`itksnap -g $dataroot/sub-ms1002/ses-20200521/flair.nii.gz -o $dataroot/sub-ms1002/ses-20200521/t1.nii.gz -s $inference_root/sub-ms1002/ses-20200521/flair.t1_choroid_resegment2_pred.nii.gz`

#### sub-ms1003
`itksnap -g $dataroot/sub-ms1003/ses-20170329/flair.nii.gz -o $dataroot/sub-ms1003/ses-20170329/t1.nii.gz -s $inference_root/sub-ms1003/ses-20170329/flair.t1_choroid_resegment2_pred.nii.gz`

Giant choroid. Not well labeled



---
### sub-ms1038

- No pineal
- Very scant choroid label, but scan is low quality, abnormal looking
- Pituitary over labeled

### sub-ms1071

- Got pituitary
- No pineal
