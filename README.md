# SynInsight Atlas

**An evidence-grounded benchmark of strategic reasoning in recent total synthesis.**

SynInsight Atlas is a versioned data and browsing layer derived from the AutoPlanner
recent-total-synthesis curation workspace. It separates four claims that are often
collapsed in retrosynthesis benchmarks:

1. a paper and target were discovered;
2. a candidate molecular structure was transcribed and passes cheminformatics checks;
3. route-defining evidence was located in the literature;
4. independent chemists admitted the exact structure and route as benchmark truth.

The hosted browser is available at
<https://sunyrain.github.io/syninsight-atlas/>.

## Current release

`v0.1.0-candidate.1` is a **candidate curation release**, not a finished benchmark:

- 133 candidate papers;
- 253 target slots;
- 131 acquired source packages recorded in the private curation workspace;
- 145 RDKit-valid structure candidates;
- 242 targets with automatically located route-evidence leads;
- 0 human-admitted structures, 0 human-admitted routes, and 0 runnable targets.

Those zeroes are deliberate. Machine extraction, source availability, valid SMILES,
and route connectivity do not grant literature-truth admission.

## Desktop route browser update

The original discovery snapshot remains intact. The desktop website adds a separate
source-bound route dataset: **6,555 step occurrences, 635 paths/branches, and 91
source papers**. These are candidate records pending independent chemical review;
path occurrences must not be mistaken for unique experimental operations.

- `data/database/SynInsight_ABSynth_Dataset.csv`: main nine-column reaction table.
- `data/routes/`: curated candidate cases, structures and source locators.
- `route.html` and `assets/route-overviews/`: connected vector pathways with desktop
  pan/zoom, step navigation, highlighting and shareable step links.
- `reader.html` and `pages/`: readable data/document views.
- `scripts/build_web.py` and `scripts/validate_web.py`: website build and checks.
- `tests/`: original release contract plus website integration checks.

The site remains a static website served from the repository root with `.nojekyll`.
See [deployment and update instructions](docs/DEPLOYMENT.md) and the
[repository integration notes](docs/REPOSITORY_UPDATE.md).

To rebuild only the website (without re-exporting the original snapshot):

```sh
python -m pip install -r requirements-web.txt
python scripts/build_web.py
python scripts/validate_web.py
python scripts/validate_release.py
```

## Repository contents

- `data/papers.json` and `data/papers.csv`: paper-level browser and analysis tables;
- `data/targets.json` and `data/targets.csv`: target-, structure-, route-lead-, and
  review-state records;
- `data/release.json`: release provenance and redistribution boundary;
- `data/schema.json`: machine-readable field contract;
- `structures/`: SVG depictions derived from candidate SMILES;
- `index.html` and `assets/`: dependency-free data browser;
- `scripts/export_from_autoplanner.py`: deterministic snapshot exporter;
- `docs/`: data dictionary, curation model, and release roadmap.

## Public data boundary

This repository includes bibliographic metadata, candidate target identities,
candidate isomeric SMILES, derived depictions, source locators/hashes, aggregate
route-lead counts, and human-admission state. It excludes publisher PDFs, HTML/XML,
supporting information, verbatim article passages, local cache paths, browser state,
model logs, prompts, and private reviewer identities.

DOI links direct users to the original publications. Access and reuse of article or
supporting-information content remain governed by the publisher and source license.

## Rebuild a snapshot

With AutoPlanner checked out as a sibling directory and RDKit available:

```powershell
python scripts/export_from_autoplanner.py
```

Preview locally through HTTP rather than opening `index.html` directly:

```powershell
python -m http.server 8765
```

Then open <http://localhost:8765/>.

## Citation and release policy

Use the metadata in `CITATION.cff`. A DOI will be added after the first frozen,
human-reviewed release is archived in a research-data repository. Candidate releases
remain versioned and must not be cited as an experimentally validated reaction corpus.

Data are released under CC BY 4.0; site and export code are released under MIT.
