# openicu-yaib

`openicu-yaib` converts OpenICU concept parquet outputs into a YAIB/RICU-compatible dynamic wide table for the ICU mortality use case.

The main output has the shape:

```text
stay_id | time | alb | alp | alt | ast | ... | wbc
```

`time` is the YAIB-style integer hour since ICU admission. With an ICU stays table, the converter maps timestamped OpenICU concept rows to ICU stays and aggregates them to an hourly grid. Without an ICU stays table, the concept parquets must already contain `stay_id`, integer `time`, and `numeric_value`.

## Current MVP workflow

The recommended workflow is `example/00_create_yaib_wide_and_compare_ricu.ipynb`. It has four cells:

1. build the OpenICU YAIB/RICU-style wide parquet for all available ICU stay hours (`max_hours=None`);
2. build a second OpenICU YAIB/RICU-style wide parquet for the first 7 days (`max_hours=7 * 24`, inclusive max time) for validation;
3. optionally run the R/RICU export scripts;
4. compare the 7-day generated OpenICU parquet against the R/RICU reference parquet using the same stay-window logic as the working archive notebook.

The all-hours parquet is intended for downstream ML/training. The 7-day parquet is intended for R/RICU validation.

The notebook exposes only the dataset, OpenICU concept version, time horizon, and paths. The creation and comparison logic from the archived notebooks lives in `src/openicu_yaib/workflow.py`.

## Install

```bash
python -m pip install -e .
```

For development:

```bash
python -m pip install -e ".[dev]"
pytest -q
```

## Path configuration

The simple workflow writes generated files below:

```text
~/output/openicu_yaib
```

The notebook can use explicit path variables:

```python
CONCEPT_ROOT = Path("/path/to/OpenICU/concept/output")
ICUSTAYS_CSV = Path("/path/to/mimiciv/3.1/icu/icustays.csv.gz")
RICU_CONCEPT_DICT = Path("/path/to/ricu/inst/extdata/config/concept-dict.json")
```

Alternatively, set environment variables:

```bash
export OPENICU_YAIB_OUTPUT_ROOT="$HOME/output/openicu_yaib"
export OPENICU_YAIB_CONCEPT_ROOT="/path/to/OpenICU/concept/output"
export OPENICU_YAIB_ICUSTAYS_CSV="/path/to/mimiciv/3.1/icu/icustays.csv.gz"
export OPENICU_YAIB_RICU_CONCEPT_DICT="/path/to/ricu/inst/extdata/config/concept-dict.json"
```

The fallback defaults are intentionally lightweight local-layout defaults for the example notebook. In most environments, pass paths explicitly or use the environment variables above.

## R/RICU validation export

For the optional validation step, create the R/RICU reference parquets in the same output directory:

```bash
RICU_OUT_DIR="$HOME/output/openicu_yaib" Rscript scripts/export_ricu_dynamic_vars.R
RICU_OUT_DIR="$HOME/output/openicu_yaib" Rscript scripts/export_ricu_stay_windows.R
```

This writes files such as:

```text
~/output/openicu_yaib/ricu_dynamic_vars_miiv.parquet
~/output/openicu_yaib/ricu_stay_windows_miiv.parquet
```

The comparison uses the same window logic as the working archive notebook: RICU stay windows are converted to integer hours, capped to `MAX_HOURS`, and RICU dynamic rows are filtered to `start <= time <= end`.

## Python usage

Config-first usage:

```python
from pathlib import Path
from openicu_yaib import build_mortality_dynamic_wide_from_config

lf = build_mortality_dynamic_wide_from_config(Path("example/config/openicu_yaib.yml"))
lf.sink_parquet("output/yaib_mortality_dynamic.parquet")
```

Or write directly from the config:

```python
from pathlib import Path
from openicu_yaib import run_from_config

run_from_config(Path("example/config/openicu_yaib.yml"))
```

Notebook-friendly usage:

```python
from pathlib import Path
from openicu_yaib import build_and_write_yaib_wide_for_dataset

result = build_and_write_yaib_wide_for_dataset(
    dataset="mimic-iv",
    version="1.0.0",
    max_hours=None,
    output_root=Path.home() / "output" / "openicu_yaib",
    concept_root=Path("/path/to/OpenICU/concept/output"),
    icustays_csv=Path("/path/to/mimiciv/3.1/icu/icustays.csv.gz"),
    ricu_concept_dict=Path("/path/to/ricu/inst/extdata/config/concept-dict.json"),
)
```

## CLI usage

Preferred config-first mode:

```bash
openicu-yaib --config example/config/openicu_yaib.yml
```

Direct-argument mode is also available:

```bash
openicu-yaib \
  --concept-root /path/to/openicu/workspace/concept \
  --dataset mimic-iv \
  --version 1.0.0 \
  --no-grid \
  --output /path/to/output/yaib_mortality_dynamic.parquet
```

For subject-level timestamped concept parquets, provide ICU stays and enable the grid if desired:

```bash
openicu-yaib \
  --concept-root /path/to/openicu/workspace/concept \
  --icustays-csv /path/to/mimiciv/3.1/icu/icustays.csv.gz \
  --ricu-concept-dict /path/to/ricu/inst/extdata/config/concept-dict.json \
  --dataset mimic-iv \
  --version 1.0.0 \
  --aggregation-mode mean \
  --grid-end-rounding floor \
  --output /path/to/output/yaib_mortality_dynamic.parquet
```

## Repository layout

```text
configs/
  mortality_dynamic_vars.yml   # mortality dynamic variable set
  concept_mapping.yml          # YAIB/RICU name -> OpenICU concept name
  unit_mapping.yml             # extension point for explicit unit conversion
example/
  config/openicu_yaib.yml
  00_create_yaib_wide_and_compare_ricu.ipynb
scripts/
  export_ricu_dynamic_vars.R
  export_ricu_stay_windows.R
src/openicu_yaib/
  config.py
  pipeline.py
  concepts.py
  io.py
  transform.py
  validation.py
  compare.py
  workflow.py
  ricu_meta.py
  cli.py
```

## Notes on units

The imported converter logic currently consumes `numeric_value` directly. `configs/unit_mapping.yml` is included as the explicit place to define YAIB unit harmonization rules when OpenICU concept outputs expose units that need conversion.

## Current limitations

- The default dynamic variable set targets the YAIB ICU mortality use case.
- The package builds the dynamic wide feature table; it does not yet implement the complete YAIB cohort and label generation pipeline.
- Exact equality with RICU/YAIB reference outputs can depend on ICU-window filtering, time rounding, grid construction, aggregation mode, and source concept coverage.

test