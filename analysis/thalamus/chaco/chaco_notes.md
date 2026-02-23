# Notes

The top level contents of their S3 bucket:

```bash
$ aws s3 ls s3://kuceyeski-wcm-nemodata/ --request-payer requester
                           PRE chunkfiles/
                           PRE chunkfiles_sdstream/
                           PRE nemo_atlases/
2025-01-27 19:32:01     329076 AAL116_MNI152_1mm_182x218x182.nii.gz
2025-01-27 19:31:53   10963667 MNI152_T1_1mm.nii.gz
2025-01-27 19:31:57    3219212 MNI152_T1_1mm_brain.nii.gz
2025-01-27 19:32:01      67270 MNI152_T1_1mm_brain_mask.nii.gz
2025-01-27 19:31:57    2668958 chacomean.nii.gz
2025-01-27 19:31:52   28884256 chacomean.npy
2025-01-27 19:30:01 2706184241 chacomean_per_patient.npz
2025-01-27 19:30:54 2255727329 fs86_allsubj.npz
2025-01-27 19:32:00     620838 fs86_allsubj_mode.nii.gz
2025-01-27 19:32:01     265937 fs86_allsubj_mode_dil1.nii.gz
2025-01-27 19:32:01     252184 fs86_allsubj_mode_dil2.nii.gz
2025-01-27 19:32:01     254587 fs86_allsubj_mode_dil3.nii.gz
2025-09-04 21:17:29  698728448 nemo_2.1.5_py313.sif
2025-01-27 19:31:59    1260224 nemo_Asum.nii.gz
2025-01-27 19:28:40 2899227785 nemo_Asum.npz
2025-01-27 19:32:00     708022 nemo_Asum_cumulative.nii.gz
2025-01-27 19:31:19 1147339349 nemo_Asum_cumulative.npz
2025-01-27 19:31:56    3778402 nemo_Asum_endpoints.nii.gz
2025-01-27 19:31:37 1147339349 nemo_Asum_endpoints.npz
2025-01-27 19:31:57    2586948 nemo_Asum_endpoints_binmean.nii.gz
2025-01-27 19:31:58    1305723 nemo_Asum_weighted.nii.gz
2025-01-27 19:29:36 2899227785 nemo_Asum_weighted.npz
2025-01-27 19:31:59     729903 nemo_Asum_weighted_cumulative.nii.gz
2025-01-27 19:31:38 1147339349 nemo_Asum_weighted_cumulative.npz
2025-01-27 19:31:59    1057158 nemo_Asum_weighted_endpoints.nii.gz
2025-01-27 19:31:39 1147339249 nemo_Asum_weighted_endpoints.npz
2025-01-27 19:31:54    5747882 nemo_Asum_weighted_endpoints_mean.nii.gz
2025-01-27 19:31:54    5626851 nemo_Asum_weighted_endpoints_stdev.nii.gz
2025-01-27 19:31:47   94087612 nemo_chunklist.npz
2025-01-27 18:16:52 16800000128 nemo_endpoints.npy
2025-01-27 19:31:57    2121168 nemo_endpoints_allsubj_sum.nii.gz
2025-01-27 19:31:39  717090296 nemo_endpoints_mask.npz
2025-01-27 19:31:01 2100000128 nemo_endpoints_mask_fs87bs_dil3.npy
2025-01-27 18:21:54 8400000128 nemo_meanFA.npy
2025-01-27 19:32:01       1320 nemo_parcellate_results.py
2025-01-27 19:31:58    1327319 nemo_sdstream_Asum.nii.gz
2025-01-27 19:28:40 4884788901 nemo_sdstream_Asum.npz
2025-01-27 19:32:00     707120 nemo_sdstream_Asum_cumulative.nii.gz
2025-01-27 19:30:03 2283518297 nemo_sdstream_Asum_cumulative.npz
2025-01-27 19:31:55    5249661 nemo_sdstream_Asum_endpoints.nii.gz
2025-01-27 19:30:15 2283518297 nemo_sdstream_Asum_endpoints.npz
2025-01-27 19:31:56    3692557 nemo_sdstream_Asum_endpoints_binmean.nii.gz
2025-01-27 19:31:58    1615288 nemo_sdstream_Asum_weighted.nii.gz
2025-01-27 19:28:40 4884788901 nemo_sdstream_Asum_weighted.npz
2025-01-27 19:31:59     826710 nemo_sdstream_Asum_weighted_cumulative.nii.gz
2025-01-27 19:30:17 2283518297 nemo_sdstream_Asum_weighted_cumulative.npz
2025-01-27 19:31:58    1500609 nemo_sdstream_Asum_weighted_endpoints.nii.gz
2025-01-27 19:30:33 2283518297 nemo_sdstream_Asum_weighted_endpoints.npz
2025-01-27 19:31:49   94084152 nemo_sdstream_chunklist.npz
2025-01-27 18:18:38 16800000128 nemo_sdstream_endpoints.npy
2025-01-27 19:31:03 1427199991 nemo_sdstream_endpoints_mask.npz
2025-01-27 19:31:01 2100000128 nemo_sdstream_endpoints_mask_fs87bs_dil3.npy
2025-01-27 18:22:29 8400000128 nemo_sdstream_meanFA.npy
2025-01-27 18:23:01 8400000128 nemo_sdstream_meanMyl.npy
2025-01-27 18:23:38 8400000128 nemo_sdstream_siftweights.npy
2025-01-27 19:28:40 4200000128 nemo_sdstream_tracklengths.npy
2025-01-27 18:24:11 8400000128 nemo_siftweights.npy
2025-01-27 19:28:40 4200000128 nemo_tracklengths.npy
2025-01-27 19:32:02        799 save_nemomean.py
2025-01-27 19:32:01       2940 subjects_unrelated420_scfc.txt
```

