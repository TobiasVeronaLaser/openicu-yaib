# openicu-yaib

`openicu-yaib` converts OpenICU concept parquet outputs into a YAIB-compatible dynamic wide table for the ICU mortality use case.

The main output has the shape:

```text
stay_id | time | alb | alp | alt | ast | ... | wbc
```

`time` is the YAIB-style integer hour. When `icustays_csv` is provided, timestamps are mapped to ICU stays and converted to hours since ICU admission. When `icustays_csv` is `null`, the concept parquets are expected to already contain `stay_id`, integer `time`, and `numeric_value`.

## Current MVP workflow

The simplest workflow is `example/00_create_yaib_wide_and_compare_ricu.ipynb`. It has four cells:

1. build the OpenICU YAIB/RICU-style wide parquet for all available stay hours (`max_hours=None`);
2. build a second OpenICU YAIB/RICU-style wide parquet for the first two weeks (`max_hours=14 * 24`, inclusive max time);
3. run the R/RICU export scripts if a comparison is needed;
4. compare the two-week generated parquet against the R/RICU parquet using the same stay-window logic as the working archive notebook.

The notebook exposes only the dataset, version, time horizon and paths. The creation and comparison logic from the archived notebooks lives in `src/openicu_yaib/workflow.py`.

## Install

```bash
python -m pip install -e .
```

## Python usage

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

## CLI usage

Preferred config-first mode:

```bash
openicu-yaib --config example/config/openicu_yaib.yml
```

Legacy direct-argument mode is still available:

```bash
openicu-yaib   --concept-root /path/to/openicu/workspace/concept   --dataset mimic-iv   --version 1.0.0   --no-grid   --output /path/to/output/yaib_mortality_dynamic.parquet
```

For subject-level timestamped concept parquets, provide ICU stays and enable the grid if desired:

```bash
openicu-yaib   --concept-root /path/to/openicu/workspace/concept   --icustays-csv /path/to/mimiciv/3.1/icu/icustays.csv.gz   --ricu-concept-dict /path/to/ricu/inst/extdata/config/concept-dict.json   --dataset mimic-iv   --version 1.0.0   --aggregation-mode mean   --grid-end-rounding floor   --output /path/to/output/yaib_mortality_dynamic.parquet
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
  01_openicu_concepts_to_yaib_mortality_wide.ipynb
  02_validate_yaib_mortality_wide.ipynb
  03_compare_openicu_vs_reference.ipynb
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
- Exact equality with RICU/YAIB reference outputs can depend on ICU-window filtering, time rounding, grid construction, and aggregation mode.
