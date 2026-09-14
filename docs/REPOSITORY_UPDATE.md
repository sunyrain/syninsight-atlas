# Repository integration — 2026-09-14

Reference: `sunyrain/syninsight-atlas`, branch `main`, commit `faa651baadf761c4969f8c6f800774b7a0bf2495`.

The existing root layout is retained: `assets/`, `data/`, `docs/`, `scripts/`, `structures/`, `tests/`. `pages/` adds generated document views, while `route.html` and `reader.html` sit beside the existing entry page.

The original discovery snapshot, structure SVGs, citation and licenses are preserved byte-for-byte. The legacy checksum file used CRLF-dependent hashes for some files stored with LF in Git; its original file scope is retained, and hashes are corrected to match the actual Git bytes. Original scripts `export_from_autoplanner.py` and `validate_release.py`, and `tests/test_release.py`, are restored from the reference commit. New website checks are separate from that unchanged release contract. `.gitattributes` preserves release bytes across platforms, preventing automatic newline conversion from invalidating checksums.

The connected-route extension lives in `data/database/` and `data/routes/`; it does not redefine the original snapshot's human-admission claims. The README documents both layers separately. No publisher source PDFs, local environments, Git metadata, cache directories or build logs are included.

This is an additive update: no existing tracked repository paths are scheduled for deletion. Before applying to a newer checkout, inspect overlapping changes rather than discarding them. Packaging and local validation do not push commits or change repository settings.
