from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Drift:
    request_id: str
    kind: str
    detail: str


def load_capture(path: Path) -> dict[str, dict]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return {str(row["id"]): row for row in rows}


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, nested in value.items():
            child = f"{prefix}.{key}" if prefix else str(key)
            out.update(flatten(nested, child))
        return out
    return {prefix: value}


def compare(old: dict[str, dict], new: dict[str, dict], latency_ratio: float) -> list[Drift]:
    drifts: list[Drift] = []
    for request_id, before in old.items():
        after = new.get(request_id)
        if after is None:
            drifts.append(Drift(request_id, "missing-response", "new capture has no matching id"))
            continue
        if before.get("status") != after.get("status"):
            drifts.append(
                Drift(
                    request_id,
                    "status-change",
                    f"{before.get('status')} -> {after.get('status')}",
                )
            )
        old_body = flatten(before.get("body", {}))
        new_body = flatten(after.get("body", {}))
        for field in sorted(old_body.keys() - new_body.keys()):
            drifts.append(Drift(request_id, "field-removed", field))
        for field in sorted(new_body.keys() - old_body.keys()):
            drifts.append(Drift(request_id, "field-added", field))
        for field in sorted(old_body.keys() & new_body.keys()):
            if old_body[field] != new_body[field]:
                drifts.append(
                    Drift(
                        request_id,
                        "value-change",
                        f"{field}: {old_body[field]} -> {new_body[field]}",
                    )
                )
        old_latency = float(before.get("latency_ms", 0) or 0)
        new_latency = float(after.get("latency_ms", 0) or 0)
        if old_latency and new_latency / old_latency > latency_ratio:
            drifts.append(
                Drift(
                    request_id,
                    "latency-regression",
                    f"{old_latency:.0f}ms -> {new_latency:.0f}ms",
                )
            )
    for request_id in sorted(new.keys() - old.keys()):
        drifts.append(Drift(request_id, "new-response", "new capture has an extra id"))
    return drifts


def render_text(drifts: list[Drift]) -> str:
    if not drifts:
        return "No API drift found.\n"
    return "\n".join(f"{d.request_id}\t{d.kind}\t{d.detail}" for d in drifts) + "\n"


def render_json(drifts: list[Drift]) -> str:
    return json.dumps([asdict(drift) for drift in drifts], indent=2)
