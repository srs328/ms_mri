# Abstract

clinical characteristics

- cysts
  - diameter?
- empty sella

## QA Assessment

15-20 subj

Look at `inspect_inference_labels.ipynb`

### Choroid

- choroid selected?
- Under/overselected?
- Extra tissue selected outside of ROI

### Pituitary

### Pineal

- pit stalk

[thoo](https://peps.python.org/pep-0289/)

## Questions

- What is vol_TIV?
- Where is the column AI for whole brain volume?
- In linear regression, can categorical data (like phenotype) be included?
- Missing data?
- Is EDSS an ordinal variable, or can we treat it as a continuous variable?
  - EDSS is sort of an ordinal variable; can it be the outcome variable for a linear regression?

## Emails

The abstract is 2500 words max so not much room for background- a sentence at most.  But attached are a few articles for some of the project motivation (have a look at the CP article from Niels and Michael at Buffalo), including one on the pineal gland hot off the press (Vukovic).  There’s a sort of crazy-sounding guy who wrote a lot about the pineal and MS back in the 90s, but I’m not so sure he’s worth reading/citing.  There’s lots that can be done in addition to volume measurements once we have good masks for these tissue targets.  In particular, we can look at calcification of these tissues susceptibility imaging, and iron accumulation as well.  I’m also attaching the brain volumetrics for these scans, in case you want to look at correlations between tissue volumes and MS lesion volumes or brain volumes.  It also occurred to me that we should probably correct (include as a covariate) for the intracranial volume when looking at the tissue volumes for CP, pineal and pituitary.  That can be found in column AI.  Alternatively, just divide every volume by the vol_TIV (column AI) and analyze as percentages.   I can review with you what all these man tomorrow, but the most important one is BPF= brain parenchymal volume.  That one does not need to be corrected for ICV.

Here’s the submission forum, due at midnight tomorrow!

https://forum.actrims.org/submit

And a quick draft you could consider working from:

Background: Multiple sclerosis is an immune-mediated neuroinflammatory disease; the etiopathogenesis of this disease remains unclear.  Circumventricular areas are fenestrated tissues at the border between brain and peripheral blood circulation and are implicated in not just neuroendocrine roles but immunomodulatory ones as well, and have been associated with both MS and MS disease severity.

Objectives: Here we aimed to create a deep learning pipeline to facilitate automated segmentation of circumventricular tissue, and relate these volumes to the clinical features of multiple sclerosis; we additionally aimed to compare these tissue volumes to other non-MS neurological conditions.

Methods: This is a retrospective case-control study of a cohort of patients with relapsing-remitting MS, non-inflammatory neurological disease (NIND), and other inflammatory neurological disease (OIND).  3*** patients were selected to create an age and sex-matched comparative groups.  Manual tissue labels were created for the pituitary, pineal, and choroid plexus based on FLAIR and T1 images. We then used these manual segmentations on multimodal (T1 and FLAIR) images from the same 3T scanner to train a Swin-UNETR deep learning algorithm. Tissue volumes were compared between groups using linear regression (*** or MANOVA) adjusted for age and sex, and compared to clinical and MRI characteristics.  Qualitative analysis of circumventricular tissue abnormalities, as well as the results of inference from the Swin-UNETR model were performed.

Results: Clinical and demographic features of the three groups were as follows:  ***.   Among the RRMS group, XX/XX had at least one abnormality of their choroid plexus, pineal, and pituitary gland, respectively.  In the NINDS group ***.   Last, in the OIND group ***.  The Using the 30 manual labels, the swin-UNETR model produced good inference results on the pituitary gland (Dice= ***), but not the choroid plexus (Dice=***) or pituitary (dice=***) Qualitative assessments of inference errors showed poor identification of the pineal gland and undersegmentation of the choroid.  We anticipate improved performance with additional training data, which we speculate is needed due to the substantial variance in tissue heterogeneity and high rate of “abnormal” features.

Conclusions: ***

Also a sort of interesting abstract re: pineal volume & MS:

https://www.neurology.org/doi/10.1212/WNL.86.16_supplement.P4.182#:~:text=Results%3A%20The%20risk%20of%20multiple,interval%2C%200.86%2D0.98).

Hi Shridhar,

Nothing special, I’d run descriptive summary measures for each cohort (RRMS; OIND, NIND) and consider looking at the (manual) pituitary, pineal, and CP volumes for each group.  It’s unlikely anything will be statistically significant (using an ANOVA or regression, adjusted for sex and age) but could still be interesting to look for effect directionality and effect sizes to estimate how many patients we would need to achieve statistical significance.  I don’t think EDSS or disease duration will be relevant, but good to report with any MS cohort.

The next part of the abstract could be a basic summary of “abnormalities” noted in each of the tissues.  For example, something like “15/30 patients had an abnormality of their pineal gland, mostly classified as a cystic inclusion.”  (or break this down by group). “Pineal clinical assessments were limited by the sequences, but 14/30 patients were noted to have a partially or fully empty sella.”  Substantial enlargement of the choroid plexus was noted in 3 patients (1 RRMS, 1 NIND, 1 OIND).  I am making these numbers up but you get the idea.  I need to finish looking at the pituitaries—will do my best to get to this later tonight.
 
The last part would be a qualitative assessment of the success of inference.  I would choose 15-20 patients randomly and record any errors that were made during inference, perhaps categorized as minor errors: overselection/underselection of tissue in the correct place, and major errors (failure to segment or inclusion of non-target tissue).  Then we can speculate that additional training is needed due to the high levels of abnormalites noted in these organs causing a lot of variance.  Or something like that.

 