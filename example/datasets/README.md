# Dataset-specific validation notebooks

Each notebook follows the same workflow:

1. create an all-hours OpenICU YAIB-wide parquet;
2. create a seven-day validation parquet;
3. run the matching dataset-specific R script;
4. compare the OpenICU output with the R/`ricu` reference.

The notebooks default to `INCLUDE_GRID=False`. Consequently, OpenICU concept parquets must already contain `stay_id`, integer-hour `time`, and `numeric_value`. This is the portable path for datasets whose raw ICU-stay tables do not follow the MIMIC-IV schema.

| Notebook | OpenICU dataset | RICU source | R support |
|---|---|---|---|
| `eicu.ipynb` | `eicu` | `eicu` | built in |
| `nwicu.ipynb` | `nwicu` | `nwicu` | custom configuration required |
| `hirid.ipynb` | `hirid` | `hirid` | built in |
| `sic.ipynb` | `sicdb` | `sic` | custom configuration required |
| `aumc.ipynb` | `aumc` | `aumc` | built in |
| `miiv.ipynb` | `mimic-iv` | `miiv` | built in |
| `mimic.ipynb` | `mimic-iii` | `mimic` | built in |
| `mimic_demo.ipynb` | `mimic_demo` | `mimic_demo` | demo package required |
| `eicu_demo.ipynb` | `eicu_demo` | `eicu_demo` | demo package required |

Run a matching R export from the repository root, for example:

```bash
RICU_OUT_DIR="$HOME/output/openicu_yaib/eicu" \
Rscript scripts/datasets/export_ricu_eicu.R
```
