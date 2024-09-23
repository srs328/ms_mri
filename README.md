# README

- For WSL, mount external drive with `sudo mount -t drvfs F: /mnt/f`
- Shared drive
  - smb://umwssnas01.umassmed.edu/MS-neuroimaging$
  - \\umwssnas01\MS-neuroimaging$

Monai [Installation Guide](https://docs.monai.io/en/stable/installation.html).

Issues

- sub-ms1196 t1 is bad
- Check the processed versions of some scans, which are messed up

- remap scroll lock to S for itksnap: `xmodmap -e "keycode 78 = s"`  
- remap home to S for itksnap: `xmodmap -e "keycode 110 = s"`
  - [Guide](https://askubuntu.com/questions/296155/how-can-i-remap-keyboard-keys)
