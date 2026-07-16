#!/usr/bin/env Rscript

# Export the RICU reference files for OpenICU dataset MIMIC-IV.
Sys.setenv(RICU_SRC = "miiv")

script_dir <- file.path(getwd(), "scripts")
source(file.path(script_dir, "export_ricu_dynamic_vars.R"), chdir = TRUE)
source(file.path(script_dir, "export_ricu_stay_windows.R"), chdir = TRUE)
