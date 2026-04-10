# ------------------------
# extracting data into R
install.packages("readxl")
library(readxl)
df_stop<-read_excel("sqf-2025.xlsx")
df_stop
library(brms)
library(dplyr)
options(mc.cores=parllel::detectCores())

df_stop[df_stop == "(null)"] <- NA
df_stop_clean <- df_stop[
  complete.cases(
    df_stop[, c("SUSPECT_REPORTED_AGE",
                "SUSPECT_ARRESTED_FLAG",
                "STOP_FRISK_TIME",
                "SUSPECT_SEX",
                "SUSPECT_HEIGHT",
                "SUSPECT_WEIGHT",
                "SUSPECT_BODY_BUILD_TYPE",
                "STOP_LOCATION_BORO_NAME")]
  ),
]

df_stop_clean


df_stop_q1 <- df_stop_clean[df_stop_clean$MONTH2 %in% c("January","February","March"), ]

df_stop_q1


model_1 <- brm(
  SUSPECT_ARRESTED_FLAG ~ SUSPECT_RACE_DESCRIPTION+
    SUSPECT_SEX ,
  data = df_stop_q1,
  family = bernoulli(),
  chains = 1,
  iter = 4000,
  warmup = 2000,
  seed = 123,
  refresh = 0
)

summary(model_1)
exp(-1.20)
#--print
