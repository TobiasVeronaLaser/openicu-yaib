"""Dataset-specific ICU stay table definitions for autonomous examples."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DatasetStaySpec:
    dataset: str
    filenames: tuple[str, ...]
    subject_col: str
    stay_col: str
    intime_col: str | None
    outtime_col: str | None
    numeric_time_scale_hours: float = 1.0
    subject_is_stay: bool = False


_SPECS = {
    "mimic-iv": DatasetStaySpec("mimic-iv", ("icustays.csv.gz",), "subject_id", "stay_id", "intime", "outtime"),
    "miiv": DatasetStaySpec("miiv", ("icustays.csv.gz",), "subject_id", "stay_id", "intime", "outtime"),
    "mimic-iii": DatasetStaySpec("mimic-iii", ("ICUSTAYS.csv.gz", "icustays.csv.gz"), "SUBJECT_ID", "ICUSTAY_ID", "INTIME", "OUTTIME"),
    "mimic": DatasetStaySpec("mimic", ("ICUSTAYS.csv.gz", "icustays.csv.gz"), "SUBJECT_ID", "ICUSTAY_ID", "INTIME", "OUTTIME"),
    "mimic_demo": DatasetStaySpec("mimic_demo", ("ICUSTAYS.csv.gz", "icustays.csv.gz"), "SUBJECT_ID", "ICUSTAY_ID", "INTIME", "OUTTIME"),
    "eicu": DatasetStaySpec("eicu", ("patient.csv.gz",), "patientunitstayid", "patientunitstayid", "unitadmitoffset", "unitdischargeoffset", 1 / 60, True),
    "eicu_demo": DatasetStaySpec("eicu_demo", ("patient.csv.gz",), "patientunitstayid", "patientunitstayid", "unitadmitoffset", "unitdischargeoffset", 1 / 60, True),
    "hirid": DatasetStaySpec("hirid", ("general_table.csv",), "patientid", "patientid", "admissiontime", None, 1.0, True),
    "aumc": DatasetStaySpec("aumc", ("admissions.csv",), "admissionid", "admissionid", "admittedat", "dischargedat", 1 / 3_600_000, True),
    "sicdb": DatasetStaySpec("sicdb", ("cases.csv.gz",), "CaseID", "CaseID", "ICUOffset", "TimeOfStay", 1 / 60, True),
    "sic": DatasetStaySpec("sic", ("cases.csv.gz",), "CaseID", "CaseID", "ICUOffset", "TimeOfStay", 1 / 60, True),
    # NWICU is not part of the supplied standard ricu source configuration.
    # The autonomous fallback assumes OpenICU subject_id already identifies an ICU stay.
    "nwicu": DatasetStaySpec("nwicu", (), "subject_id", "subject_id", None, None, 1.0, True),
}


def dataset_stay_spec(dataset: str) -> DatasetStaySpec:
    key = dataset.lower()
    if key not in _SPECS:
        raise ValueError(f"No ICU-stay specification for dataset {dataset!r}.")
    return _SPECS[key]


def find_dataset_stay_file(dataset: str, explicit: str | Path | None = None) -> Path | None:
    """Resolve a raw ICU-stay table without requiring notebook code changes."""
    if explicit is not None:
        return Path(explicit).expanduser().resolve()

    env_specific = os.getenv(f"OPENICU_YAIB_{dataset.upper().replace('-', '_')}_STAYS")
    if env_specific:
        return Path(env_specific).expanduser().resolve()

    spec = dataset_stay_spec(dataset)
    if not spec.filenames:
        return None

    roots = []
    for name in ("OPENICU_YAIB_DATA_ROOT", "RICU_DATA_PATH"):
        value = os.getenv(name)
        if value:
            roots.append(Path(value).expanduser())
    roots.extend([Path.home() / "ricu_data", Path.home() / "physionet.org" / "files"])

    for root in roots:
        if not root.exists():
            continue
        for filename in spec.filenames:
            matches = sorted(root.rglob(filename))
            if matches:
                return matches[0].resolve()
    return None
