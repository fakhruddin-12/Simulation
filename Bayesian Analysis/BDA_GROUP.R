# ------------------------
# extracting data into R
install.packages("readxl")
library(readxl)
#df_stop<-read_excel("sqf-2025.xlsx")
df_stop <- read_excel("/Users/didar/Documents/BDA_GROUP/Simulation/Bayesian Analysis/sqf-2025.xlsx")
df_stop
library(brms)
library(dplyr)
#options(mc.cores=parllel::detectCores())

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

#-------------------------------
#as we are doing this for one quarter
#--------------------------------

df_stop_q1 <- df_stop_clean[df_stop_clean$MONTH2 %in% c("January","February","March"), ]

sum(df_stop_q1$SUSPECT_REPORTED_AGE<=5)

df_stop_q1<-df_stop_q1[df_stop_q1$SUSPECT_REPORTED_AGE>=5,]

df_stop_q1

#-------------------------------------
#add bucket to some of covariates
#----------------------------------

# age ---------------------

df_stop_q1 <- df_stop_q1 %>%
  mutate(
    AGE_GROUP = case_when(
      SUSPECT_REPORTED_AGE <= 24 ~ "Young",
      SUSPECT_REPORTED_AGE >= 25 & SUSPECT_REPORTED_AGE <= 59 ~ "Adult",
      SUSPECT_REPORTED_AGE >= 60 ~ "Old"
    )
  )
table(df_stop_q1$AGE_GROUP)

df_stop_q1$AGE_GROUP<-as.factor(df_stop_q1$AGE_GROUP)

#---------------------------
# time of day
#--------------------------



model_1 <- brm(
  SUSPECT_ARRESTED_FLAG ~ SUSPECT_RACE_DESCRIPTION+
  SUSPECT_SEX + STOP_DURATION_MINUTES+AGE_GROUP ,
  data = df_stop_q1,
  family = bernoulli(),
  chains = 1,
  iter = 4000,
  warmup = 2000,
  seed = 123,
  refresh = 0
)

summary(model_1)
exp(0.01)


