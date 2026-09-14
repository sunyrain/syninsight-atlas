# Native embedded chemical structure extraction

`scripts/extract_embedded_structures.py` reads native ChemDraw objects from the
locally archived Word supporting information. It detects OOXML by package contents,
including `.zip` files that are actually DOCX documents. It does not perform OCR or
infer reaction routes.

Install and reproduce from the repository root:

```powershell
.venv/Scripts/python.exe -m pip install -r requirements-embedded.txt
.venv/Scripts/python.exe scripts/extract_embedded_structures.py
```

`--archive-root` accepts the folder containing `paper-*` source packages, independently
of the repository location. `--inventory` accepts the batch inventory JSON. Optional
repeated `--paper-id` arguments restrict the run; they never bypass the inventory
policy. Only entries with `detail_policy=allowed` are opened for extraction.

Converter revision 4 reads native CDX with RDKit 2026.03.6 and its bundled ChemDraw extension (Chem.HasChemDrawCDXSupport()). It retains the original fragment object ID and checks that conversion has not lost explicitly drawn heavy atoms. Unspecified nodes carrying text (including Bpin and annotation numbers) and unsupported non-tetrahedral stereo are rejected for source review. No graph or valence repair is applied. Open Babel and PyCDXML are not runtime dependencies of this path.

The previous Open Babel conversion was found to truncate some large-ID source structures to methane or disconnected atoms. A canonical SMILES roundtrip cannot detect this loss. All current embedded candidates have been regenerated with the native RDKit reader. Query structures, unexpanded aliases, ambiguous fragment IDs and empty conversions are rejected. Formula checks are graph consistency checks, not source HRMS verification.

extract_embedded_structures.py still keeps molecule roles and publication labels unknown. The separate extract_native_reactions.py reads explicit CDX ReactionStep object references, never geometric arrow proximity. Source document hashes, CDX hashes, fragment IDs and reaction IDs remain attached to every endpoint. Binary Word .doc sources are supported by the reaction reader through OLE CONTENTS streams; text indexing uses the Word CLX piece table.

For the combined build:

    .venv/Scripts/python.exe scripts/batch_extract_atlas.py --extract-native --extract-native-reactions

See the [database documentation](ATLAS_DATABASE.md) and [native endpoint browser](../data/database/native_reactions.html). AND/OR stereo groups are retained separately in enhanced_stereo_cxsmiles where present; ordinary canonical SMILES alone cannot encode all mixture/relative-stereo semantics.

Public output is `data/extraction/embedded_structures/paper-*.json` plus `summary.json`:

| Field | Meaning |
|---|---|
| `sources` | Original attachment hash, source ID, document format and logical archive path; no invented page count |
| `structures` | Candidate ID, canonical isomeric SMILES, formula, charge, stereocenters, source atom maps and provenance |
| `source_references` | Attachment SHA256, OOXML embedding member, OLE stream, embedded-object/CDX hashes, native molecule index and paragraph locator |
| `paper_label`, `role`, `reaction_id` | Null; no source numbering, chemical role or endpoint assignment is inferred |
| `native_objects` | Every native object occurrence, parser status and count of accepted/rejected graphs |
| `rejected_objects` | Unresolved/query atoms, nonchemical OLE objects and conversion failures, tied to original object locators |
| `validation` | Canonical, formula, no-query, source-hash binding, no-inferred-label and JSON roundtrip checks |

Native molecule indices refer to the native RDKit converter output inside that
CDX object. They are not publication compound numbers. Nearby Word text stays only
in `.local/extraction/embedded_structures/private_document_contexts.json`; public
records contain paragraph positions without experimental text. Original CDX
intermediates and the conversion cache also stay in `.local`.

These graphs form a separate candidate collection from name-parsed compounds and
curated route datasets. They may depict substrates, products, reagents, generic
examples or comparison structures. A parser-valid structure is not automatically a
route intermediate, and no candidate has expert admission or complete-route status.
