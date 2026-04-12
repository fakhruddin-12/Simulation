# =========================
# 1. LOAD PACKAGES + DATA
# =========================
library(readxl)
library(dplyr)
library(brms)
library(loo)

df_stop <- read_excel("/Users/didar/Documents/BDA_GROUP/Simulation/Bayesian Analysis/sqf-2025.xlsx")


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

print(df_stop)

# =========================
# 4. KEEP ONLY COLUMNS NEEDED
# =========================
df_model <- df_stop[, c(
  "MONTH2",
  "STOP_FRISK_TIME",
  "SUSPECT_ARRESTED_FLAG",
  "SUSPECT_RACE_DESCRIPTION",
  "SUSPECT_SEX",
  "SUSPECT_REPORTED_AGE",
  "SUSPECT_HEIGHT",
  "SUSPECT_WEIGHT",
  "STOP_LOCATION_BORO_NAME",
  "STOP_LOCATION_PRECINCT"
)]



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
    precinct=factor(STOP_LOCATION_PRECINCT),

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
    !is.na(time_bucket),
    !is.na(precinct)
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
df_model$race2[df_model$race2 %in% c("ASIAN / PACIFIC ISLANDER","MIDDLE EASTERN/SOUTHWEST ASIAN","AMERICAN INDIAN/ALASKAN NATIVE" ,"OTHER")] <- "OTHER"
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
    refresh = 0
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

# Cleaner additive model
model_clean <- fit_logit_model(
  arrested ~ race2 + sex+ age_band + height_band + weight_band + time_bucket ,
  df_model
)
summary(model_add)


loo_add <- loo(model_add)
loo_clean <- loo(model_clean)
loo_compare(loo_add , loo_clean)

summary(model_clean)



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


#----------------------
#Model1
#----------------------

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
    refresh = 0
  )
}

model_1<-fit_logit_model(
  arrested ~ race2 + sex+ age_band + height_band + weight_band + time_bucket ,
  df_model
)

summary(model_1)

informative_priors <- c(

  # Intercept
  prior(normal(0.284, 0.321), class = Intercept),

  # Age band
  prior(normal(-0.349, 0.254), class = b, coef = age_band18M24),
  prior(normal(-0.125, 0.258), class = b, coef = age_band25M34),
  prior(normal(0.303,  0.272), class = b, coef = age_band35M44),
  prior(normal(0.364,  0.283), class = b, coef = age_band45P),

  # Height band
  prior(normal(-0.178, 0.263), class = b, coef = height_band56M58),
  prior(normal(-0.206, 0.276), class = b, coef = height_band59M511),
  prior(normal(-0.013, 0.294), class = b, coef = height_band6P),

  # Race
  prior(normal(0.048,  0.270), class = b, coef = race2BLACKHISPANIC),
  prior(normal(-0.119, 0.375), class = b, coef = race2OTHER),
  prior(normal(0.029,  0.299), class = b, coef = race2WHITE),
  prior(normal(0.039,  0.221), class = b, coef = race2WHITEHISPANIC),

  # Sex
  prior(normal(-0.425, 0.297), class = b, coef = sexMALE),

  # Time bucket
  prior(normal(-0.377, 0.213), class = b, coef = time_bucket16_21),
  prior(normal(-0.485, 0.227), class = b, coef = time_bucket22_02),

  # Weight band
  prior(normal(-0.020, 0.277), class = b, coef = weight_band131M160),
  prior(normal(-0.300, 0.294), class = b, coef = weight_band161M190),
  prior(normal(-0.182, 0.318), class = b, coef = weight_band191P)
)

#------------------------
#updated 1st model
#_______________________

fit_logit_model_1 <- function(formula, data) {
  brm(
    formula = formula,
    data = data,
    family = bernoulli(link = "logit"),
    chains = 4,
    prior=informative_priors,
    iter = 3000,
    warmup = 1500,
    cores = min(4, parallel::detectCores()),
    seed = 123,
    control = list(adapt_delta = 0.99, max_treedepth = 15),
    refresh = 0
  )
}

model_1_update<-fit_logit_model_1(
  arrested ~ race2 + sex+ age_band + height_band + weight_band + time_bucket ,
  df_model
)

summary(model_1_update)

draws_update <- as_draws_df(model_1_update)

draws_update |>
  dplyr::select(starts_with("b_")) |>        # ← explicit dplyr::
  tidyr::pivot_longer(everything(), names_to = "param", values_to = "value") |>
  ggplot(aes(x = value)) +
  geom_histogram(aes(y = after_stat(density)), bins = 50,
                 fill = "steelblue", alpha = 0.6) +
  geom_density(colour = "red", linewidth = 1) +
  facet_wrap(~ param, scales = "free") +
  theme_minimal()

prior_summary(model_1_update)

prior_summary(model_1)


loo1 <- loo(model_1_update)
loo2 <- loo(model_1)


loo_compare(loo1, loo2)

draws_2025_update <- as_draws_df(model_1_update)

#install.packages("moments")
library(moments)


# Run for all b_ coefficients
results_1 <- imap_dfr(draws_2025_update, check_distribution)

print(results_1)

pp_check(model_1_update)


#----------------------------------------
#model-2
#------------------------------------

model_2 <- brm(
  arrested ~ race2 + sex + age_band + height_band + weight_band + time_bucket + (1 | precinct),
  data = df_model,
  family = bernoulli(link = "logit"),
  prior = informative_priors,
  chains = 4,
  iter = 3000,
  warmup = 1500,
  cores = min(4, parallel::detectCores()),
  seed = 123,
  control = list(adapt_delta = 0.99, max_treedepth = 15),
  refresh = 0
)

summary(model_2)

loo2 <- loo(model_1)
loo3<-loo(model_2)

loo_compare(loo2, loo3)
