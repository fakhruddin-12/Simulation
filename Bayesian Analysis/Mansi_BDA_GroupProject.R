# Load required libraries and dataset
library(readxl)
library(dplyr)
library(brms)
library(loo)
library(writexl)
library(bayesplot)

options(mc.cores = parallel::detectCores())

df_raw <- read_excel("sqf-2025.xlsx")


# Clean raw data

# Replace string "(null)" entries with NA across all character columns
char_cols <- sapply(df_raw, is.character)
df_raw[char_cols] <- lapply(df_raw[char_cols], function(col) {
  col[col == "(null)"] <- NA
  col})

# Select variables required for modelling
df_clean <- df_raw[, c(
  "YEAR2",
  "MONTH2",
  "STOP_ID",
  "STOP_FRISK_TIME",
  "SUSPECT_ARRESTED_FLAG",
  "SUSPECT_RACE_DESCRIPTION",
  "SUSPECT_SEX",
  "SUSPECT_REPORTED_AGE",
  "STOP_LOCATION_PRECINCT",
  "WEAPON_FOUND_FLAG"
)]

# Restrict dataset to first quarter (Q1)
df_clean <- df_clean %>%
  filter(MONTH2 %in% c("January", "February", "March"))
nrow(df_clean)

# Construct model variables and transform raw fields
df_clean <- df_clean %>%
  mutate(
    # Binary outcome: arrest indicator
    arrested = ifelse(SUSPECT_ARRESTED_FLAG == "Y", 1,
                      ifelse(SUSPECT_ARRESTED_FLAG == "N", 0, NA)),

    # Convert and encode covariates
    age = suppressWarnings(as.numeric(SUSPECT_REPORTED_AGE)),
    sex = factor(SUSPECT_SEX),
    race = factor(SUSPECT_RACE_DESCRIPTION),
    precinct = factor(STOP_LOCATION_PRECINCT),
    weapon = factor(WEAPON_FOUND_FLAG),

    # Extract hour from time string (HH format)
    hour = suppressWarnings(as.integer(substr(as.character(STOP_FRISK_TIME), 1, 2))),

    # Create time-of-day categorical variable
    time_bucket = case_when(
      hour >= 16 & hour <= 21 ~ "16_21",
      hour >= 22 | hour <= 2  ~ "22_02",
      hour >= 3  & hour <= 15 ~ "remaining",
      TRUE ~ NA_character_
    ),

    # Set reference category for time
    time_bucket = factor(time_bucket,
                         levels = c("remaining", "16_21", "22_02"))
  )

# Remove observations with missing values in model variables
df_clean <- df_clean %>%
  filter(
    !is.na(arrested),
    !is.na(race),
    !is.na(sex),
    !is.na(age),
    !is.na(time_bucket),
    !is.na(precinct),
    !is.na(weapon)
  )

# Restrict to plausible age range
df_clean <- df_clean %>%
  filter(age >= 10 & age <= 90)

# Discretise age into categorical bands
df_clean <- df_clean %>%
  mutate(
    age_band = cut(
      age,
      breaks = c(-Inf, 17, 24, 34, 44, Inf),
      labels = c("<=17", "18-24", "25-34", "35-44", "45+"),
      include.lowest = TRUE
    )
  )

# Collapse race categories with fewer observations into "OTHER"
# to improve numerical stability of race coefficient estimates
df_clean$race2 <- as.character(df_clean$race)
df_clean$race2[df_clean$race2 %in% c(
  "ASIAN / PACIFIC ISLANDER",
  "MIDDLE EASTERN/SOUTHWEST ASIAN",
  "AMERICAN INDIAN/ALASKAN NATIVE",
  "OTHER"
)] <- "OTHER"

df_clean$race2 <- factor(df_clean$race2)
df_clean <- droplevels(df_clean)
nrow(df_clean)

# Save processed dataset
write_xlsx(df_clean, "processed_sqf2025.xlsx")

# Specify informative priors based on 2024 Q1 analysis
# Note: priors below are elicited from a separate fit to 2024 Q1 data
# (sqf-2024.xlsx) using the same preprocessing pipeline and brms default priors.

priors_fixed <- c(
  # Intercept prior
  prior(normal(0.284, 0.321), class = Intercept),

  # Age effects
  prior(normal(-0.349, 0.254), class = b, coef = age_band18M24),
  prior(normal(-0.125, 0.258), class = b, coef = age_band25M34),
  prior(normal(0.303, 0.272), class = b, coef = age_band35M44),
  prior(normal(0.364, 0.283), class = b, coef = age_band45P),

  # Race effects
  prior(normal(0.048, 0.270), class = b, coef = race2BLACKHISPANIC),
  prior(normal(-0.119, 0.375), class = b, coef = race2OTHER),
  prior(normal(0.029, 0.299), class = b, coef = race2WHITE),
  prior(normal(0.039, 0.221), class = b, coef = race2WHITEHISPANIC),

  # Sex effect
  prior(normal(-0.425, 0.297), class = b, coef = sexMALE),

  # Time-of-day effects
  prior(normal(-0.377, 0.213), class = b, coef = time_bucket16_21),
  prior(normal(-0.485, 0.227), class = b, coef = time_bucket22_02)
)

