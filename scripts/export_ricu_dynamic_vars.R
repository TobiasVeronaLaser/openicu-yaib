#!/usr/bin/env Rscript

# Export RICU dynamic variables for Python comparison.
# Output: /home/q039tl/output/openicu_yaib_windows/ricu_dynamic_vars_miiv.parquet by default.

suppressPackageStartupMessages({
  library(ricu)
  library(data.table)
  library(lubridate)
})

src <- Sys.getenv("RICU_SRC", unset = "miiv")
out <- Sys.getenv("RICU_DYN_OUT", unset = "/home/q039tl/output/openicu_yaib_converter/ricu_dynamic_vars_miiv.parquet")

dynamic_vars <- c("alb", "alp", "alt", "ast", "be", "bicar", "bili", "bili_dir",
                  "bnd", "bun", "ca", "cai", "ck", "ckmb", "cl", "crea", "crp", 
                  "dbp", "fgn", "fio2", "glu", "hgb", "hr", "inr_pt", "k", "lact",
                  "lymph", "map", "mch", "mchc", "mcv", "methb", "mg", "na", "neut", 
                  "o2sat", "pco2", "ph", "phos", "plt", "po2", "ptt", "resp", "sbp", 
                  "temp", "tnt", "urine", "wbc")

interval <- as.difftime(1, units = "hours")
df <- load_concepts(dynamic_vars, src = src, interval = interval)
#df <- load_concepts(dynamic_vars, src = src, interval = hours(1))
dt <- as.data.table(df)

print(names(dt))
print(head(dt))
print(meta_vars(df))

# Normalize charttime to integer hours if present as difftime.
if ("charttime" %in% names(dt)) {
  dt[, time := as.integer(as.numeric(charttime, units = "hours"))]
}

if (requireNamespace("arrow", quietly = TRUE)) {
  arrow::write_parquet(dt, out)
  message("Wrote parquet: ", out)
} else {
  csv_out <- sub("\\.parquet$", ".csv", out)
  data.table::fwrite(dt, csv_out)
  message("Package 'arrow' not available. Wrote CSV: ", csv_out)
}
