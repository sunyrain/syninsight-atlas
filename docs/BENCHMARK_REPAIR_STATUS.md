# SynInsight Atlas repair status

Updated 2026-10-04 after checking source changes, database mirrors, rebuilt tasks and
the scoring entry points. **The first targeted repair pass and executable candidate
bank are complete; full chemical reference review is not.** There are 27 corrected
operations in five papers. The candidate repair is published on the
[`benchmark-repair-20261004` branch](https://github.com/sunyrain/syninsight-atlas/tree/benchmark-repair-20261004).
Prior experiment scores remain unchanged; the branch does not claim chemical reference admission.

The repair starts from published commit `a9c781035b6522ed914addb94b11f2fda0f12db2`,
which is also the source used in the Retraxis experiments. The older local checkout
was not used as the repair baseline.

## Corrections applied

| Paper / operation | Source-grounded correction |
| --- | --- |
| Hinckdentine A, A02.1 | 80 °C; 30 min after substrate addition. The approximately 2 h acid/P2O5 preparation is not reaction duration. |
| Hinckdentine A, A03.1 | Formic acid medium, 90 °C, 1 h. The reported 93% belongs to 33 → 34 → 35, not independently to 34 → 35. |
| Exiguamines, F01.1 | SI p25 specifies benzene, nitroethylene in toluene, addition at 0 °C then room temperature for 24 h. |
| Palhinines, A01.1 / ent-A01.1 | Each arrow is two referenced steps at 69% combined yield; neither is a single operation with separately measured yield. |
| Macrocephadiolide A, T02.1 | Room-temperature overnight peroxide rearrangement; no added reagent specified. Scheme 89% and prose “quantitatively” remain an unresolved source discrepancy. |
| Ineleganolide, E01.1–E21.1 | Recover key conditions for 21 operations from the archived SI DOCX experimental paragraphs; resolve 20 previously empty condition records. Identify 16 single operations and five two-stage operations. Preserve the E15.1 solvent disagreement, E17.1 reaction environment and coproduct, and E14.1 workup distinction. |

All 27 operations are updated in source JSON, per-paper JSON/CSV, SQLite
operation/event records and the path CSV/ABSynth exports. The correction ledger is
[`data/curation/repairs_20261004.json`](../data/curation/repairs_20261004.json).
Source figures or experimental paragraphs were checked locally; this is not
independent human review. Structures and reaction endpoints were not changed by
this repair pass. Five papers with targeted edits does not mean five fully audited papers.

Relative to the published baseline, completely empty structured-condition records
decreased **71 → 48** (23 recovered), empty CSV condition cells **215 → 152** (63
path occurrences), and unresolved operation segmentation **503 → 482**. Repeated
CSV rows are not additional independent repairs. The earlier status of six corrected
operations, 68 gaps and 1,238 single-step questions preceded the Ineleganolide update.

This closeout also fixes one export omission: evaluation records now retain source
condition conflicts, yield claims, operation scope/stage count, reaction environment,
coproduct observations and workup notes when present. For example, Ineleganolide
E15.1 explicitly retains the scheme's MeOH versus the experimental paragraph's
EtOH/toluene. This transfers evidence; it does not adjudicate the disagreement.
Model inputs and candidate selection are unchanged.

## Candidate bank and remaining work

| Item | Current count |
| --- | ---: |
| Source papers | 91 |
| Molecular records | 2,887 |
| Source operations | 2,315 |
| Recorded paths, including controls and fragments | 635 |
| Path CSV occurrences / distinct represented operations | 6,555 / 2,166 |
| Operations absent from the path CSV, now retained in the operation bank | 149 |
| Unique single-step candidate product questions | 1,254 |
| Unique multistep candidate endpoints | 228 |
| Source paths represented by those multistep candidates | 300 |
| Multistep endpoints themselves in Repaired ZINC | 14 |
| Multistep endpoints with at least one literally stock-closed reference path | 68 |
| Operations still without structured conditions | 48 |
| Independently admitted benchmark questions | 0 |

The 228 endpoints include intermediates and analogues. Neither that count nor 635
recorded paths means complete natural-product syntheses. Of all 635 paths, 235 have
literal closure under the current stock; this count includes fragments and controls.
Closure only describes the listed starting boundary, not chemical feasibility.

| Candidate split | Single-step products | Multistep endpoints | Papers |
| --- | ---: | ---: | ---: |
| Development | 103 | 33 | 14 |
| Validation | 149 | 30 | 13 |
| Test | 1,002 | 165 | 64 |

These are grouped candidate splits, not verified temporal holdouts or scaffold-disjoint splits.

## Remaining source work

| Source | Empty condition records | Required work |
| --- | ---: | --- |
| Bisnicalaterine alkaloids | 25 | Expand the graph-only transcription into source-supported operations and conditions. |
| Ascidiathiazones A/B and analogues | 21 | Expand the graph-only transcription into source-supported operations and conditions. |
| Palhinines | 2 | Retrieve the cited upstream procedures before splitting the two-step arrows. |

These 48 records are missing structured conditions, not 48 proven chemical errors.
Conversely, a nonempty condition field does not establish complete experimental
specification. Recovering an agent name alone is not a finished chemical audit.

Segmentation also needs review: 482 operation records have no resolved stage count;
255 are already recorded as multistage operations. The single-step task builder keeps
them out of the restricted single-operation track. Review racemic representatives,
uncertain stereo and alternative/negative-control branches before formal task admission.
Preserve unresolved source disagreements, including Macrocephadiolide A's yield and
Ineleganolide's E15.1 solvent. The machine review queue is not an exhaustive list of
all chemical/source uncertainties.

Across the full route bank, 161 paths carry paper-level unresolved-source events and
eight contain off-target operations; their scope needs inspection. In the multistep
candidate set, 54 endpoints have at least one reference carrying unresolved-source
events. These annotations do not prove every affected path is invalid, but prevent
calling the whole pool an admitted full-synthesis test set.

The current automated checks find no invalid source SMILES, formula mismatches,
reaction/label endpoint disagreements, broken source hashes/page bounds or missing
route target production. These technical checks cannot verify every drawing, condition
or chemical interpretation. Full paper-by-paper expert/source re-admission remains
unfinished.

## Verification and closeout decision

The source JSON, per-paper steps and SQLite records agree for all 27 repairs. The
existing seven benchmark tests pass, including stereo-sensitive matching, missing
prediction denominators, input/answer separation and disconnected/unclosed routes.
The release and website tests also pass (two tests), and the route-tree check covers
635 paths and 6,555 step occurrences in both display modes.

Before the metadata export fix, a clean compilation with the frozen stock reproduced
all 11 bank files byte for byte. After the fix, the bank was rebuilt and both input
files remain byte-identical; task counts and split assignments are unchanged. Source
qualifications are present in the evaluator records. CLI canaries using known
reference answers pass single-step matching and multistep closure/reference recovery;
unsubmitted tasks remain in the denominator. These are software checks, not model results.

The scorer implements strict/relaxed precursor recovery, route connectivity, stock
closure, reference-operation recovery and condition-field presence. It does not
judge condition correctness, chemical plausibility or innovation. Those judgments
still require the separate chemical review process in the protocol.

The benchmark uses the full Repaired ZINC list with no additions or target-dependent
filters. Old Retraxis experiments retain their original frozen inputs and inventories;
changing their reference files or scores requires a separately reported reevaluation.

**Decision: close the first targeted repair pass; use the candidate bank for internal
pipeline trials.** Formal benchmark performance claims remain pending source/chemical
admission. Next work is bounded to the three-paper condition backlog, operation and
stereo review, and selection of full-target tasks. The zero admission count refers
to this newly compiled reference bank, not to prior expert reviews of generated routes.
