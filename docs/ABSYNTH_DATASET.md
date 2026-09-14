# ABSynth-shaped route-step dataset

The website's main table reads `data/database/SynInsight_ABSynth_Dataset.csv` directly. It has the same nine named columns, in the same order, as the supplied ABSynth reference. The reference is actually tab-delimited despite its `.csv` suffix and has an empty trailing header. Our CSV uses comma separation, standard quoting and UTF-8 with BOM; the companion `.tsv` preserves tab separation without the unnamed column. Reference records are not copied into this dataset.

## Row scope

6,555 rows represent operation occurrences in 635 existing paths across 91 extracted papers. They cover 2,166 distinct paper-specific operations. Shared upstream operations repeat across paths. The complete extraction database contains 2,315 operations: 149 operations not assigned to these exported paths are not included in this path-shaped table. Do not count rows as unique reactions or regard paths as verified complete syntheses. Partial, formal and control branches remain included.

## Field mapping

| Column | Source and meaning |
| --- | --- |
| PathId | Existing globally unique `route_id` from `route_steps.csv`; treated as text, not renumbered. |
| TargetName | Existing route label with paper-ID prefix removed. It may be a named target, a numbered endpoint, or a branch description; not a newly assigned chemical name. |
| Year | First four characters of existing `publication_date` in `data/papers.json`. |
| DOI | Existing paper DOI. |
| Author | Existing `first_author` text, preserved as recorded; may contain multiple names. Not normalized to corresponding-author surname. |
| StepId | One-based step occurrence index within PathId. `(PathId, StepId)` is unique. Original local operation/event IDs remain in metadata. |
| RxnSMILES | Existing `canonical_reaction_smiles`, unchanged. Not guaranteed atom-mapped or atom-balanced. Dot-separated species are preserved. |
| RxnName | Existing operation `transformation` only. No reaction-class inference from SMILES. 6,409 rows are blank. |
| Conditions | Labeled, semicolon-separated existing agents, solvents, temperature/time, pressure/current and operation stages. Nested values use JSON so source stage detail is retained. 215 rows are blank; presence does not mean conditions are complete or standardized. |

## Provenance and review

`data/database/absynth_metadata.json` stores path type, coverage, review status, original step/event identifiers, reported yield, source locators and source SHA-256 hashes. It accompanies the CSV and must be retained for reuse. All records remain candidates pending independent chemical review. Source conflicts and full limitations are in each original case dataset/report; a compact conditions cell does not reconcile them. Blank values mean absent in existing data, not a negative result.

Filters and filtered downloads retain the exact nine-column schema. The website defaults to all paths. A target/route button filters to its full path; Step details links back to the source case. Related paper coverage and the original catalog remain available below the main dataset.

## Rebuild

Run from the project root:

```sh
.venv/Scripts/python.exe scripts/build_absynth.py
.venv/Scripts/python.exe scripts/build_web.py
.venv/Scripts/python.exe scripts/validate_web.py
```

The builder validates row identity, path-step order and reaction agreement with case data (allowing only dot-component order changes), and records source hashes. Existing scientific exports are not overwritten. Publication metadata are reused, not newly verified against publishers.
