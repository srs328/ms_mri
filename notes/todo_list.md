# To Do List

## Important

- [ ] Make it so that the training script/notebook automatically makes a copy of `datalist.json` called `training-datalist.json`

## Segmentation

- [ ] Look into deepedit
- [ ] Try the CP segmentation approach described in Bergsland et. al to compare to the Monai results

## Project Structure

- [ ] Rename the notebooks in `/notebooks` to not have "notebook" in the name, but have an expressive title

## itksnap

- [ ] Complete/refine `itksnap_workspaces/create_manual_labels_workspaces.ipynb`

## File Management

- [ ] Make a leaner library for dealing with MRI data and paths (without monai and all that)
- [ ] Would it make sense to subclass Path for working with nifti files, then override methods/properties like
  `stem`, `with_stem`, `with_name`, etc so that they handle `.nii.gz`?
- [ ] Inferred labels should be named in such a way that indicates which training
  they were produced from
- [ ] The new Scan class should have a function that returns all niftis in
  its root folder
- [ ] The new Scan class should have a function that returns all subdirectories
  in its root folder
- [ ] Rename all the inferred labels with something more descriptive of which training
  they were produced from (e.g. t1_pituitary_pred → t1_pituitary1_pred)
- [ ] The trainings for pituitary1 and choroid1 were via the old notebook. Convert exactly what
  was done into a command with associated datalist and dataset
- [ ] Fix `find_labels()` so that it actually gets labels with initials
  - It worked on pineal but not choroid. Maybe it's because pineal didn't have labels without initials,
    whereas for choroid, it defaulted to one w/o initials since it was available
- [x] Make a function and format saved datasets/datalist to be more easily usable
  across devices where the paths are different

## Training

- [ ] Train choroid segmentation with the actual fixed segmentation (screwed it up the first time, didn't collect right labels)
- [ ] Fix the training code so that the ensemble_predict files have the same name format as the inference ones
- [ ] In evaluate training, fix the spots that are hard coded
- [ ] Figure out why `ensemble_out_dir` for old trainings has a subdirectory `3Tpioneer_bids`, but new ones don't
- [ ] View [YouTube tutorial](https://www.youtube.com/watch?v=wEfLVnL-7D4) for auto3dseg

## Logging

- [ ] See if I can capture Monai logs using `| tee`. Might need to do something extra
  to capture stderr ([look here](https://serverfault.com/questions/201061/capturing-stderr-and-stdout-to-file-using-tee))

## Code Style

- [ ] Find any instance where I use a list comprehension as a function argument
  or in constructer and change to generator expression (see [PEP 289](https://peps.python.org/pep-0289/))


brain and lesion vol cubic and prl, thalamus, cortical thickness, 