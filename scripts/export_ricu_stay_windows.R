#!/usr/bin/env Rscript

# Export RICU stay_windows("miiv", interval = hours(1)) for Python debugging.
# Output: /home/q039tl/output/openicu_yaib_converter/ricu_stay_windows_miiv.parquet by default.

suppressPackageStartupMessages({
  library(ricu)
  library(data.table)
  library(lubridate)
})

src <- Sys.getenv("RICU_SRC", unset = "miiv")
out <- Sys.getenv("RICU_STAY_WINDOWS_OUT", unset = "/home/q039tl/output/openicu_yaib_converter/ricu_stay_windows_miiv.parquet")

interval <- as.difftime(1, units = "hours")
patients <- stay_windows(src, interval = interval)
#patients <- stay_windows(src, interval = hours(1))
dt <- as.data.table(patients)

# Keep original column names. Typical columns include stay_id and end.
print(names(dt))
print(head(dt))
print(meta_vars(patients))

if (requireNamespace("arrow", quietly = TRUE)) {
  arrow::write_parquet(dt, out)
  message("Wrote parquet: ", out)
} else {
  csv_out <- sub("\\.parquet$", ".csv", out)
  data.table::fwrite(dt, csv_out)
  message("Package 'arrow' not available. Wrote CSV: ", csv_out)
}
