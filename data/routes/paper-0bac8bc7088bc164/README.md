# Glabridin source-bound candidate dataset

Source: Asymmetric Total Synthesis of Glabridin, DOI 10.1021/acs.joc.6c00242.

Reproduce from the repository root with `.venv/Scripts/python.exe scripts/extract_glabridin_case.py`. The script requires the three archived source hashes and aborts if any source changes.

The 17 numbered molecules cover Schemes 3-5. There are 13 main-network events, one separate selected Table 1 optimization, 16 structure-supported operation groups, and 3 routes (two fragments and one full convergent DAG). The full route has start_labels [a1,b1]; its molecule sequence is a topological inventory, not a linear reaction path.

All molecular and participant SMILES are RDKit canonical isomeric SMILES. No unspecified stereochemistry, atom mapping, or missing elementary intermediate is invented. Compound 6 remains an unspecified-C9 diastereomeric mixture; 7 is not isolated. Combined yields stay attached to the reported event boundary.

Main article PDF p3 was rendered with Poppler and visually compared with generated structures; experimental PDF pp5-7 and SI S11/S15 were also visually checked. Source PDFs are not redistributed. Six source HRMS formula checks, source page/hash binding, JSON Schema, CIP, canonical SMILES, convergent topology, JSON/CSV/SDF round trips and output checksums pass. The Atlas database importer accepts this dataset. These checks are not independent expert admission.
