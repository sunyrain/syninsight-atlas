# Data dictionary

## Release units

`paper_id` identifies one provider-reconciled paper record. `article_family_id`
groups parallel editions or duplicate index records. `target_id` identifies one
reported target slot; paper counts and target counts must never be interchanged.

## `data/papers.json`

Each row contains public bibliographic metadata, cohort membership, target count,
candidate-evidence counts, source-package completeness, and human paper-review state.
Source-package fields describe the curation workspace but do not expose source files.

## `data/targets.json`

- `candidate_structure`: non-admitting structure transcription state, canonical
  isomeric SMILES when RDKit-valid, derived SVG path, source locator/hash, and note;
- `route_evidence_lead`: non-admitting extraction state, passage count, and source
  locators; article text is intentionally excluded;
- `source_package`: availability and completeness without local paths;
- `human_review`: paper, structure, route, and runnable states;
- `formal_benchmark_eligible`: true only after the parent paper, exact structure, and
  literature route/key step pass the declared human-admission contract.

## Candidate structure states

- `exact_source_structure_candidate`: the automated transcription appears complete
  and passes RDKit, but has not been independently admitted;
- `partial_stereo_candidate`: connectivity is useful for review, while one or more
  stereochemical claims require resolution;
- `unresolved`: no reliable source-concordant SMILES candidate is available.

No candidate state is a synonym for chemical truth.
