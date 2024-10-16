# README

Monai [Installation Guide](https://docs.monai.io/en/stable/installation.html).

See [this doc](notes/training_cli.md) for notes about the training command line interface

## Reference

- For WSL, mount external drive with `sudo mount -t drvfs F: /mnt/f`
- Shared drive
  - smb://umwssnas01.umassmed.edu/MS-neuroimaging$
  - \\umwssnas01\MS-neuroimaging$
- Sync command for WD_Black_5TB to smbShare:
  - `rsync --ignore-existing --progress -r /media/hemondlab/Data/3Tpioneer_bids /media/smbshare`

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

Running `run_inference_` giving the error: `No such file or directory: '/home/srs-9/Projects/ms_mri/training_work_dirs/pineal1/swinunetr_0/model_fold0/progress.yaml'. I think I fixed the paths everywhere I could, so it's possible that monai sets the path of the training_work_dir somewhere in one of its own config files.

- Until I can figure that out, I created symlinks to match the paths where training was done

### Old

- sub-ms1196 t1 is bad
- Check the processed versions of some scans, which are messed up
  