## Submitting the job through the GUI

A single job with the following inputs:

- Lesion mask: `lesion_mask_mni.nii.gz`
- Custom parcellation: `thomas_thalamus.nii.gz` which has 10 unique label indices 1-10

Full details of my input parameters are in the file `lesion_mask_mni_nemo_output_ifod2act_20260222_203419351_config.json`, which was created by nemo and included in their outputs.

## Outputs

The following outputs are returned regardless of whether a parcellation is provided or the option to output for each reference subject is selected. If my understanding is correct, these are the voxel wise chaco ratios averaged across reference subjects, which would mean (number of tracts transected by a lesion)/(total number of tracts) for tracts that have an endpoint at that voxel

- `lesion_mask_mni_nemo_output_ifod2act_chacovol_res1mm_mean.nii.gz` ndarray shape (182,218,182)
- `lesion_mask_mni_nemo_output_ifod2act_chacovol_res1mm_stdev.nii.gz` ndarray shape (182,218,182)

The following outputs are returned if a parcellation is provided and regardless of whether the option to output ChaCo for each ref subject is selected. I do not know how these are computed which is essentially the crux of this endeavor to understand their code. I'll add more on this in the section "how to copmute ROI based chaco ratios"

- `lesion_mask_mni_nemo_output_ifod2act_chacovol_thomas_thalamus_mean.pkl` ndarray shape (1,10)
- `lesion_mask_mni_nemo_output_ifod2act_chacovol_thomas_thalamus_stdev.pkl` ndarray shape (1,10)
- `lesion_mask_mni_nemo_output_ifod2act_chacoconn_thomas_thalamus_mean.pkl` csr_matrix shape (10,10)
- `lesion_mask_mni_nemo_output_ifod2act_chacoconn_thomas_thalamus_stdev.pkl` csr_matrix shape (10,10)

The following outputs are only returned if the option to ouput ChaCo for each reference subject is selected.

- `lesion_mask_mni_nemo_output_ifod2act_chacovol_res1mm_allref.pkl`: csr_matrix shape (420, 7221032)
- `lesion_mask_mni_nemo_output_ifod2act_chacovol_res1mm_allref_denom.pkl` csr_matrix shape (420, 7221032)
- `lesion_mask_mni_nemo_output_ifod2act_chacovol_thomas_thalamus_allref.pkl`: ndarcsr_matrixray shape (420, 10)
- `lesion_mask_mni_nemo_output_ifod2act_chacovol_thomas_thalamus_allref_denom.pkl` csr_matrix shape (420, 10)
- `lesion_mask_mni_nemo_output_ifod2act_chacoconn_thomas_thalamus_allref.pkl`: 420 element list of csr_matrix with shape (10,10)
- `lesion_mask_mni_nemo_output_ifod2act_chacoconn_thomas_thalamus_allref_denom.pkl` 420 element list of csr_matrix with shape (10,10)

## How to compute ROI based chaco ratios

My naive instinct was that I could load `lesion_mask_mni_nemo_output_ifod2act_chacovol_res1mm_mean.gz`, and then average the voxels that fall within one of the ROIs. This way I end up with 10 averages. However, these differed significantly from what was contained in `lesion_mask_mni_nemo_output_ifod2act_chacovol_thomas_thalamus_mean.pkl`. Just to give a sense, I provide the values below:

```output
# from the pkl file provided by nemo
[0.040872424840927124, 0.030032090842723846, 0.010976091958582401, 0.019914278760552406, 0.027912579476833344, 0.05090194568037987, 0.029394857585430145, 0.03634316474199295, 0.022196678444743156, 0.03861214593052864]

# the averages I computed by looking at the nifti and averaging in ROI's
[0.056728043221417314, 0.07048230594109417, 0.04970836273381652, 0.05833122023618951, 0.03717169936724419, 0.06497520823226782, 0.009711612824216181, 0.04217460730063749, 0.05985130600734626, 0.07280325995909334]
```

