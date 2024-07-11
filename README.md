# README

Mount external drive with `sudo mount -t drvfs F: /mnt/f` 

Monai [Installation Guide](https://docs.monai.io/en/stable/installation.html). 

## Brats Data

- [MONAI Tutorials](https://github.com/Project-MONAI/tutorials)

- [The Medical Segmentation Decathlon](https://www.nature.com/articles/s41467-022-30695-9)

cluster -i T:\brain\lesjak_2017\data\patient01\proc\patient01_FLAIR.csf.1.nii.gz -t 30

fslmaths patient01_FLAIR.cs
f.1.clustered.nii.gz -thr 2080.5 -bin patient01_FLAIR.csf.1.clusteredLarge.nii.gz

1. Intensity normalize across subjects and within subjects
2. 

multis

ACTRIMS - Oct 25 deadline
AAN april deadline