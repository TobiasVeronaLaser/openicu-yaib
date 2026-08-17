"""Dataset registry used by the one-notebook-per-dataset YAIB workflows."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DatasetSpec:
    """OpenICU dataset name and optional matching RICU source."""

    name: str
    ricu_source: str | None
    aliases: tuple[str, ...] = ()

    @property
    def has_ricu(self) -> bool:
        return self.ricu_source is not None


DATASETS: tuple[DatasetSpec, ...] = (
    DatasetSpec("aumc", "aumc"),
    DatasetSpec("eicu-crd", "eicu", ("eicu",)),
    DatasetSpec("eicu-demo", "eicu_demo", ("eicu_demo",)),
    DatasetSpec("hirid", "hirid"),
    DatasetSpec("mimic-iii", "mimic", ("mimic",)),
    DatasetSpec("mimic-iii-demo", "mimic_demo", ("mimic_demo", "mimic-demo")),
    DatasetSpec("mimic-iv", "miiv", ("miiv",)),
    # ricu has no separate built-in/source entry corresponding to OpenICU mimic-iv-demo.
    DatasetSpec("mimic-iv-demo", None),
    DatasetSpec("nwicu", None),
    DatasetSpec("sic", "sic", ("sicdb",)),
)


def dataset_spec(dataset: str) -> DatasetSpec:
    """Resolve canonical OpenICU dataset metadata from a name or alias."""
    key = dataset.lower()
    for spec in DATASETS:
        if key == spec.name or key in spec.aliases:
            return spec
    supported = ", ".join(spec.name for spec in DATASETS)
    raise ValueError(f"Unsupported dataset {dataset!r}; expected one of: {supported}")
