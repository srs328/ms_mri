# Plan

## Hemond Data

### Preproc

- In `hemond_data.py` in `HaemondData.find_scan`, consider raising a Warning instead of an Exception if a scan is not found for a subid/ses. This will make sense when the program is more complete and things are ready to run

- Issue is that hemond data have slightly different shape in one axis where as the data going into the monai network are all uniform in shape. Need to crop data
- Also need to modify the network to not expect four dimensional stacked images

Right now the `Scan` class has the method `get_subj_ses` with a regex pattern hard coded in, so it only works for scans with the format: `sub-{subid}_ses-{sesid}`. Instead I could make the regex id be an argument for the class.

#### Messed up scans

1030, 1053, 1063

## Auto3dseg

[Documentation](https://github.com/Project-MONAI/tutorials/tree/main/auto3dseg)

Analyzes data to generate networks from algorithm templates, then trains the models. The validation accuracy of the models is ranked to create an ensemble prediction. There are different levels of customization, with the easiest being plug and play using `AutoRunner`. The customizable steps are:

1. Data analyzer
2. Algorithm generation
3. Model training, validation, and inference
4. Hyper-parameter optimization
5. Model ensemble

### Training the network

- Buffalo group used the [auto3dseg_hello_world](https://github.com/Project-MONAI/tutorials/blob/main/auto3dseg/notebooks/auto3dseg_hello_world.ipynb) example

- I had forgotten to binarize the labels, and fixing this solved the ZeroDivisionErroir
- Hemondlab computer GPU running out of memory when trying to train. Tries to allocate 1.14 gb then fails. Checking with nvidia-smi shows that when this happens, the gpu usage reaches ~11000MiB / 12288MiB
  - [ ] Check if this resolves when I train with binarized labels
  
Trained model for first time. Training set had 100 scans, and there were 4 folds with max 10 epochs per fold. The work dir was `cp_work_dir21`

How does the training work with folds? Is the network trained from scratch at each fold?

## Pipeline

Goal is to be able to do something like: ...

1. CLI: modalities, ...
2. fslmerge if a stack of given modalities doesn't exist

## Issues

- Use `fslmerge` instead of worrying about the things below
- To stack the scans, I convert an nibabel image to a numpy array then stack. To resave as Nifi, I need to convert that image stack back to Nifti format and save. An nibabel image object has a header, affine, and dataobj attributes. I need to provide a value for affine when converting the stacked numpy array to nibabel image (or not? it's an optional parameter so maybe it doesn't matter). In the Lesjak data, the affine values are different for each scan of a subject. If this is the case for the Hemond data, I'll have to think about what to do.
  - They're similar enough in the Lesjak data that I could just pick any one. But I should look into the significance of the affine in case it's important and very sensitive to differences
- In the Lesjak data, the shapes of each nifti image within a subject are different. If this is the case with the Hemond data, I'll have to think about how to stack them.

## Ideas

>cortical lesions and paramagnetic rim lesions (PRL) would be AWESOME to train as well.  I have a huge set of manually-labeled PRL lesions, which would require FLAIR and a susceptibility-weighted sequence, and probably benefit from T1 as well.  Cortical lesions need T1 and FLAIR, right now I am segmenting them using Z-score combinations. Our clinical MRI scanner includes 6 modalities of potential interest: T1 (3D), FLAIR (3D), SWI (3D), Diffusion (3D), T2 (2D), +/- post-gadolinium T1SE (3D).

## Brats Data

- [MONAI Tutorials](https://github.com/Project-MONAI/tutorials)

- [The Medical Segmentation Decathlon](https://www.nature.com/articles/s41467-022-30695-9)
