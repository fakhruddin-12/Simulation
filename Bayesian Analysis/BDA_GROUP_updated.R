# =========================
# 1. LOAD PACKAGES + DATA
# =========================
library(readxl)
library(dplyr)
library(brms)
library(loo)

df_stop <- read_excel("sqf-2025.xlsx")


# =========================
# 2. HELPER FUNCTIONS
# =========================

# Convert height strings like "5.10" into inches
parse_height_to_inches <- function(x) {
  x <- as.character(x)
  out <- rep(NA_real_, length(x))
  
  for (i in seq_along(x)) {
    if (is.na(x[i])) next
    
    parts <- strsplit(x[i], ".", fixed = TRUE)[[1]]
    if (length(parts) != 2) next
    
    feet <- suppressWarnings(as.numeric(parts[1]))
    inches <- suppressWarnings(as.numeric(parts[2]))
    
    if (is.na(feet) || is.na(inches)) next
    if (inches < 0 || inches > 11) next
    
    out[i] <- 12 * feet + inches
  }
  
  out
}


# =========================
# 3. CLEAN CHARACTER "(null)" VALUES
# =========================
char_cols <- sapply(df_stop, is.character)

df_stop[char_cols] <- lapply(df_stop[char_cols], function(col) {
  col[col == "(null)"] <- NA
  col
})


# =========================
# 4. KEEP ONLY COLUMNS NEEDED
# =========================
df_model <- df_stop %>%
  select(
    MONTH2,
    STOP_FRISK_TIME,
    SUSPECT_ARRESTED_FLAG,
    SUSPECT_RACE_DESCRIPTION,
    SUSPECT_SEX,
    SUSPECT_REPORTED_AGE,
    SUSPECT_HEIGHT,
    SUSPECT_WEIGHT,
    STOP_LOCATION_BORO_NAME
  )


# =========================
# 5. FILTER TO Q1
# =========================
df_model <- df_model %>%
  filter(MONTH2 %in% c("January", "February", "March"))


# =========================
# 6. CREATE CLEAN MODEL VARIABLES
# =========================
df_model <- df_model %>%
  mutate(
    arrested = ifelse(SUSPECT_ARRESTED_FLAG == "Y", 1,
                      ifelse(SUSPECT_ARRESTED_FLAG == "N", 0, NA)),
    
    age = suppressWarnings(as.numeric(SUSPECT_REPORTED_AGE)),
    weight = suppressWarnings(as.numeric(SUSPECT_WEIGHT)),
    height_in = parse_height_to_inches(SUSPECT_HEIGHT),
    
    sex = factor(SUSPECT_SEX),
    race = factor(SUSPECT_RACE_DESCRIPTION),
    boro = factor(STOP_LOCATION_BORO_NAME),
    
    # extract hour from HH:MM:SS
    hour = suppressWarnings(as.integer(substr(as.character(STOP_FRISK_TIME), 1, 2))),
    
    # time buckets: 16-21, 22-02, remaining
    time_bucket = case_when(
      hour >= 16 & hour <= 21 ~ "16_21",
      hour >= 22 | hour <= 2  ~ "22_02",
      hour >= 3  & hour <= 15 ~ "remaining",
      TRUE ~ NA_character_
    ),
    
    time_bucket = factor(
      time_bucket,
      levels = c("remaining", "16_21", "22_02")
    )
  )


# =========================
# 7. REMOVE MISSING VALUES
# =========================
df_model <- df_model %>%
  filter(
    !is.na(arrested),
    !is.na(race),
    !is.na(sex),
    !is.na(age),
    !is.na(weight),
    !is.na(height_in),
    !is.na(boro),
    !is.na(time_bucket)
  )


# =========================
# 8. BASIC SANITY FILTERS
# =========================
df_model <- df_model %>%
  filter(
    age >= 10 & age <= 90,
    weight >= 60 & weight <= 400,
    height_in >= 48 & height_in <= 84
  )


# =========================
# 9. BUCKETIZATION
# =========================
df_model <- df_model %>%
  mutate(
    age_band = cut(
      age,
      breaks = c(-Inf, 17, 24, 34, 44, Inf),
      labels = c("<=17", "18-24", "25-34", "35-44", "45+"),
      include.lowest = TRUE
    ),
    
    height_band = cut(
      height_in,
      breaks = c(-Inf, 65, 68, 71, Inf),
      labels = c("<=5'5", "5'6-5'8", "5'9-5'11", "6'+"),
      include.lowest = TRUE
    ),
    
    weight_band = cut(
      weight,
      breaks = c(-Inf, 130, 160, 190, Inf),
      labels = c("<=130", "131-160", "161-190", "191+"),
      include.lowest = TRUE
    )
  )

df_model <- droplevels(df_model)


# =========================
# 10. COLLAPSE RACE CATEGORIES
# =========================
df_model$race2 <- as.character(df_model$race)
df_model$race2[df_model$race2 %in% c("ASIAN / PACIFIC ISLANDER", "OTHER")] <- "OTHER"
df_model$race2 <- factor(df_model$race2)

df_model <- droplevels(df_model)


# =========================
# 11. CHECK COUNTS
# =========================
table(df_model$age_band)
table(df_model$height_band)
table(df_model$weight_band)
table(df_model$time_bucket)

table(df_model$race2, df_model$sex)
ftable(xtabs(~ race2 + sex + arrested, data = df_model))


# =========================
# 12. MODEL FITTING FUNCTION
# =========================
fit_logit_model <- function(formula, data) {
  brm(
    formula = formula,
    data = data,
    family = bernoulli(link = "logit"),
    chains = 4,
    iter = 3000,
    warmup = 1500,
    cores = min(4, parallel::detectCores()),
    seed = 123,
    control = list(adapt_delta = 0.99, max_treedepth = 15),
    refresh = 200
  )
}


# =========================
# 13. MODELS
# =========================

# Additive model with sex
model_add <- fit_logit_model(
  arrested ~ race2 + sex + boro + age_band + height_band + weight_band + time_bucket,
  df_model
)

summary(model_add)

# Cleaner additive model without sex
model_clean <- fit_logit_model(
  arrested ~ race2 + sex+ age_band + height_band + weight_band + time_bucket ,
  df_model
)
summary(model_add)


loo_add <- loo(model_add)
loo_clean <- loo(model_clean)
loo_compare(loo_add , loo_clean)

summary(model_clean)

# Optional interaction model
model_interaction <- fit_logit_model(
  arrested ~ race2 * sex + boro + age_band + height_band + weight_band + time_bucket,
  df_model
)

summary(model_interaction)


# =========================
# 14. MODEL COMPARISON
# =========================
loo_add <- loo(model_add)
loo_clean <- loo(model_clean)
loo_interaction <- loo(model_interaction)

loo_add
loo_clean
loo_interaction

loo_compare(loo_add, loo_clean, loo_interaction)