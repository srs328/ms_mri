# from https://rpubs.com/kareena_delrosario/lavaan_intro_medsem
pkgs <- c("tidyverse", 
          "dplyr", 
          "haven", 
          "foreign", 
          "lme4", 
          "nlme", 
          "lsr", 
          "emmeans", 
          "afex", 
          "knitr", 
          "kableExtra", 
          "car",
          "mediation",
          "rockchalk",
          "multilevel",
          "bda",
          "gvlma",
          "stargazer",
          "QuantPsyc",
          "pequod",
          "MASS",
          "texreg",
          "pwr",
          "effectsize",
          "semPlot",
          "lmtest",
          "semptools",
          "conflicted",
          "nnet",
          "ordinal",
          "DescTools")


packages <- rownames(installed.packages())
p_to_install <- pkgs[!(pkgs %in% packages)]

if(length(p_to_install) > 0){
  install.packages(p_to_install)
}
lapply(pkgs, library, character.only = TRUE)


# devtools::install_github("cardiomoon/semMediation")
library(semMediation)
library(semPlot)


library(mediation)
library(lavaan)

setwd('C:/Users/srs-9/Dev/ms_mri/analysis/paper1')
cwd <- getwd()
data_dir <- file.path(cwd, "data")

df = read.csv(file.path(data_dir, "proc_ms_data_numeric.csv"))

check <- c("thoo", "thee")

# lesion vol mediating effect of choroid vol
model.Y <- lm(edss_sqrt ~ lesion_vol_logtrans + choroid_volume + Female + age + tiv, df)
summary(model.Y)

model.M <- lm(lesion_vol_logtrans ~ choroid_volume + Female + age + tiv, df)
summary(model.M)

results <- mediate(model.M, model.Y, treat='choroid_volume', 
                   mediator='lesion_vol_logtrans',
                   boot=TRUE, sims=500,
                   covariates = c("Female", "age", "tiv"),
                   outcome="edss_sqrt")
summary(results)


model <- '# direct
            edss_sqrt ~ c*choroid_volume + age + Female + tiv
          # mediator
            lesion_vol_logtrans ~ a*choroid_volume
            edss_sqrt ~ b*lesion_vol_logtrans + age + Female + tiv
          # indirect effect
            ab := a*b
          # total effect
            total := c + (a*b)
'
fit <- sem(model, data = df)
summary(fit)

semPaths(object = fit, whatLabels = "par")

mediationPlot(fit, indirect = TRUE, whatLabels = "est")

# -----------------------------------------------------------------------

# lesion vol mediating effect of PRL
model.Y <- lm(edss_sqrt ~ lesion_vol_logtrans + PRL + Female + age + tiv, df)
summary(model.Y)

model.M <- lm(lesion_vol_logtrans ~ PRL + Female + age + tiv, df)
summary(model.M)

results <- mediate(model.M, model.Y, treat='PRL', 
                   mediator='lesion_vol_logtrans',
                   boot=TRUE, sims=500)
summary(results)

# choroid volume mediating female effect
model.Y <- lm(edss_sqrt ~ Female + choroid_volume + tiv, df)
summary(model.Y)

model.M <- lm(choroid_volume ~ Female + age + tiv, df)
summary(model.M)

results <- mediate(model.M, model.Y, treat='Female', 
                   mediator='choroid_volume',
                   boot=TRUE, sims=1000)
summary(results)


# lesion_vol mediating tiv effect on cp vol
model.Y <- lm(choroid_volume ~ lesion_vol_logtrans + tiv + age + Female, df)
summary(model.Y)

model.M <- lm(lesion_vol_logtrans ~ tiv + Female + age, df)
summary(model.M)

results <- mediate(model.M, model.Y, treat='tiv', 
                   mediator='lesion_vol_logtrans',
                   boot=TRUE, sims=500)
summary(results)


# female mediating tiv effect on cp vol (sig)
model.Y <- lm(choroid_volume ~ tiv + age + Female, df)
summary(model.Y)

model.M <- lm(Female ~ tiv + age, df)
summary(model.M)

results <- mediate(model.M, model.Y, treat='tiv', 
                   mediator='Female',
                   boot=TRUE, sims=500)
summary(results)



df$dzdurC <- c(scale(df$dzdur, center=TRUE, scale=FALSE))
df$lesion_volC <- c(scale(df$lesion_vol_logtrans, center=TRUE, scale=FALSE))

model <- lm(edss_sqrt ~ lesion_volC*dzdurC + dzdurC + lesion_volC + Female + age + tiv, df)
summary(model)

library(stargazer)
stargazer(model, type="text", title = "dzdur and lesion_vol on EDSS")

library(rockchalk)
ps  <- plotSlopes(model, plotx="dzdurC", modx="lesion_volC", xlab = "dzdur", ylab = "EDSS", modxVals = "std.dev")
