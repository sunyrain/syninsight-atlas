# Ineleganolide SI route extraction

Case: `paper-77cc3e5bcb3be4ba`, *Asymmetric Total Synthesis of (+)-Ineleganolide*.

The local source is `supporting_information/si-001.docx`, SHA256
`9c776a9a888937f07252254df464d12c299c7b933c4414ae6815604c2dcd5a44`.
The main article is absent. This case covers the available SI network and does
not claim complete coverage of the article or independent expert admission.

The [case report](../data/routes/paper-77cc3e5bcb3be4ba/report.html) contains:

- 27 molecular structures with canonical isomeric SMILES and SDF depictions;
- 21 preparation events: 5 attributed reference preparations and 16 SI events;
- 4 paths: the main sequence from 15, a path including the referenced preparation
  of 15, the one-pot alternative from 22 to 23, and the characterization branch
  from 27 to 28;
- 14 source HRMS comparisons, all agreeing with the neutral molecular formula.

Each structure and event points to the original attachment hash, a specific Word
embedding member, the CDX hash and a paragraph locator. Native fragment object IDs
are kept separately from publication compound labels. No PDF page is invented.

## Interpretation boundaries

Compound 30 is a bracketed mechanistic intermediate. It is stored as a drawn
structure but is not counted as a separate isolated preparation. The source names
organozinc reagent 16 without establishing a unique solution-species representation;
its participant SMILES remains null.

The native parser misread Bpin labels as carbon atoms. Structures 20 and the final
boronate were transcribed from the inspected source drawing with explicit pinacol
boronate groups. The source triflate 19 required removal of a spurious square-planar
sulfur tag; source-drawn carbon stereochemistry was retained. These corrections
are recorded as source transcription, not silent generic graph repair.

The source reports compound 29 with an M+H label but a sodium-containing ion
formula and mass. The conflicting adduct annotation remains in `hrms_checks.json`.
The scheme and procedure also disagree on the alcohol solvent for 27 to 29;
the discrepancy is retained in `issues`, without choosing an unsupported value.

Raw ChemDraw ReactionStep lists sometimes include reagents and mechanistic
intermediates among products. This case assigns roles from the inspected figures
and preparation paragraphs, while the separate native layer retains raw associations.

## Reproduction

From the repository root, using the pinned extraction environment:

```powershell
.venv/Scripts/python.exe scripts/extract_ineleganolide_case.py
.venv/Scripts/python.exe scripts/batch_extract_atlas.py --extract-native --extract-native-reactions
.venv/Scripts/python.exe scripts/validate_atlas_database.py
```

The adapter rejects a changed source hash. Tests cover boronate expansion, role
assignment, the alternative path, the bracketed intermediate, source conflicts and
missing-article coverage. SDF roundtrips preserve the canonical SMILES of all 27
structures. These checks establish data consistency, not independent chemical truth.
