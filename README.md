# README

- Mount external drive with `sudo mount -t drvfs F: /mnt/f` 
- Shared drive
    - smb://umwssnas01.umassmed.edu/MS-neuroimaging$
    - \\umwssnas01\MS-neuroimaging$


Monai [Installation Guide](https://docs.monai.io/en/stable/installation.html). 

## Hemond Data

### Preproc

- In `hemond_data.py` in `HaemondData.find_scan`, consider raising a Warning instead of an Exception if a scan is not found for a subid/ses. This will make sense when the program is more complete and things are ready to run

- Issue is that hemond data have slightly different shape in one axis where as the data going into the monai network are all uniform in shape. Need to crop data
- Also need to modify the network to not expect four dimensional stacked images


## Brats Data

- [MONAI Tutorials](https://github.com/Project-MONAI/tutorials)

- [The Medical Segmentation Decathlon](https://www.nature.com/articles/s41467-022-30695-9)

## 3D Autoseg

[Source code](https://docs.monai.io/en/1.2.0/_modules/monai/apps/auto3dseg/auto_runner.html)

[SwinUNETR](https://docs.monai.io/en/1.3.0/_modules/monai/networks/nets/swin_unetr.html)

- Uses soft dice loss function

### Training the network

- I think the Buffalo people are only using the set of slices that include the choroid plexus
- They used the [auto3dseg_hello_world](https://github.com/Project-MONAI/tutorials/blob/main/auto3dseg/notebooks/auto3dseg_hello_world.ipynb) example

- On lenovo_desktop, getting ZeroDivisionError during training ([see output](logs/ZeroDivisionError.txt))
    - SwinUNETR uses soft dice loss function

- Hemondlab computer GPU running out of memory when trying to train. Tries to allocate 1.14 gb then fails. Checking with nvidia-smi shows that when this happens, the gpu usage reaches ~11000MiB / 12288MiB
    - [Question on pytorch forum](https://discuss.pytorch.org/t/how-to-prevent-cuda-out-of-memory-error-for-a-large-monai-network-swinunetr-with-large-patch-size-images/179639)

## Notes

### Segmenting CSF/lymph channels

Can use cluster to segment continuous regions of a particular intensity and then pull out ROI's like the dorsal and ventral sinuses

- `cluster -i T:\brain\lesjak_2017\data\patient01\proc\patient01_FLAIR.csf.1.nii.gz -t 30`
- `fslmaths patient01_FLAIR.csf.1.clustered.nii.gz -thr 2080.5 -bin patient01_FLAIR.csf.1.clusteredLarge.nii.gz`

Preprocessing steps

1. Intensity normalize across subjects and/or within subjects
2. 

multis (don't know what this is referring to)

### Meeting with Buffalo people

- I think they're only using the set of slices that include choroid plexus


## Conferences

- ACTRIMS - Oct 25 deadline
- AAN april deadline