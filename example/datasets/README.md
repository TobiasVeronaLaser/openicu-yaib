# Dataset-specific YAIB validation notebooks

Each notebook follows the same three-stage workflow as
`example/00_create_yaib_wide_and_compare_ricu.ipynb`:

1. run the matching `scripts/datasets/export_ricu_<source>.R` wrapper;
2. transform OpenICU `subject_id`, `time`, `numeric_value` concept parquets to YAIB wide format for all hours and for `0..168` hours;
3. normalize dtypes and compare the 168-hour OpenICU output with RICU.

The notebooks resolve raw ICU-stay tables from, in order:

- `OPENICU_YAIB_<DATASET>_STAYS`;
- `OPENICU_YAIB_DATA_ROOT`;
- `RICU_DATA_PATH`;
- the default local `~/ricu_data` and `~/physionet.org/files` trees.

Dataset mappings are derived from the RICU `id_cfg` definitions:

- eICU/eICU demo: `patient.csv.gz`, `patientunitstayid`, `unitadmitoffset`, `unitdischargeoffset`;
- HiRID: `general_table.csv`, `patientid`, `admissiontime`;
- AUMCdb: `admissions.csv`, `admissionid`, `admittedat`, `dischargedat`;
- MIMIC-III/demo: `ICUSTAYS.csv.gz`, `SUBJECT_ID`, `ICUSTAY_ID`, `INTIME`, `OUTTIME`;
- MIMIC-IV: `icustays.csv.gz`, `subject_id`, `stay_id`, `intime`, `outtime`;
- SICdb: `cases.csv.gz`, `CaseID`, `ICUOffset`, `TimeOfStay`.

NWICU is not present in the supplied standard RICU source configuration. Its
notebook therefore uses the explicit fallback assumption that OpenICU
`subject_id` already represents an ICU stay and that `time` is already a
relative hour value.
