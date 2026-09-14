# SynInsight Atlas

**Literature-derived synthesis routes for benchmarking machine-learning retrosynthesis models.**

SynInsight Atlas organizes synthesis pathways reported in the literature into a
traceable reference dataset for evaluating trained retrosynthesis and synthesis
planning models. Its main purpose is to support comparison of single-step precursor
predictions and complete proposed routes against documented experimental syntheses.
The desktop website is an inspection interface for the benchmark data: researchers
can search reaction records, inspect connected pathways, and trace steps to sources.

**Status: candidate benchmark data under curation.** The repository contains route
records and provenance, but does not yet provide a frozen train/validation/test split,
an automated scoring suite, or a model leaderboard. Independent chemical review is
still required before records are admitted as benchmark reference truth.

[Reaction CSV](data/database/SynInsight_ABSynth_Dataset.csv) ·
[Provenance metadata](data/database/absynth_metadata.json) ·
[Evaluation design](docs/CURATION_AND_EVALUATION.md) ·
[Documentation](docs/README.md)

## Dataset

| Current route export | Count |
| --- | ---: |
| Source papers | 91 |
| Recorded paths and branches | 635 |
| Step occurrences (CSV rows) | 6,555 |
| Distinct operations represented in paths | 2,166 |

A CSV row represents one operation occurrence within a recorded path. Shared
operations repeat across paths; rows are not independent reaction examples. Paths
include fragments, partial syntheses and control branches, so 635 paths does not
mean 635 complete target syntheses or benchmark tasks.

The primary file is `data/database/SynInsight_ABSynth_Dataset.csv`, with an equivalent
TSV export. Its ABSynth-style layout contains these nine columns:

| Field | Meaning |
| --- | --- |
| `PathId` | Source-defined path identifier |
| `TargetName` | Recorded endpoint/path label; may describe a fragment or control |
| `Year`, `DOI`, `Author` | Literature metadata |
| `StepId` | Step identifier within the path |
| `RxnSMILES` | Recorded forward reaction, to be reversed for precursor prediction |
| `RxnName` | Reaction name, when recorded |
| `Conditions` | Recorded conditions serialized as text |

Missing values mean not recorded, not a negative observation. Reaction names are
blank in 6,409 rows and conditions in 215 rows. Do not infer missing chemistry from
these fields. The companion `absynth_metadata.json` links paths and steps to case
records, operation identifiers, source locators, yields, coverage and review state.
See [format and scope](docs/ABSYNTH_DATASET.md) for details.

## Intended evaluation workflow

1. **Select and freeze reference tasks.** Review target identity, stereochemistry,
   route coverage and source agreement. Separate complete routes from partial,
   fragment and control tasks; publish inclusion criteria and exclusion counts.
2. **Prevent train/test leakage.** Group shared operations and overlapping paths,
   and split by source paper and target family as appropriate. Audit overlap with
   model training data and publish the split manifest and normalization rules.
3. **Run trained models under fixed conditions.** Give each model the same target,
   starting-material stock, search budget and allowed inputs. Keep literature routes,
   conditions and source metadata out of model inputs unless explicitly part of the task.
4. **Report complementary metrics.** For single-step prediction, report top-k
   precursor recovery and valid-output rate. For route planning, report stock-closed
   target coverage, reference transformation/route recovery, search cost and route
   length under the same protocol. Report failures against the full frozen task set.
5. **Review route quality.** A route different from the literature may still be
   chemically sound. Assess plausibility, stereochemistry and strategic value
   separately from exact reference recovery; stock closure alone is not validation.

This is the proposed evaluation design, not a claim that these metrics are already
implemented or that any model has been scored. Detailed admission and reporting
rules are in [Curation and evaluation](docs/CURATION_AND_EVALUATION.md).

## Browse and run locally

The desktop website provides reaction search, filters, page jumps, step conditions
and evidence, an interactive complete-recorded-route tree, and CSV/SVG downloads.
It displays the available record without inventing missing upstream steps.

```sh
python -m http.server 8765
```

Open http://localhost:8765/ from the repository root. Use HTTP rather than opening
`index.html` directly so the browser can load CSV and JSON resources.

To regenerate the static site and validate the data presentation:

```sh
python -m pip install -r requirements-web.txt -r requirements-test.txt
python scripts/build_web.py
python -m pytest tests/test_release.py tests/test_web.py
node tests/test_route_tree.cjs
```

These checks validate export contracts, links and route rendering; they do not
establish chemical correctness or model performance. Publishing instructions are
in [Deployment](docs/DEPLOYMENT.md).

## Repository guide

| Location | Purpose |
| --- | --- |
| `data/database/` | Main reaction table, provenance and database exports |
| `data/routes/` | Per-paper pathway records and source evidence locators |
| `index.html`, `route.html`, `reader.html` | Dataset browser, route viewer and document reader |
| `assets/`, `pages/` | Website resources and generated document pages |
| `scripts/`, `tests/` | Build, export and validation tools |
| `docs/` | Evaluation design, data reference and maintenance documentation |

The original discovery snapshot (`data/papers.*`, `data/targets.*`, `data/release.json`
and `structures/`) is retained for provenance. Its population and counts are separate
from the current stepwise route export; it is not a ready-made benchmark test split.
Historical extraction notes are indexed separately in [Documentation](docs/README.md).

## Contributing, citation and licenses

Corrections should identify the affected paper, path or operation and supply a
source locator. See [CONTRIBUTING.md](CONTRIBUTING.md). Publisher PDFs, supporting
information files, private model logs and reviewer identities are excluded from
the public repository.

Cite the dataset version using [CITATION.cff](CITATION.cff), and record the exact
commit, task manifest and evaluation protocol used in an experiment. The current
candidate release has no archived dataset DOI. Data: [CC BY 4.0](LICENSE-DATA).
Website and export code: [MIT](LICENSE-CODE).
