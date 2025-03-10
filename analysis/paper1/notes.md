# Notes

## Preprocessing of MRI data

All of these scans are preprocessed with bias correction and noise reduction, in addition to upscaling to a higher isotropic resolution and reslicing (with interpolation)

## Deciding which model

- Bland-Altman plots
- Note that with the flair model, use of flair_contrast
  - flair contrast is a significant covariate for predicting all volumes

## Analysis

- How do the structures' volumes correlate with eachother
- Plot EDSS against volumes
- Read [this](https://www.andrewheiss.com/blog/2022/05/20/marginalia/) in depth explanation about marginal means
- Check [this](https://www.statsmodels.org/dev/examples/notebooks/generated/plots_boxplots.html) documentation about stats models regression plots (eg partial regression plots)

It'd take too long to do an omnibus test for the mediation analysis on ordinal EDSS

## Ideas

- [ ] Pineal thing
- [ ] What happens to flair results if I adjust volumes based on proportional bias?
- [x] Could pituitary volume not be associated with MS, but it's dimensions or shape still be? Try pyradiomics on it
  - Not the case. Looks like the Eren paper did not control for TIV
  - Our pituitary volumes do correlate with phenotype and EDSS when TIV not controlled
  - Minor axis length is the radiomic feature with strongest association
- [ ] Do PRL cause faster disease progression (ie worse EDSS with less dzdur)

### Segmentation

- [ ] Resegment all the pineals. Start with my flair segmentation and erase around what I can see in T1
  - Do we train the T1 model and FLAIR model on same segmentations, or their respective segmentations? The problem with the latter is that there is then no "ground truth"
- [ ] Get the difference between T1 and FLAIR segmentations
- [ ] Coregister all the subjects, see where those differences are
  - [ ] Produce a heatmap with FreeSurfer
- [ ] Could have someone segment the ChP on \~10 CE T1 images as "gold standards" to compare the predictions to (e.g. Visani et. al 2024)
- [ ] Test retest reliability: find patients with longitudinal scans somewhat close to eachother and compare the volumes (Eisma paper picks 10 participants with scans within 2 months of another)

#### Pineal Resegmentation

New segmentation fails at 2144 and 2146. 2144 is a strange case where the pineal is a giant hole (cyst?) on T1, and the original segmentation didn't do well either, but still better

### Choroid Analysis

- Based on Fleischer et al 2021 (which looks at patients starting much earlier in their disease course), our patients choroid volumes have likely peaked
  - Their chp volume hist is positively skewed whereas ours is normal
  - Their chp volumes have a much greater correlation with edss
  - Their edss's are lower
  - Their disease duration is around 2 years. They have many patients who started getting tracked as soon as they were diagnosed
- Check choroid_analysis.ipynb moderation section for choroid_volume*leson_volume
  - Chris mentioned two types of inflammation, and ChP volume reflected one and T2LV reflected the other

## Questions

- EDSS "." issue
- What mediation analysis results to trust?

## Stats Questions

- If a ttest is essentially the same as a linear regression with one categorical predictor, why is it okay to have non-normal predictors in regressions?
- Ask about mediation analysis on CrossValidated
- Read [this](https://stats.stackexchange.com/questions/445578/how-do-dags-help-to-reduce-bias-in-causal-inference/445606#445606) for detailed intuition about causal inference, mediation, moderation
