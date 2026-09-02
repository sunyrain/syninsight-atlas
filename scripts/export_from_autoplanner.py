#!/usr/bin/env python3
"""Export a redistribution-safe SynInsight Atlas snapshot from AutoPlanner.

Only derived metadata, candidate structures, source locators, aggregate evidence
counts, and admission state are exported. Publisher article text, PDFs, SI, local
paths, prompts, model logs, and reviewer identities never enter this repository.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any


RELEASE_VERSION = "0.1.0-candidate.1"
RELEASE_SCHEMA = "syninsight_atlas.release.v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        default="../AutoPlanner/benchmarks/recent_total_synthesis",
        help="Path to the AutoPlanner benchmark directory.",
    )
    parser.add_argument("--output", default=".", help="SynInsight Atlas repository root.")
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def locator_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        parts = []
        for key in ("type", "section_title", "paragraph_index", "page", "scheme"):
            if key in value and value[key] not in (None, ""):
                parts.append(f"{key}={value[key]}")
        return "; ".join(parts) or json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value or "")


def render_structure(smiles: str, path: Path, legend: str) -> None:
    from rdkit import Chem
    from rdkit.Chem.Draw import rdMolDraw2D

    molecule = Chem.MolFromSmiles(smiles)
    if molecule is None:
        raise RuntimeError(f"invalid_candidate_smiles:{legend}")
    drawer = rdMolDraw2D.MolDraw2DSVG(520, 340)
    options = drawer.drawOptions()
    options.clearBackground = False
    options.padding = 0.08
    rdMolDraw2D.PrepareAndDrawMolecule(drawer, molecule, legend=legend)
    drawer.FinishDrawing()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(drawer.GetDrawingText(), encoding="utf-8")


def safe_source_summary(receipt: dict[str, Any]) -> dict[str, Any]:
    return {
        "acquired": bool(receipt.get("source_package_acquired")),
        "completeness": str(receipt.get("source_package_completeness") or "none"),
        "artifact_kinds": sorted(
            {str(row.get("artifact_kind") or "") for row in receipt.get("artifacts") or []}
        ),
        "status": str(receipt.get("status") or "missing_receipt"),
    }


def make_target(
    *,
    target: dict[str, Any],
    cohort: str,
    paper: dict[str, Any],
    visual: dict[str, Any],
    route: dict[str, Any],
    receipt: dict[str, Any],
    output_root: Path,
) -> dict[str, Any]:
    target_id = str(target["target_slot_id"])
    rdkit_valid = (visual.get("rdkit_validation") or {}).get("status") == "roundtrip_valid"
    smiles = str(visual.get("visual_canonical_isomeric_smiles") or "") if rdkit_valid else ""
    structure_asset = ""
    if smiles:
        structure_asset = f"structures/{target_id}.svg"
        render_structure(smiles, output_root / structure_asset, str(target.get("target_name") or ""))
    passages = list(route.get("evidence_passages") or [])
    route_locators = []
    seen_locators: set[str] = set()
    for passage in passages:
        locator = locator_text(passage.get("source_locator"))
        if locator and locator not in seen_locators:
            seen_locators.add(locator)
            route_locators.append(locator)
    source_image = dict(visual.get("source_image") or {})
    return {
        "target_id": target_id,
        "paper_id": str(target["paper_id"]),
        "cohort": cohort,
        "target_name": str(target.get("target_name") or ""),
        "doi": str(target.get("doi") or ""),
        "paper_title": str(paper.get("title") or target.get("publication_title") or ""),
        "journal": str(paper.get("journal") or ""),
        "publication_date": str(paper.get("publication_date") or ""),
        "source_url": str(paper.get("source_url") or ""),
        "candidate_structure": {
            "status": str(visual.get("visual_status") or "unresolved"),
            "rdkit_valid": bool(rdkit_valid),
            "isomeric_smiles": smiles,
            "svg": structure_asset,
            "source_locator": str(visual.get("source_locator") or ""),
            "source_artifact_sha256": str(source_image.get("source_artifact_sha256") or ""),
            "transcription_note": str(visual.get("transcription_note") or ""),
            "admission_authority": False,
        },
        "route_evidence_lead": {
            "status": str(route.get("extraction_status") or "not_available"),
            "passage_count": len(passages),
            "source_locators": route_locators,
            "admission_authority": False,
        },
        "source_package": safe_source_summary(receipt),
        "human_review": {
            "paper_status": str(target.get("paper_review_status") or "not_started"),
            "structure_status": str(
                target.get("structure_status") or "pending_source_concordant_structure"
            ),
            "route_status": str(
                target.get("route_evidence_status") or "pending_human_route_review"
            ),
            "runnable": bool(target.get("runnable")),
        },
        "formal_benchmark_eligible": bool(target.get("runnable")),
    }


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def export(*, source: Path, output_root: Path) -> dict[str, Any]:
    papers_all = read_jsonl(source / "papers.jsonl")
    papers_by_id = {str(row["paper_id"]): row for row in papers_all}
    p0_targets = [
        row for row in read_jsonl(source / "target_slots.jsonl") if row.get("slot_class") == "primary"
    ]
    p1_targets = read_jsonl(
        source / "curation_candidates" / "p1_scope" / "candidate-target-slots.jsonl"
    )
    p0_visual = {
        str(row["target_slot_id"]): row
        for row in read_jsonl(source / "visual_structure_candidates.jsonl")
    }
    p1_visual = {
        str(row["target_slot_id"]): row
        for row in read_jsonl(
            source / "curation_candidates" / "p1_scope" / "visual-structure-candidates.jsonl"
        )
    }
    p0_routes = {
        str(row["target_slot_id"]): row
        for row in read_jsonl(source / "route_evidence_candidates.jsonl")
    }
    p1_routes = {
        str(row["target_slot_id"]): row
        for row in read_jsonl(
            source / "curation_candidates" / "p1_scope" / "route-evidence-candidates.jsonl"
        )
    }
    receipts = {
        str(row["paper_id"]): row
        for row in (
            read_jsonl(source / "source_package_receipts.jsonl")
            + read_jsonl(source / "p1_source_package_receipts.jsonl")
        )
    }
    manifest = read_json(source / "manifest.json")
    quality = read_json(source / "quality_report.json")

    targets: list[dict[str, Any]] = []
    for cohort, source_targets, visuals, routes in (
        ("P0", p0_targets, p0_visual, p0_routes),
        ("P1", p1_targets, p1_visual, p1_routes),
    ):
        for target in source_targets:
            paper_id = str(target["paper_id"])
            targets.append(
                make_target(
                    target=target,
                    cohort=cohort,
                    paper=papers_by_id[paper_id],
                    visual=visuals.get(str(target["target_slot_id"]), {}),
                    route=routes.get(str(target["target_slot_id"]), {}),
                    receipt=receipts.get(paper_id, {}),
                    output_root=output_root,
                )
            )
    targets.sort(key=lambda row: (row["target_name"].casefold(), row["target_id"]))

    paper_ids = sorted({str(row["paper_id"]) for row in targets})
    targets_by_paper: dict[str, list[dict[str, Any]]] = {}
    for target in targets:
        targets_by_paper.setdefault(str(target["paper_id"]), []).append(target)
    papers = []
    for paper_id in paper_ids:
        paper = papers_by_id[paper_id]
        children = targets_by_paper[paper_id]
        cohorts = sorted({str(row["cohort"]) for row in children})
        papers.append(
            {
                "paper_id": paper_id,
                "article_family_id": str(paper.get("article_family_id") or ""),
                "doi": str(paper.get("doi") or ""),
                "title": str(paper.get("title") or ""),
                "first_author": str(paper.get("first_author") or ""),
                "journal": str(paper.get("journal") or ""),
                "publication_date": str(paper.get("publication_date") or ""),
                "source_url": str(paper.get("source_url") or ""),
                "cohorts": cohorts,
                "target_count": len(children),
                "valid_structure_candidate_count": sum(
                    row["candidate_structure"]["rdkit_valid"] for row in children
                ),
                "route_evidence_lead_count": sum(
                    row["route_evidence_lead"]["passage_count"] > 0 for row in children
                ),
                "human_review_status": str(paper.get("human_review_status") or "not_started"),
                "source_package": safe_source_summary(receipts.get(paper_id, {})),
            }
        )
    papers.sort(key=lambda row: (row["publication_date"], row["title"]), reverse=True)

    summary = {
        "schema_version": RELEASE_SCHEMA,
        "release_version": RELEASE_VERSION,
        "release_stage": "candidate_curation_release",
        "candidate_papers": len(papers),
        "candidate_targets": len(targets),
        "source_packages_acquired": sum(row["source_package"]["acquired"] for row in papers),
        "rdkit_valid_structure_candidates": sum(
            row["candidate_structure"]["rdkit_valid"] for row in targets
        ),
        "targets_with_route_evidence_leads": sum(
            row["route_evidence_lead"]["passage_count"] > 0 for row in targets
        ),
        "human_admitted_structures": int(
            quality.get("counts", {}).get("admitted_source_concordant_structures", 0)
        ),
        "human_admitted_routes": int(
            quality.get("counts", {}).get("admitted_literature_routes_or_key_steps", 0)
        ),
        "runnable_targets": int(quality.get("counts", {}).get("runnable_primary_targets", 0)),
        "freeze_window": manifest.get("freeze_window", {}),
        "all_source_quality_checks_passed": bool(quality.get("all_checks_passed")),
        "claim_boundary": manifest.get("claim_boundary", {}),
    }
    release = {
        **summary,
        # Bind the public release to the immutable source snapshot. Re-exporting
        # unchanged inputs must not change data bytes merely because wall time moved.
        "generated_at": manifest.get("generated_at", ""),
        "source_snapshot_generated_at": manifest.get("generated_at", ""),
        "source_manifest_sha256": sha256(source / "manifest.json"),
        "redistribution_boundary": {
            "included": [
                "bibliographic metadata",
                "candidate target identities",
                "candidate isomeric SMILES and derived SVG depictions",
                "source locators and hashes",
                "aggregate route-evidence lead counts",
                "human-admission state",
            ],
            "excluded": [
                "publisher PDF, HTML, XML, and supporting information",
                "verbatim article passages",
                "local source paths and browser state",
                "model prompts, logs, and private reviewer identities",
            ],
        },
    }
    write_json(output_root / "data" / "summary.json", summary)
    write_json(output_root / "data" / "release.json", release)
    write_json(output_root / "data" / "papers.json", papers)
    write_json(output_root / "data" / "targets.json", targets)

    write_csv(
        output_root / "data" / "papers.csv",
        [
            {
                "paper_id": row["paper_id"],
                "doi": row["doi"],
                "title": row["title"],
                "journal": row["journal"],
                "publication_date": row["publication_date"],
                "cohorts": ";".join(row["cohorts"]),
                "target_count": row["target_count"],
                "source_completeness": row["source_package"]["completeness"],
                "human_review_status": row["human_review_status"],
            }
            for row in papers
        ],
        [
            "paper_id",
            "doi",
            "title",
            "journal",
            "publication_date",
            "cohorts",
            "target_count",
            "source_completeness",
            "human_review_status",
        ],
    )
    write_csv(
        output_root / "data" / "targets.csv",
        [
            {
                "target_id": row["target_id"],
                "target_name": row["target_name"],
                "cohort": row["cohort"],
                "paper_id": row["paper_id"],
                "doi": row["doi"],
                "journal": row["journal"],
                "publication_date": row["publication_date"],
                "candidate_structure_status": row["candidate_structure"]["status"],
                "candidate_isomeric_smiles": row["candidate_structure"]["isomeric_smiles"],
                "route_evidence_passage_count": row["route_evidence_lead"]["passage_count"],
                "source_completeness": row["source_package"]["completeness"],
                "formal_benchmark_eligible": row["formal_benchmark_eligible"],
            }
            for row in targets
        ],
        [
            "target_id",
            "target_name",
            "cohort",
            "paper_id",
            "doi",
            "journal",
            "publication_date",
            "candidate_structure_status",
            "candidate_isomeric_smiles",
            "route_evidence_passage_count",
            "source_completeness",
            "formal_benchmark_eligible",
        ],
    )

    checksum_paths = sorted((output_root / "data").glob("*")) + sorted(
        (output_root / "structures").glob("*.svg")
    )
    checksum_lines = [
        f"{sha256(path)}  {path.relative_to(output_root).as_posix()}" for path in checksum_paths
    ]
    (output_root / "CHECKSUMS.sha256").write_text(
        "\n".join(checksum_lines) + "\n", encoding="utf-8"
    )
    return summary


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    source = (repo_root / args.source).resolve()
    output_root = (repo_root / args.output).resolve()
    summary = export(source=source, output_root=output_root)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
