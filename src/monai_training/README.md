# README

## Training

```shell
monai-training prepare-data -i "/media/hemondlab/Data1/3Tpioneer_bids" -m flair -l pineal_SRS -f first_ses
monai-training train -i "/mnt/h/3TPioneer_bids" -o /home/srs-9/Projects/ms_mri/training_work_dirs/pineal_tmp" \
    -m flair -l pineal_SRS -f first_ses
```
