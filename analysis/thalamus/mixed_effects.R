library(lme4)
library(dplyr)
library(ggplot2)
require(stats); require(graphics)
require(nlme)
require(pracma)


setwd("/home/srs-9/Projects/ms_mri/analysis/thalamus/R_data")
df = read.csv("melted_data_for_R_NIND_thalamus_z.csv")
model <- lmer(value ~ choroid_dist + age + Female + tiv +
                (1 | subid), data = df)
summary(model)
confint(model)


# df$dz_type3 <- factor(df$dz_type3, levels = c("NIND", "MS"))
# 
# df <- df %>%
#   group_by(dz_type3) %>%
#   mutate(choroid_dist_scaled = scale(choroid_dist)) %>%
#   ungroup()

df <- df %>%
  group_by(variable) %>%
  mutate(value_scaled = scale(value))

df <- df %>%
  group_by(variable) %>%
  mutate(choroid_dist_scaled = scale(choroid_dist))

filtered_data <- df %>%
  filter(variable == "VLP_6")
model = lm(value ~ choroid_dist + age + Female + THALAMUS_1, data=filtered_data)
summary(model)
ggplot(filtered_data, aes(x=choroid_dist, y=value)) + geom_point()




df2 = read.csv("longitudinal_for_R_MS.csv")
model <- lmer(change ~ choroid_dist + age + scale(tiv) + Female +
                (1 | subid) + (1 | struct_name), data = df2)
summary(model)


volume_change <- function(distance, a, b, c) {
  return (a * erf(b*(distance-c)) - abs(a))
}

model = nlme(change ~ volume_change(choroid_dist, a, b, c),
             data = df2,
             fixed = list(a ~ 1, b ~ 1, c ~ 1),
             groups = ~subid,
             start = c(a=0.01, b=0.35, c=12))
summary(model)

x = seq(from=0, to=22, length.out=50)
y = volume_change(x, 0.01, 0.35, 12)

filtered_data <- df2 %>%
  filter(struct_name == "Pul_8")

ggplot(filtered_data, aes(x=choroid_dist, y=change)) + geom_point()

