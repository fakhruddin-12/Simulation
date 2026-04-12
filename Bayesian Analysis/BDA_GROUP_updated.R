# =========================
# 1. LOAD PACKAGES + DATA
# =========================
library(readxl)
library(dplyr)
library(brms)

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

# Collapse rare levels into "OTHER" using base R
lump_rare_levels <- function(x, min_count = 100, other_label = "OTHER") {
  x <- as.character(x)
  tab <- table(x, useNA = "no")
  keep_levels <- names(tab[tab >= min_count])
  
  x[!(x %in% keep_levels)] <- other_label
  factor(x)
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
    SUSPECT_ARRESTED_FLAG,
    SUSPECT_RACE_DESCRIPTION,
    SUSPECT_SEX,
    SUSPECT_REPORTED_AGE,
    SUSPECT_HEIGHT,
    SUSPECT_WEIGHT,
    SUSPECT_BODY_BUILD_TYPE,
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
    body_build = factor(SUSPECT_BODY_BUILD_TYPE),
    boro = factor(STOP_LOCATION_BORO_NAME)
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
    !is.na(body_build),
    !is.na(boro)
  )


# =========================
# 8. BASIC SANITY FILTERS
#    (adjust if you want)
# =========================
df_model <- df_model %>%
  filter(
    age >= 10 & age <= 90,
    weight >= 60 & weight <= 400,
    height_in >= 48 & height_in <= 84
  )


# =========================
# 9. COLLAPSE VERY SMALL CATEGORIES
# =========================
df_model <- df_model %>%
  mutate(
    race = lump_rare_levels(race, min_count = 100, other_label = "OTHER"),
    body_build = lump_rare_levels(body_build, min_count = 100, other_label = "OTHER")
  )

df_model <- droplevels(df_model)

# =========================
# 10. BUCKETIZATION
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

table(df_model$age_band)
table(df_model$height_band)
table(df_model$weight_band)

df_model$race2 <- as.character(df_model$race)

df_model$race2[df_model$race2 %in% c("ASIAN / PACIFIC ISLANDER", "OTHER")] <- "OTHER"

df_model$race2 <- factor(df_model$race2)

table(df_model$race2, df_model$sex)
ftable(xtabs(~ race2 + sex + arrested, data = df_model))


df_model$body_build2 <- as.character(df_model$body_build)

df_model$body_build2[df_model$body_build2 %in% c("OTHER", "U")] <- "OTHER_OR_U"

df_model$body_build2 <- factor(df_model$body_build2)
table(df_model$body_build2, df_model$sex)
ftable(xtabs(~ body_build2 + sex + arrested, data = df_model))

# =========================
# 11. MODEL FITTING FUNCTION
# =========================
fit_logit_model <- function(formula, data) {
  brm(
    formula = formula,
    data = data,
    family = bernoulli(link = "logit"),
    chains = 4,
    iter = 4000,
    warmup = 2000,
    seed = 123,
    cores = min(4, parallel::detectCores()),
    refresh = 200
  )
}
model_add <- brm(
  arrested ~ race2 + sex + age_band + height_band + weight_band + body_build2 + boro,
  data = df_model,
  family = bernoulli(link = "logit"),
  prior = c(
    prior(normal(0, 1.5), class = "b"),
    prior(student_t(3, 0, 2.5), class = "Intercept")
  ),
  chains = 4,
  iter = 3000,
  warmup = 1500,
  cores = 4,
  seed = 123,
  control = list(adapt_delta = 0.99, max_treedepth = 15),
  refresh = 200
)
summary(model_add)
model_no_body <- update(model_add, formula. = . ~ . - body_build2)
loo(model_add, model_no_body)


model_clean <- brm(
  arrested ~ race2 + age_band + height_band + weight_band + boro,
  data = df_model,
  family = bernoulli(link = "logit"),
  prior = c(
    prior(normal(0, 1.5), class = "b"),
    prior(student_t(3, 0, 2.5), class = "Intercept")
  ),
  chains = 4,
  iter = 3000,
  warmup = 1500,
  cores = 4,
  seed = 123,
  control = list(adapt_delta = 0.99, max_treedepth = 15),
  refresh = 200
)
summary(model_clean)
loo(model_add, model_clean)