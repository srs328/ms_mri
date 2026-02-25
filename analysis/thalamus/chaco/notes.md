# Notes

| Region   | Label      | Region of Interest                  |
| :------- | :--------- | :---------------------------------- |
| 1 | 2-AV       | Antero-Ventral Nucleus              |
| 2 | 4-VA       | Ventral Anterior Nucleus            |
| 3 | 5-VLa      | Ventral Lateral Nucleus (anterior)  |
| 4 | 6-VLP      | Ventral Lateral Nucleus (posterior) |
| 5 | 7-VPL      | Ventral Posterior Lateral           |
| 6 | 8-Pul      | Pulvinar                            |
| 7 | 9-LGN      | Lateral Geniculate Nucleus          |
| 8 | 10-MGN     | Medial Geniculate Nucleus           |
| 9 | 11-CM      | Centromedian Nucleus                |
| 10 | 12-MD-Pf   | Mediodorsal Nucleus                 |

---

## ChaCo Batches

- `lesion_mask_mni_nemo_output_sdstreamANDifod2act_20260222_184222817`
  - Both sdstream and ifod2
  - All ref subs
  - Did not include tracts that start and end at same ROI
- `lesion_mask_mni_nemo_output_ifod2act_20260222_203419351`
  - Justifod2
  - All ref subs
  - Included tracts that start and end at same ROI
- `lesion_mask_mni_nemo_output_ifod2act_20260223_013527837`
  - Just ifod2
  - All ref subs for just 1mm res (not for thomas)
  - Thomas without pairwise 
- `lesion_batch_001_nemo_output_ifod2act_20260222_234401174.zip`
  - lesion_batch1
  - All ref subs for 1mm res only (not for thomas)
  - Thomas without pairwise option selected
- chaco1
  - Default options no parcellation

## Commands

```bash
scan_dir=/mnt/h/srs-9/chaco/sub1001-20170215
nemo_base=$scan_dir/lesion_mask_mni_nemo_output
mni=/mnt/h/srs-9/chaco/MNI152_T1_1mm_brain.nii
volumefile=$nemo_base/lesion_mask_mni_nemo_output_sdstream_chacovol_res1mm_mean.nii.gz
parcelfile=$scan_dir/thomas_thalamus.nii.gz

python nemo_save_average_glassbrain.py \
    --out $nemo_base/test.png \
    --parcellation $parcelfile \
    --binarize \
    $volumefile
```

```bash
--out /mnt/h/srs-9/chaco/sub1001-20170215/lesion_mask_mni_nemo_output/test.png --parcellation /mnt/h/srs-9/chaco/sub1001-20170215/thomas_thalamus.nii.gz /mnt/h/srs-9/chaco/sub1001-20170215/lesion_mask_mni_nemo_output/lesion_mask_mni_nemo_output_sdstream_chacovol_res1mm_mean.nii.gz

```

```bash
scan_dir=/mnt/h/srs-9/chaco/sub1001-20170215
nemo_base=$scan_dir/lesion_mask_mni_nemo_output_sdstreamANDifod2act_20260221_052753046
mni=/mnt/h/srs-9/chaco/MNI152_T1_1mm_brain.nii
volumefile=$nemo_base/lesion_mask_mni_nemo_output_ifod2act_chacovol_thomas_mean.pkl
parcelfile=$scan_dir/thomas_thalamus.nii.gz

python nemo_save_average_glassbrain.py \
    --out $nemo_base/test.png \
    --parcellation $parcelfile \
    $volumefile
```


```bash
scan_dir=/mnt/h/srs-9/chaco
nemo_base=$scan_dir/lesion_mask_mni_nemo_output_allsubs
mni=/mnt/h/srs-9/chaco/MNI152_T1_1mm_brain.nii.gz
chacofile=$nemo_base/lesion_mask_mni_nemo_output_ifod2act_chacovol_res1mm_allref.pkl
parcelfile=$scan_dir/sub1001-20170215/thomas_thalamus.nii.gz

python nemo_parcellate_results.py \
    --input  $chacofile \
    --output $nemo_base/test.npz \
    --parcelvol $parcelfile \
    --refvol $mni \
    --asum /mnt/h/chaco_batches/localnemo/nemo_Asum_endpoints.npz 
```


run with regular lst
- 1245, 1379

run lst-ai
- 2120

should be ready to add to batch
- 1357, 1112, 1529

- 1529 the thomas segmentation was screwed up
- 1112 nonlinear registration was screwed up
- 1357 the nonlinear registration was screwed up


- sub2001 does not have a 2016 flair. The old t2lv was from the 2020 scan. the edss date is 2020
- sub1394: does not have 2019 flair. old t2lv from jul 2020 session. EDSS from feb 2020
- sub1364: no 2017 flair. old t2lv from 20180618. No EDSS. Need to check when I pulled SDMT from
- sub2106: no flair 20170205, but has flair 20170813. EDSS from 20171214
- sub2120: flair from 20170920 is screwed up; has flair from 20180917; EDSS from 20180109


To do:

- [x] 1112: rerun prepare chaco data
- [x] 1357: rerun prepare_chaco_data
- [ ] 1529: fix thomas seg and rerun prepare chaco data
- [ ] 2120: switch to 20180917 scan
- [ ] 2001: switch to ses-20200512 scan: run hips-thomas, CP seg, already have lst-ai
- [ ] 1394: switch to ses-20200708
- [ ] 1364: switch to ses-20180618
- [ ] 2106: switch to ses-20170813

Other documentation to do:

- [ ] 1196: add my notes about this to a central location too


941327[24]  | short | EXIT | hipsthomas[24]   | [96.0%] of 4 | [100.0%] of 16.0G |    51:18
 * Job hit requested memory limit of 16G.
 * Consider requesting ~24G instead.
-------------------------------------------------------------------------------------------
941327[119] | short | EXIT | hipsthomas[119]  | [93.2%] of 4 | [100.0%] of 16.0G | 01:36:46
 * Job hit requested memory limit of 16G.
 * Consider requesting ~24G instead.
-------------------------------------------------------------------------------------------
941327[200] | short | EXIT | hipsthomas[200]  | [94.1%] of 4 | [100.0%] of 16.0G | 01:04:13
 * Job hit requested memory limit of 16G.
 * Consider requesting ~24G instead.