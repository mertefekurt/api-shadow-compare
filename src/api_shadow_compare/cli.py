from __future__ import annotations

import argparse
from pathlib import Path

from api_shadow_compare.core import compare, load_capture, render_json, render_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare old and new API response captures.")
    parser.add_argument("old", type=Path)
    parser.add_argument("new", type=Path)
    parser.add_argument("--latency-ratio", type=float, default=1.5)
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    drifts = compare(load_capture(args.old), load_capture(args.new), args.latency_ratio)
    print(render_json(drifts) if args.json else render_text(drifts), end="")
    return 1 if drifts else 0
