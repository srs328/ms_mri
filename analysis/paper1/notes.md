# Notes

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
- [ ] Get the difference between T1 and FLAIR segmentations
- [ ] Coregister all the subjects, see where those differences are
  - [ ] Produce a heatmap with FreeSurfer

## Questions

- EDSS "." issue
- What mediation analysis results to trust?

## Stats Questions

- If a ttest is essentially the same as a linear regression with one categorical predictor, why is it okay to have non-normal predictors in regressions?
- Ask about mediation analysis on CrossValidated
