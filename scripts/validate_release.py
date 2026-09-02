#!/usr/bin/env python3
"""Validate the public SynInsight Atlas release without private source files."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any


FORBIDDEN_KEYS = {
    "cache_path",
    "source_artifact_path",
    "verbatim_text",
    "reviewer_id",
    "prompt",
    "model_output",
}
WINDOWS_ABSOLUTE_RE = re.compile(r"^[A-Za-z]:[\\/]")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def walk(value: Any, path: str = "$"):
    if isinstance(value, dict):
        for key, child in value.items():
            yield f"{path}.{key}", key, child
            yield from walk(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, f"{path}[{index}]")


def validate(root: Path) -> dict[str, int]:
    summary = json.loads((root / "data" / "summary.json").read_text(encoding="utf-8"))
    papers = json.loads((root / "data" / "papers.json").read_text(encoding="utf-8"))
    targets = json.loads((root / "data" / "targets.json").read_text(encoding="utf-8"))
    release = json.loads((root / "data" / "release.json").read_text(encoding="utf-8"))
    if len(papers) != summary["candidate_papers"]:
        raise RuntimeError("paper_count_mismatch")
    if len(targets) != summary["candidate_targets"]:
        raise RuntimeError("target_count_mismatch")
    if len({row["paper_id"] for row in papers}) != len(papers):
        raise RuntimeError("paper_ids_not_unique")
    if len({row["target_id"] for row in targets}) != len(targets):
        raise RuntimeError("target_ids_not_unique")
    paper_ids = {row["paper_id"] for row in papers}
    if not all(row["paper_id"] in paper_ids for row in targets):
        raise RuntimeError("target_has_unknown_paper")
    if sum(row["candidate_structure"]["rdkit_valid"] for row in targets) != summary[
        "rdkit_valid_structure_candidates"
    ]:
        raise RuntimeError("valid_structure_count_mismatch")
    if sum(row["route_evidence_lead"]["passage_count"] > 0 for row in targets) != summary[
        "targets_with_route_evidence_leads"
    ]:
        raise RuntimeError("route_lead_count_mismatch")
    if any(row["formal_benchmark_eligible"] != row["human_review"]["runnable"] for row in targets):
        raise RuntimeError("benchmark_eligibility_not_bound_to_admission")
    for document_name, document in (("release", release), ("papers", papers), ("targets", targets)):
        for field_path, key, value in walk(document):
            if key in FORBIDDEN_KEYS:
                raise RuntimeError(f"forbidden_public_field:{document_name}:{field_path}")
            if isinstance(value, str) and (
                WINDOWS_ABSOLUTE_RE.match(value) or value.startswith("/home/")
            ):
                raise RuntimeError(f"absolute_path_leak:{document_name}:{field_path}")
    for target in targets:
        svg = target["candidate_structure"]["svg"]
        if svg:
            relative = PurePosixPath(svg)
            if relative.is_absolute() or ".." in relative.parts or not (root / relative).is_file():
                raise RuntimeError(f"structure_asset_invalid:{target['target_id']}")
    for filename, expected in (("papers.csv", len(papers)), ("targets.csv", len(targets))):
        with (root / "data" / filename).open(encoding="utf-8-sig", newline="") as handle:
            if sum(1 for _ in csv.DictReader(handle)) != expected:
                raise RuntimeError(f"csv_count_mismatch:{filename}")
    checksum_rows = []
    for line in (root / "CHECKSUMS.sha256").read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        path = root / relative
        if not path.is_file() or sha256(path) != digest:
            raise RuntimeError(f"checksum_invalid:{relative}")
        checksum_rows.append(relative)
    if not checksum_rows:
        raise RuntimeError("checksum_manifest_empty")
    return {
        "papers": len(papers),
        "targets": len(targets),
        "structures": summary["rdkit_valid_structure_candidates"],
        "checksums": len(checksum_rows),
    }


if __name__ == "__main__":
    print(json.dumps(validate(Path(__file__).resolve().parents[1]), indent=2))
