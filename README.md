# SynInsight Atlas

**An evidence-grounded dataset and desktop browser for strategic reasoning in recent total synthesis.**

SynInsight Atlas is a versioned data and browsing layer derived from the AutoPlanner
recent-total-synthesis curation workspace. It connects candidate targets and
stepwise synthesis records to their literature evidence, with searchable reaction
tables and connected pathway diagrams.

The project separates four claims that are often collapsed in retrosynthesis benchmarks:

1. A paper and target were discovered.
2. A candidate structure was transcribed and passes cheminformatics checks.
3. Route-defining evidence was located in the literature.
4. Independent chemists admitted the exact structure and route as benchmark truth.

**Current records are candidates pending independent chemical review.** Valid SMILES,
connected diagrams and source locators do not establish literature-truth admission.

[Project website](https://sunyrain.github.io/syninsight-atlas/) ·
[Reaction CSV](data/database/SynInsight_ABSynth_Dataset.csv) ·
[Dataset metadata](data/database/absynth_metadata.json) ·
[Deployment guide](docs/DEPLOYMENT.md)

## Data coverage

### Stepwise route dataset

The current route-browser export contains:

| Measure | Count | Meaning |
| --- | ---: | --- |
| Source papers | 91 | Papers represented in the route export |
| Paths and branches | 635 | Source-defined paths, including partial and control branches |
| Step occurrences | 6,555 | One row per operation occurrence within a path |
| Distinct operations in paths | 2,166 | Shared operations counted once across the exported paths |

A shared operation can occur in several paths and therefore appear in several CSV
rows. A path is not necessarily a complete total synthesis. Coverage, review state,
source compound labels and evidence locators are retained in the accompanying
metadata and case reports.

### Original discovery snapshot

The original `v0.1.0-candidate.1` discovery release remains a separate data layer:

- 133 candidate papers and 253 target slots;
- 131 acquired source packages recorded in the private curation workspace;
- 145 RDKit-valid structure candidates;
- 242 targets with automatically located route-evidence leads;
- 0 human-admitted structures, 0 human-admitted routes and 0 runnable targets.

These counts describe the original discovery snapshot, not the denominator of the
stepwise route export. See [release provenance](data/release.json) and the
[data dictionary](docs/DATA_DICTIONARY.md).

## Explore the desktop website

The website is designed for desktop use and runs as a static site.

- **Find reactions:** search target/path names, DOI, author, SMILES or conditions;
  combine keywords with path and route-type filters.
- **Navigate results:** browse 20 records per page, jump directly to a page, and
  retain the current search and page when returning from a product view.
- **Inspect a step:** preview conditions, reported yield, operation identifiers and
  source locators; open the full detail dialog or case report for context.
- **Open a complete recorded pathway:** click a product/path name to see connected
  starting materials, intermediates, convergent branches and the target.
- **Explore the diagram:** drag to pan, zoom, enter full screen, or select a step to
  center and highlight it. Copy a link that includes the selected step.
- **Reuse the records:** copy reaction SMILES, export the filtered CSV, or download
  the pathway as a vector SVG.

The interactive canvas uses the [AutoPlanner-style route-tree renderer](docs/ROUTE_TREE_RENDERER.md): target on the left, recorded precursors branching to the right, with compact/full detail and horizontal/vertical layouts. The downloadable SVG remains a forward-reaction scheme.

Keyboard shortcuts: `/` focuses dataset search; when the pathway viewer has focus,
`+` and `−` zoom, `0` restores the whole-route view, and the Expand button enlarges the workspace.
`Esc` exits full screen. Scrolling zooms around the pointer, and double-clicking the canvas zooms in.

Pathway SVGs use a uniform chemical scale, monochrome structures, source compound
labels and conditions above reaction arrows. They show only the recorded pathway:
unreported upstream steps are not inferred. Chemical review and sizing for a
specific journal remain separate from rendering. See
[reaction figure documentation](docs/REACTION_FIGURES.md).

## Reaction CSV format

The main export is [SynInsight_ABSynth_Dataset.csv](data/database/SynInsight_ABSynth_Dataset.csv),
with a companion [TSV](data/database/SynInsight_ABSynth_Dataset.tsv). Its nine-column
layout follows the ABSynth-style reference format; the records come from this
repository's existing curated data, not from importing the reference dataset.

| Column | Description |
| --- | --- |
| `PathId` | Identifier of the source-defined path |
| `TargetName` | Existing route/endpoint label; may identify a fragment or control path |
| `Year` | Source publication year |
| `DOI` | Source publication DOI |
| `Author` | Author metadata retained from the source records |
| `StepId` | Step identifier within the exported path |
| `RxnSMILES` | Reaction SMILES from the recorded substrate/product structures |
| `RxnName` | Recorded reaction name, when available |
| `Conditions` | Recorded conditions serialized for the tabular export |

Blank values mean **not recorded**. `RxnName` is blank in 6,409 rows and `Conditions`
in 215 rows. The export does not fill gaps by guessing reaction classes or conditions.

[absynth_metadata.json](data/database/absynth_metadata.json) maps each path and step
to its case dataset, local operation/event identifiers, reported yield, structure
basis, coverage, review status and source references. Consult the case report for
mixture yields, combined preparations and unresolved source conflicts.

## Run locally

The generated website is included; viewing it requires no build dependencies.
From the repository root, serve it over HTTP:

```sh
python -m http.server 8765
```

Open [localhost:8765](http://localhost:8765/). Opening `index.html` directly with a
`file://` URL will not reliably load the JSON and CSV resources.

## Build and validate

To regenerate the website from the included data, use an environment with the
pinned dependencies:

```sh
python -m pip install -r requirements-web.txt
python scripts/build_web.py
python scripts/validate_web.py
python scripts/validate_release.py
```

The web build refreshes the CSV, vector pathway diagrams, document pages and
resource manifest. It does not re-export the original discovery snapshot from the
private AutoPlanner workspace.

To run both repository tests:

```sh
python -m pip install -r requirements-test.txt
python -m pytest tests/test_release.py tests/test_web.py
```

The original release test checks its data contract and checksums. The website test
checks page/resource links, route coverage, operation counts, connection endpoints
and diagram node bounds/overlap. These checks are not independent chemical review.

### Re-export the original discovery snapshot

The original exporter is retained. With AutoPlanner checked out as a sibling
directory and RDKit available:

```sh
python scripts/export_from_autoplanner.py
```

This separate workflow requires the upstream curation workspace; it is not needed
to preview or rebuild the included website.

## Repository contents

| Path | Purpose |
| --- | --- |
| `index.html` | Main dataset and discovery browser |
| `route.html` | Interactive connected-pathway viewer |
| `reader.html` | Data and document preview |
| `assets/` | Styles, interaction scripts, manifests and pathway SVGs |
| `data/database/` | Unified candidate database exports and main reaction CSV |
| `data/routes/` | Source-bound candidate cases, structures and evidence locators |
| `data/papers.*`, `data/targets.*` | Original discovery snapshot tables |
| `data/release.json`, `data/schema.json` | Original release provenance and field contract |
| `structures/` | Original candidate target depictions |
| `pages/` | Generated document and report pages |
| `scripts/` | Export, website generation and validation tools |
| `tests/` | Original release and website integration checks |
| `docs/` | Data model, curation, figure and deployment documentation |

## Deploy or update the website

The site uses repository-relative links and `.nojekyll`, with `index.html` at the
repository root. The existing GitHub Pages layout is retained. Follow the
[deployment guide](docs/DEPLOYMENT.md) to update an existing checkout and configure
its publishing source; see [integration notes](docs/REPOSITORY_UPDATE.md) for the
repository baseline and checksum correction.

The project website link above is the upstream address recorded in the original
release. A fork's published URL depends on its own GitHub Pages configuration.

## Public data boundary

This repository includes bibliographic metadata, candidate identities and
structures, source-bound step records, derived diagrams, source locators/hashes,
route coverage and human-admission state. It excludes publisher source PDFs,
HTML/XML and supporting-information files, verbatim article passages, local cache
paths, browser state, model logs, prompts and private reviewer identities.

The HTML reports and pages included here are generated presentations of the
candidate records. DOI links point to the original publications, whose access and
reuse remain governed by the publisher and source license.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and the
[curation and evaluation model](docs/CURATION_AND_EVALUATION.md). Corrections should
retain source locators and distinguish structure/route transcription from human
admission. The [release roadmap](docs/ROADMAP_TO_SCIENTIFIC_DATA.md) describes the
broader publication goals.

## Citation and license

Use the versioned metadata in [CITATION.cff](CITATION.cff). A dataset DOI is planned
for the first frozen, human-reviewed release archived in a research-data repository.
Candidate releases must not be cited as an experimentally validated reaction corpus.

- **Data:** [CC BY 4.0](LICENSE-DATA).
- **Website and export code:** [MIT](LICENSE-CODE).
