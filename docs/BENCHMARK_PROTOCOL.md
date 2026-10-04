# SynInsight Atlas candidate benchmark protocol

This branch provides an executable **candidate** benchmark. It does not certify the
chemistry through automated parsing or source transcription. No independent expert
reference admission is claimed. Existing Retraxis experiment results are unchanged.

## Units and tracks

| Artifact | Unit | Treatment |
| --- | --- | --- |
| `evaluation_only/operation_bank.jsonl` | One source operation, keyed by paper and step | Includes operations absent from the path CSV; conditions and source locators retained |
| `inputs/single_step.jsonl` | One unique product with one or more recorded precursor sets | Restricted to declared single operations with one product identity, valid endpoints and nonzero/nonfailed outcomes |
| `inputs/multistep.jsonl` | One unique endpoint from the listed productive route types | Controls excluded; endpoints still include intermediates and analogues, not just final natural products |
| `evaluation_only/route_bank.jsonl` | One source-defined path | Preserves fragments, controls, start boundaries, side branches and route coverage |
| `evaluation_only/review_queue.jsonl` | One machine-detected unresolved field or inconsistency | Source interpretation required; absence is not a negative chemical result |

The path CSV contains repeated operation occurrences. Never randomly split its rows.
Single operations, multistage operations, aggregate literature sequences, physical
separations and unresolved graph-only connections are different units. In particular,
an arrow marked “two steps” is not an elementary single-step answer. A combined yield
belongs to its entire stated sequence, not automatically to the last arrow.

Evaluator records retain source disagreements and qualifications when recorded,
including condition conflicts, competing yield claims, reaction environment,
coproduct observations and workup distinctions. Retaining a disputed value is not
adjudication. These fields remain outside the model input files.

The current single-step track is intentionally restricted: operations with unknown
segmentation, multiple named products or an explicit failed/zero-yield outcome stay
in the operation bank. This is an inclusion rule, not a declaration that their
chemistry is invalid. An additional endpoint-prediction track can evaluate them after
the operation scope is resolved; do not silently pool it with single-step results.

The current multistep candidates require subsequent target/coverage review before a
formal full-synthesis benchmark is selected. A route to a fragment is not a solved
total synthesis, even if its terminal structure can be produced from stock.

## Inventory and inputs

Use only the entire ChemEnzy **Repaired ZINC** list. There are 10,320,697 raw rows and
10,320,664 unique entries under RDKit 2023.09.6 canonicalization. `data/benchmark/stock.json`
records the source and canonical-index hashes. No eMolecules additions, manual
supplements, advanced-intermediate filters or target-dependent exclusions are merged.
Whole ion-pair/salt identities are queried, rather than pretending each disconnected
SMILES component is an independently purchasable material.

Each model question contains only the opaque task ID, target SMILES, track, candidate
limit and inventory ID where relevant. Do not pass `evaluation_only`, `splits.json`,
literature DOI, paper labels, reaction names, source conditions or reference graphs to
generation. Those files are for the evaluator. File separation is not a claim that
the underlying public literature was absent from model training.

Supply at most **three ranked candidates** per target. Rank them without access to
the reference answer or evaluation judge. Freeze model, prompt, inventory, generation
budget, candidate-selection rule and all failures before scoring. All methods use
the same target list and inventory; token/model-call budgets and conventional search
limits must be reported separately rather than called equivalent computational cost.

## Grouping and temporal claims

The compiler joins paper records sharing a declared article-family key, a product
structure or reaction identity with stereochemistry removed. Components are assigned
deterministically toward 15% development, 15% validation and 70% test at paper level.
Common reactants alone do not join papers. All exact product/reaction duplicates and
shared paths remain together; products are deduplicated into task questions.

These are **candidate grouped splits**, not certified scaffold-family disjointness
or temporal holdouts. A temporal evaluation additionally needs an actual publication
date and a documented training cutoff for each model/checkpoint. Unknown cutoffs
remain unknown. Human review must also handle source racemates encoded as representative
enantiomers, unspecified stereocentres, mixtures and P/M helicity that ordinary SMILES
cannot express; a strict SMILES match does not resolve those source limitations.

## Scoring

Single-step scoring reports strict top-1/top-3 precursor-component multiset recovery.
Atom maps and component ordering are ignored; stereo, isotope, charge, salt fragments
and tautomer identities are preserved. A connectivity-only diagnostic removes stereo
and isotopes, and is never substituted for the primary strict score. All recorded
alternative precursor sets admitted to this candidate track are acceptable references.

