# Dataset workflows

There is exactly one Python notebook per OpenICU dataset. Every notebook creates the all-hours/all-concepts OpenICU YAIB-wide output. Datasets with a matching RICU source additionally have one R wrapper in `scripts/datasets/` and perform a 168-hour OpenICU↔RICU validation. `mimic-iv-demo` intentionally has no R wrapper/comparison.

The notebook output layout is `WORKSPACE/yaib/<dataset>/...`. If an OpenICU project root is supplied, `workspace/yaib` is selected automatically. If an arbitrary output directory is supplied, `yaib` is created below that directory and `concept/` is expected alongside it unless `concept_root` is supplied explicitly.
