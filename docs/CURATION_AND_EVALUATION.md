# Benchmark curation and evaluation

## Scope and current status

The objective is a literature-derived reference benchmark for trained machine-learning
retrosynthesis models, covering single-step precursor prediction and multi-step
planning. Current exports are candidate records. Frozen task splits, scoring tools
and published model results are not yet provided. The protocol below describes the
requirements for a future reproducible evaluation, not completed evaluations.

## Reference admission

Review paper scope, exact target identity/stereochemistry and source-bound route
connectivity separately. Two independent experts should accept the same normalized
record; disagreements require adjudication. Automated SMILES validation and connected
diagrams are technical checks, not admission of literature truth.

A complete-route task requires an admitted target and a source-supported route with
an explicit starting boundary. Partial routes, fragments and control branches must
be labelled and evaluated separately. Preserve uncertain records and document all
exclusions without treating them as model failures before task admission.

## Splits and model inputs

Freeze a versioned task manifest containing task IDs, paper DOI, target structures,
reference operation IDs, coverage, review state and split assignment. Shared steps
and overlapping routes must remain in the same split. Group by paper and inspect
cross-paper target-family and reaction overlap. Document normalization, stereochemical
handling and duplicate removal before deriving examples from the CSV.

Audit benchmark overlap with training corpora, including literature-derived data.
If training provenance is unavailable, report that limitation. A random CSV-row split
is unsuitable because the same operation can appear in multiple paths.

For ordinary retrosynthesis, the input is the target structure plus declared stock
and task constraints. Reference steps, conditions, DOI and other answer-bearing
metadata are evaluation-only. Declare any task that supplies additional information.

## Evaluation and reporting

| Task | Proposed measurements | Required controls |
| --- | --- | --- |
| Single-step prediction | Top-k precursor-set recovery, valid-output rate | Fixed k; molecule normalization, atom-mapping and stereo policy; order-independent precursor matching |
| Multi-step planning | Stock-closed target fraction, reference transformation and route recovery | Fixed stock version, search budget, stopping rules and matching definition |
| Efficiency | Wall time, model calls, expanded nodes, route length | Comparable hardware and budgets; report successful and failed runs |
| Chemical quality | Plausibility, selectivity, convergence and strategic value | Independent blinded review, distinct from reference matching |

Publish numerators and denominators, per-task outcomes, seeds, model/checkpoint
versions, stock and split hashes, timeouts and exclusions. Do not count a fragment
path as a solved total synthesis. Do not count repeated CSV rows as independent
benchmark successes. Define how alternative precursors, reagents and combined
operations are handled before reporting reference recovery.

Literature agreement measures reference recovery; it does not prove that a different
route is wrong. Stock closure and short routes likewise do not prove feasibility.
At least three synthetic chemists should review intrinsic route value while blinded
to paper and model identity, before seeing literature similarity. Review includes
key transformations, stereochemistry, convergence/economy and risk, with an explicit
pursue/redesign/stop recommendation. This expert review is a proposed protocol.

## Related documentation

- [Reaction export format](ABSYNTH_DATASET.md)
- [Database model](ATLAS_DATABASE.md)
- [Documentation index](README.md)
