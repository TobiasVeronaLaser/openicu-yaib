from datetime import datetime
from pathlib import Path

import polars as pl

from openicu_yaib.io import scan_dataset_stays
from openicu_yaib.stays import dataset_stay_spec
from openicu_yaib.workflow import (
    normalize_ricu_dynamic_reference,
    read_ricu_stay_windows,
)


def test_eicu_stay_reconstructs_openicu_synthetic_timeline(
    tmp_path: Path,
) -> None:
    path = tmp_path / "patient.csv"

    # Equivalent to real eICU stay 141179:
    # 2015-01-01 08:56 - (-22 min) = 2015-01-01 09:18 ICU admission.
    pl.DataFrame(
        {
            "patientunitstayid": [141179],
            "patienthealthsystemstayid": [128927],
            "hospitaldischargeyear": [2015],
            "hospitaladmittime24": ["08:56:00"],
            "hospitaladmitoffset": [-22],
            "unitdischargeoffset": [2042],
        }
    ).write_csv(path)

    result = scan_dataset_stays(
        path,
        dataset_stay_spec("eicu-crd"),
    ).collect()

    expected_admission = (
        datetime(2015, 1, 1, 9, 18)
        - datetime(1970, 1, 1)
    ).total_seconds() / 3600

    assert result["subject_id"].to_list() == [128927]
    assert result["stay_id"].to_list() == [141179]
    assert result["intime_hours"].to_list() == [expected_admission]
    assert result["outtime_hours"].to_list() == [
        expected_admission + 2042 / 60
    ]


def test_eicu_ricu_stay_windows_normalize_patientunitstayid(
    tmp_path: Path,
) -> None:
    path = tmp_path / "ricu_stays.parquet"

    pl.DataFrame(
        {
            "patientunitstayid": [1, 2],
            "start": [0.0, 0.0],
            "end": [59.0, 34.0],
        }
    ).write_parquet(path)

    result = read_ricu_stay_windows(path)

    assert result["stay_id"].to_list() == [1, 2]
    assert result["ricu_start"].to_list() == [0, 0]
    assert result["ricu_end"].to_list() == [59, 34]


def test_eicu_ricu_dynamic_normalizes_keys(tmp_path: Path) -> None:
    path = tmp_path / "ricu_dynamic.parquet"

    pl.DataFrame(
        {
            "patientunitstayid": [1, 1],
            "labresultoffset": [0.0, 1.0],
            "hr": [80.0, 81.0],
        }
    ).write_parquet(path)

    windows = pl.DataFrame(
        {
            "stay_id": [1],
            "ricu_start": [0],
            "ricu_end": [1],
            "ricu_expected_n_timepoints": [2],
        }
    )

    result = normalize_ricu_dynamic_reference(
        reference_dynamic_path=path,
        ricu_windows=windows,
        openicu_columns=["stay_id", "time", "hr"],
    )

    assert result.columns == ["stay_id", "time", "hr"]
    assert result["stay_id"].to_list() == [1, 1]
    assert result["time"].to_list() == [0, 1]
    assert result["hr"].to_list() == [80.0, 81.0]
