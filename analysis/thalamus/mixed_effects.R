setwd("/home/srs-9/Projects/ms_mri/analysis/thalamus")
df = read.csv("melted_data_for_R2.csv")
library("lme4")

model <- lmer(value ~ choroid_dist + age + Female + scale(tiv) + (1 | subid) + (choroid_dist | variable), data=df)
summary(model)
