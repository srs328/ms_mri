library(lme4)
library(dplyr)
library(ggplot2)
require(stats); require(graphics)
require(nlme)
require(pracma)

check =Loblolly

fm1 <- nlme(height ~ SSasymp(age, Asym, R0, lrc),
            data = Loblolly,
            fixed = Asym + R0 + lrc ~ 1,
            random = Asym ~ 1,
            start = c(Asym = 103, R0 = -8.5, lrc = -3.3))
summary(fm1)


setwd("C:/Users/srs-9/Dev/ms_mri/analysis/thalamus")
df = read.csv("melted_data_for_R_NIND_z.csv")
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

model <- lmer(value ~ choroid_dist + age + Female + scale(THALAMUS_1) +
                (choroid_dist | subid) + (choroid_dist | variable), data = df)

summary(model)
confint(model)


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

