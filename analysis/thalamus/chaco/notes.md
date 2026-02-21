# Notes

In each data directory, niftis will be in subject specific folders named with the convention: `subXXXX-YYYYMMDD` where XXXX refers to the 4 digit subjectID (subid or sub), and YYYYMMDD is the session ID (sesid or ses). I'll refer to the whole string `subXXXX-YYYYMMDD` as scan ID or scan henceforth. The subid and sesid for scan ID can be loaded from the csv file at `/home/srs-9/Projects/ms_mri/analysis/thalamus/data0/subject-sessions.csv`, which is organized into two columns, first one is `sub`, second one is `ses`.

The first data folder is located at `/mnt/h/srs-9/thalamus_project/data`. In Python code I always assign this path to the variable `dataroot`, and I like it to be a pathlib Path object. So to be clear, that dataroot folder will have a subfolder for every scan ID with the name `subXXXX-YYYYMMDD`. In general, things inside dataroot should not be modified except certain circumstances I'll mention below; essentially, treat it as read only unless a file we expect to be there isn't, then it will be created (as described further below). The files of interest within each scan's folder in dataroot are:

- Raw T1: `t1.nii.gz`
- HIPS-THOMAS segmentation mask: `thomasfull.nii.gz`
- Lesion segmentation mask: `lst-ai/space-flair_desc-annotated_seg-lst.nii.gz`

In many scan's folders, `thomasfull.nii.gz` probably won't exist and will need to be created. So if it doesn't exist, it will be created with the following command: `fslmaths thomasfull_L.nii.gz -add thomasfull_R.nii.gz thomasfull.nii.gz`. This command could be called directly from Python using `subprocess`, or it could be incorporated into a bash script, depending on how you decide to structure this whole pipeline. If that command fails it's probably because HIPS-THOMAS was never run for the scan, but the reason doesn't matter. If the command to create `thomasfull.nii.gz` fails, just log that it failed for scan ID and add the scan ID to a running list of scans that were skipped and move to the next scan

If the folder `lst-ai` does not exist for a particular scan, then just skip the scan. Log that `lst-ai` does not exist for the scan ID and add the scan ID to the same running list of scans that were skipped.

The main working folder for writing pipeline outputs will be `/mnt/h/srs-9/chaco`. We can assign this path to a variable called `work_dir` which should be a pathlib Path object. A folder for a scan ID will need to be created if it does not already exist while looping through the scans.

For each scan, the raw T1 image in dataroot will need to be nonlinearly registered to the MNI template using `antsRegistrationSyNQuick.sh`. The MNI template path is `/mnt/h/srs-9/chaco/MNI152_T1_1mm_brain.nii.gz`. The structure of registration command should look something like:

```bash
antsRegistrationSyNQuick.sh -d 3 -t s \
    -f /path/to/mni \
    -m /path/to/t1.nii.gz \
    -o "t1_mni"
```

That command should be run in such a way that all of its output is saved into the scan's folder in `work_dir` (i.e. `/mnt/h/srs-9/chaco/subXXXX-YYYYMMDD`). That might mean running the command from within that folder, unless there's another way like prepending that path to the `-o` option.

After that, the transform needs to be applied to the HIPS-THOMAS segmentation and the lesion segmentation mask. That command will look like

```bash
antsApplyTransforms -d 3 -i /path/to/<input>.nii.gz \
    -r /path/to/mni \
    -o /path/to/<input>_mni.nii.gz \
    -t t1_mni1Warp.nii.gz \
    -t t1_mni0GenericAffine.mat \
    -n NearestNeighbor
```

The registered thomasfull file will end up being `/mnt/h/srs-9/chaco/subXXXX-YYYYMMDD/thomasfull_mni.nii.gz`, and the lesion mask will be called `/mnt/h/srs-9/chaco/subXXXX-YYYYMMDD/space-flair_desc-annotated_seg-lst_mni.nii.gz`. The last step is to make some final adjustments to those files. For thomasfull_mni, do the following:

```bash
fslmaths /path/to/thomasfull_mni.nii.gz -uthr 12 -thr 4 -sub 2 -thr 0 /path/to/thomas_thalamus.nii.gz
fslmaths /path/to/thomasfull_mni.nii.gz -uthr 2 -sub 1 -thr 0 -add /path/to/thomas_thalamus.nii.gz /path/to/thomas_thalamus.nii.gz
```

And for the lesion mask:

```bash
fslmaths /path/to/space-flair_desc-annotated_seg-lst_mni.nii.gz -bin /path/to/lesion_mask_mni.nii.gz
```

Write this as a python script.
