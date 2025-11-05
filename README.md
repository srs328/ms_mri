# README

## Analysis


Monai [Installation Guide](https://docs.monai.io/en/stable/installation.html).

See [this doc](notes/training_cli.md) for notes about the training command line interface

`requirements.txt` generated with `pipreqs . --mode no-pin`. The `--scan-notebooks`
option resulted in error related to notebook not being in JSON format correctly

## Reference

To save the monai log to a file during training, run the script like this: 

`python monai_analysis/choroid_resegment1/run_inference-choroid-10_18_24.py 2>&1 | tee -a inference.log`

### Ubuntu Desktop

- remap scroll lock to S for itksnap: `xmodmap -e "keycode 78 = s"`  
- remap home to S for itksnap: `xmodmap -e "keycode 110 = s"`
  - [Guide](https://askubuntu.com/questions/296155/how-can-i-remap-keyboard-keys)

## Issues

- Permission errors with WD Black drive, e.g. when setting the work_dir in it
- Hacky work around in utils for not recreating combined labels
- Training multi label not working
  - Double check how the monai tutorials handle multiple labels
- Figure out why I get issues with "no such file or directory:" on $PATH
  - Also why does zsh have all the windows PATH items while bash doesn't

Running `run_inference_` giving the error: `No such file or directory:
'/home/srs-9/Projects/ms_mri/training_work_dirs/pineal1/swinunetr_0/model_fold0/progress.yaml'.
I think I fixed the paths everywhere I could, so it's possible that monai sets
the path of the training_work_dir somewhere in one of its own config files.

- Until I can figure that out, I created symlinks to match the paths where training
  was done

- Everytime I run the preparation for inference, it has to go through a few bad
  scans again to realize the nifti file is screwed up. I should save a cache of
  the screwed up files so that it preemptively skips them. Then I can have a function
  to clear the cache at a later data when the files are fixed.

### Old

- sub-ms1196 t1 is bad
- Check the processed versions of some scans, which are messed up
  
  ### Research on datalist.json

- [`ensemble_builder`](https://docs.monai.io/en/1.3.0/_modules/monai/apps/auto3dseg/ensemble_builder.html)
  has class `AlgoEnsembleBuilder` which is used in my inference. That contains
  `AlgoEnsemble`, which is important. Also, a `ConfigParser` is used to parse the
  task file
  - Read about [MONAI bundle configuration](https://docs.monai.io/en/latest/config_syntax.html)

  /dev/dm-3

## Software

[Better FSL install and config guides](https://fsl.fmrib.ox.ac.uk/fsl/docs/#/)
