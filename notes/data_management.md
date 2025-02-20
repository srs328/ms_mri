# Data Management

- For WSL, mount external drive with `sudo mount -t drvfs F: /mnt/f`
- Shared drive
  - `smb://umwssnas01.umassmed.edu/MS-neuroimaging$`
  - `\\umwssnas01\MS-neuroimaging$`

- Sync command for WD_Black_5TB to smbShare:
  - `rsync --ignore-existing --progress -r
    /media/WD_BLACK_DATA/3Tpioneer_bids /media/smbshare`
  - `rsync --ignore-existing --progress -r
    /media/smbshare/3Tpioneer_bids /media/WD_BLACK_DATA/`
  - `rsync --ignore-existing --progress -r
    /media/smbshare/3Tpioneer_bids_predictions /media/WD_BLACK_DATA/`
  - `rsync --ignore-existing --progress -r
    /media/WD_BLACK_DATA/3Tpioneer_bids_predictions /media/smbshare/`

- Sync command for WD_Black_5TB to smbShare (alternative location):
  - `rsync --ignore-existing --progress -r
    /media/hemondlab/Data/3Tpioneer_bids /media/smbshare`
  - `rsync --ignore-existing --progress -r
    /media/smbshare/3Tpioneer_bids /media/hemondlab/Data/`
  - `rsync --ignore-existing --progress -r
    /media/smbshare/3Tpioneer_bids_predictions /media/hemondlab/Data/`
  - `rsync --ignore-existing --progress -r
    /media/hemondlab/Data/3Tpioneer_bids_predictions /media/smbshare/`

- Copying data between Windows drives
  - `robocopy H:\3Tpioneer_bids_predictions\ \
    G:\Data\3Tpioneer_bids_predictions\ /E /xo /xn`
  - `robocopy G:\Data\3Tpioneer_bids_predictions\ H:\3Tpioneer_bids_predictions\ /E /xo /xn`
  - `robocopy H:\3Tpioneer_bids\ G:\Data\3Tpioneer_bids\ /E /xo /xn`
