from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from armor_types import RetrievedSource, SourceRequest


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def retrieve_from_manifest(
    requests: list[SourceRequest],
    manifest: list[dict[str, Any]] | dict[str, Any],
    local_source_dir: str | Path | None = None,
) -> list[RetrievedSource]:
    records = _flatten_manifest(manifest)
    retrieved: list[RetrievedSource] = []

    for request in requests:
        for record in records:
            if not _matches_request(record, request):
                continue
            text = _load_local_text(record, local_source_dir)
            retrieved.append(
                RetrievedSource(
                    source_family=_source_family(record),
                    citation=record.get("citation") or record.get("id") or "unknown",
                    title=record.get("title") or record.get("id") or "Untitled source",
                    text=text,
                    url=record.get("url"),
                    part=str(record.get("far_part") or request.part or ""),
                    metadata=record,
                )
            )
            break

    return retrieved


def _flatten_manifest(manifest: list[dict[str, Any]] | dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(manifest, list):
        return manifest
    records: list[dict[str, Any]] = []
    for value in manifest.values():
        if isinstance(value, list):
            records.extend(value)
        elif isinstance(value, dict):
            records.append(value)
    return records


def _matches_request(record: dict[str, Any], request: SourceRequest) -> bool:
    part = str(record.get("far_part") or "")
    rung_name = str(record.get("rung_name") or "").lower()
    title = str(record.get("title") or "").lower()
    url = str(record.get("url") or "").lower()

    if request.part and request.part != "unknown":
        normalized_request_part = request.part[1:] if request.part.startswith("2") and len(request.part) == 3 else request.part
        if part and part != request.part and part != normalized_request_part:
            return False

    family = request.source_family
    if family == "rfo_far":
        return "rfo far part" in title or "far overhaul part" in url
    if family == "rfo_far_saad":
        return "saad" in title or "saad" in rung_name
    if family == "dfars_rfo":
        return "dfars" in title or "armor-plus" in url or "github" in url
    if family == "class_deviation":
        return "deviation" in title or "class deviation" in title
    if family == "dfars_pgi":
        return "pgi" in title or "pgi" in url
    if family == "rfo_conventions":
        return "part 1" in title or "convention" in title or "far_1_107" in url
    return False


def _source_family(record: dict[str, Any]) -> str:
    title = str(record.get("title") or "").lower()
    url = str(record.get("url") or "").lower()
    if "pgi" in title or "pgi" in url:
        return "dfars_pgi"
    if "dfars" in title or "armor-plus" in url or "github" in url:
        return "dfars_rfo"
    if "saad" in title:
        return "rfo_far_saad"
    if "convention" in title or "far_1_107" in url:
        return "rfo_conventions"
    return "rfo_far"


def _load_local_text(record: dict[str, Any], local_source_dir: str | Path | None) -> str:
    filename = record.get("filename") or record.get("file")
    if not filename or local_source_dir is None:
        return ""
    path = Path(local_source_dir) / str(filename)
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")