# Extend priors to include weapon effect (Model 3)
priors_full <- c(
  priors_fixed,
  prior(normal(1.888, 0.099), class = b, coef = weaponY)
)


# Fit baseline logistic regression (fixed effects only)
model_1 <- brm(
  arrested ~ race2 + sex + age_band + time_bucket,
  data = df_clean,
  family = bernoulli(link = "logit"),
  prior = priors_fixed,
  chains = 4, iter = 3000, warmup = 1500,
  seed = 123,
  control = list(adapt_delta = 0.99,   # increased from default 0.8 to reduce divergences
                 max_treedepth = 15)    # increased to allow deeper tree exploration
)

summary(model_1)

# Fit hierarchical model with precinct random intercepts and time slopes
model_2 <- brm(
  arrested ~ race2 + sex + age_band + time_bucket +
    (1 + time_bucket || precinct),
  data = df_clean,
  family = bernoulli(link = "logit"),
  prior = c(
    priors_fixed,
    prior(lognormal(log(0.47), 0.3), class = "sd", coef = "Intercept", group = "precinct"),
    prior(lognormal(log(0.35), 0.3), class = "sd", coef = "time_bucket16_21", group = "precinct"),
    prior(lognormal(log(0.57), 0.3), class = "sd", coef = "time_bucket22_02", group = "precinct")
  ),
  chains = 4, iter = 3000, warmup = 1500,
  seed = 123,
  control = list(adapt_delta = 0.99, max_treedepth = 15)
)

summary(model_2)


# Fit full hierarchical model including weapon indicator
model_3 <- brm(
  arrested ~ weapon + race2 + sex + age_band + time_bucket +
    (1 + time_bucket || precinct),
  data = df_clean,
  family = bernoulli(link = "logit"),
  prior = c(
    priors_full,
    prior(lognormal(log(0.47), 0.3), class = "sd", coef = "Intercept", group = "precinct"),
    prior(lognormal(log(0.35), 0.3), class = "sd", coef = "time_bucket16_21", group = "precinct"),
    prior(lognormal(log(0.57), 0.3), class = "sd", coef = "time_bucket22_02", group = "precinct")
  ),
  chains = 4, iter = 3000, warmup = 1500,
  seed = 123,
  control = list(adapt_delta = 0.99, max_treedepth = 15)
)

# Summarise posterior estimates
summary(model_3)

# Trace plots to assess mixing and convergence

# Trace plots for Model 1
mcmc_trace(as.array(model_1),
           pars = c("b_Intercept", "b_sexMALE"))

# Trace plots for Model 2
mcmc_trace(as.array(model_2),
           pars = c("b_Intercept", "sd_precinct__Intercept"))

# Trace plots for Model 3
mcmc_trace(as.array(model_3),
           pars = c(
             "b_Intercept",
             "b_weaponY",
             "b_sexMALE",
             "b_time_bucket16_21",
             "b_time_bucket22_02",
             "sd_precinct__Intercept"
           ))


# Compare models using LOO-CV
loo1 <- loo(model_1)
loo2 <- loo(model_2)
loo3 <- loo(model_3)

loo_compare(loo1, loo2, loo3)


# Compute DIC for model comparison
compute_DIC <- function(model){
  log_lik_mat <- log_lik(model)  # S x N matrix: rows=samples, cols=observations

  mean_deviance <- -2 * mean(rowSums(log_lik_mat))  # E[-2 * log p(y|theta)]
  post_mean <- colMeans(log_lik_mat)                # posterior mean log-lik per obs
  dev_hat <- -2 * sum(post_mean)                    # deviance at posterior mean

  p_d <- mean_deviance - dev_hat                    # effective number of parameters
  DIC <- mean_deviance + p_d                        # DIC = mean deviance + p_d

  return(list(DIC = DIC))
}
dic_compare <- data.frame(
  Model = c("Model_1","Model_2","Model_3"),
  DIC = c(
    compute_DIC(model_1)$DIC,
    compute_DIC(model_2)$DIC,
    compute_DIC(model_3)$DIC
  )
)
dic_compare


# Inspect priors for the selected model
prior_summary(model_3)


# Posterior predictive checks for model fit
pp_check(model_3, type = "stat", stat = "mean")

y_rep <- posterior_predict(model_3)
pp_means <- rowMeans(y_rep)
png("pp_image.png", width = 900, height = 600)
hist(pp_means,
     main = "Posterior Predictive Means",
     xlab = "Mean Arrest Probability")

# Compare observed mean to predictive distribution
abline(v = mean(df_clean$arrested), col = 'red', lwd = 2)
dev.off()

# Session information for reproducibility
sessionInfo()