Multistep predictions contain an ordered sequence of forward operations. Every
operation lists full reactant/product identities and a structured conditions object.
The scorer records target production, time-resolved connectivity, unrelated operations,
unresolved stock leaves, condition-field coverage, and reference-operation recall and
precision. Reference-operation multiset equality is **not** claimed to be a graph-
isomorphism route match. Multistage/aggregate granularity affects recovery and remains
visible in the reference operation bank.

Stock closure requires a produced target, connected operations and all external
reactants in the frozen inventory. A listed intermediate is supplied by an earlier
operation, not by a later occurrence with the same identity. Zero-operation purchase
of the target is a separate triviality diagnostic. Targets already in stock are
reported separately, with an additional nontrivial-target denominator.

The compiler's `reference_stock_closed` is literal closure of the listed source path
from its external starts. It does not prune known advanced intermediates from the
literature path, infer absent precursor preparations or turn a partial source route
into a complete one. It is not a reference-route feasibility metric.

Missing predictions, parse failures and timeouts remain in each requested split's
denominator. Invalid records in the reference itself must instead be documented and
removed consistently for every method in a new task version. Report both numerator
and denominator, and analyze target-level rather than treating three routes from the
same target as three independent samples.

## Chemical evaluation and expert form

Structural validity, stock closure and text presence do not establish that a reaction
will occur. The deterministic scorer therefore emits `chemical_plausibility: not_assessed`.
Reference recovery is a separate axis; a credible alternative need not reproduce the
published route. A literature route is not automatically marked correct by an AI judge.

Use the following blinded review order for reference and model routes alike:

1. Verify exact target identity, stereochemistry, start boundary and route connectivity.
2. Record closure. An unclosed route does not pass complete-route evaluation; retain
   its partial chemistry as a diagnostic.
3. Assess whether key transformations have sufficient and chemically compatible
   conditions. Missing necessary conditions or definitely incompatible conditions
   fail the executable-route screen. An agent-free thermal/photochemical rearrangement
   can still have well-defined conditions. “Not reported in the source” is not itself
   proof of impossible chemistry.
4. For every judgment identify the operation, reason and evidence. Distinguish
   clearly wrong, unresolved and plausible; do not reward brevity by interpreting
   omitted selectivity, workup or stereocontrol as correct.
5. Only after the preceding screens assess strategic value, convergence, unnecessary
   protecting groups, isolations, economy and innovation. Report these separately
   from reference similarity and closure.

Two independent reference reviewers may adjudicate admission, with disagreements
logged. Expert review of generated routes and reference-dataset admission are different
tasks; existing model-route scores cannot be repurposed as proof of source accuracy.
LLM judges receive the same anonymized information across methods, and their
conditions/feasibility judgments are compared with experts, not used as ground truth.

## Reproducible commands and prediction formats

Use Python 3.12 with RDKit 2023.09.6, BeautifulSoup4 and Markdown. Set `STOCK_INDEX` to
the frozen canonical SQLite index; the compiler and multistep scorer verify its hash.
Use a separate benchmark environment: the website requirements pin a newer RDKit
and must not replace the version used to canonicalize the frozen stock. In a fresh
environment, install `rdkit==2023.9.6`, `beautifulsoup4` and `Markdown` before the
commands below. The version string reported by RDKit is `2023.09.6`.

```powershell
python scripts/repair_source_records.py
python scripts/build_benchmark.py --stock-index $env:STOCK_INDEX
python -m unittest discover -s tests -p test_benchmark.py -v
python scripts/score_benchmark.py --track single_step --split test --predictions predictions.jsonl --output score.json
python scripts/score_benchmark.py --track multistep --split test --stock-index $env:STOCK_INDEX --predictions routes.jsonl --output route_score.json
```

Single-step prediction (the task ID must come from the input file):

```json
{"task_id":"single_step-...","candidates":[{"precursor_smiles":["CCO"]}]}
```

Multistep prediction schema (illustrative shapes only, not experimental chemistry):

```json
{"task_id":"multistep-...","candidates":[{"target_smiles":"CC=O","steps":[{"reactants":["CCO"],"products":["CC=O"],"conditions":{"agents":["reported reagent"],"temperature":"reported temperature"}}]}]}
```

Source PDFs and page images remain outside the public repository. Public factual
corrections include source hashes, page/section locators and before/after field values.
No model generation or paid LLM judging is triggered by these commands.
