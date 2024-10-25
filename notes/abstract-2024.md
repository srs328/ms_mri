# Abstract

Background: 
Multiple sclerosis is an immune-mediated neuroinflammatory disease; the 
etiopathogenesis of this disease remains unclear.  Circumventricular 
areas are fenestrated tissues at the border between brain and peripheral
 blood circulation and are implicated in not just neuroendocrine roles 
but immunomodulatory ones as well, and have been associated with both MS
 and MS disease severity.

Objectives:
 Here we aimed to create a deep learning pipeline to facilitate 
automated segmentation of circumventricular tissue, and relate these 
volumes to the clinical features of multiple sclerosis; we additionally 
aimed to compare these tissue volumes to other non-MS neurological 
conditions.

Methods:
 This is a retrospective case-control study of a cohort of patients with
 relapsing-remitting MS, non-inflammatory neurological disease (NIND), 
and other inflammatory neurological disease (OIND).  3*** patients were 
selected to create an age and sex-matched comparative groups.  Manual 
tissue labels were created for the pituitary, pineal, and choroid plexus
 based on FLAIR and T1 images. We then used these manual segmentations 
on multimodal (T1 and FLAIR) images from the same 3T scanner to train a 
Swin-UNETR deep learning algorithm. Tissue volumes were compared between
 groups using linear regression (*** or MANOVA) adjusted for age and 
sex, and compared to clinical and MRI characteristics.  Qualitative 
analysis of circumventricular tissue abnormalities, as well as the 
results of inference from the Swin-UNETR model were performed.

Results:
 Clinical and demographic features of the three groups were as follows: 
 ***.   Among the RRMS group, XX/XX had at least one abnormality of 
their choroid plexus, pineal, and pituitary gland, respectively.  In the
 NINDS group ***.   Last, in the OIND group ***.  The Using the 30 
manual labels, the swin-UNETR model produced good inference results on 
the pituitary gland (Dice= ***), but not the choroid plexus (Dice=***) 
or pituitary (dice=***) Qualitative assessments of inference errors 
showed poor identification of the pineal gland and undersegmentation of 
the choroid.  We anticipate improved performance with additional 
training data, which we speculate is needed due to the substantial 
variance in tissue heterogeneity and high rate of “abnormal” features.

Conclusions: ***
