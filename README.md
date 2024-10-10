# README

Monai [Installation Guide](https://docs.monai.io/en/stable/installation.html).

See [this doc](notes/training_cli.md) for notes about the training command line interface

## Reference

- For WSL, mount external drive with `sudo mount -t drvfs F: /mnt/f`
- Shared drive
  - smb://umwssnas01.umassmed.edu/MS-neuroimaging$
  - \\umwssnas01\MS-neuroimaging$

### Ubuntu Desktop

- remap scroll lock to S for itksnap: `xmodmap -e "keycode 78 = s"`  
- remap home to S for itksnap: `xmodmap -e "keycode 110 = s"`
  - [Guide](https://askubuntu.com/questions/296155/how-can-i-remap-keyboard-keys)

## Issues

### Old

- sub-ms1196 t1 is bad
- Check the processed versions of some scans, which are messed up
  