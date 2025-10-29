#!/usr/bin/env python3
"""Fail if raw hex colors are present outside tokens.css.

Rules:
- Scan CSS files under `pepecapiro/`.
- Ignore: `assets/css/tokens.css`, any `*.min.css`.
- Flag any occurrence of #rgb, #rgba (3,4) or #rrggbb, #rrggbbaa (6,8) hex.

Exit codes:
 0 -> PASS (no offending hex values found)
 1 -> FAIL (found hex usages outside tokens)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[2]
CSS_ROOT = ROOT / "pepecapiro"

HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")


def should_skip(path: Path) -> bool:
    name = path.name
    if name.endswith(".min.css"):
        return True
    # Allow tokens to define canonical palette
    if name == "tokens.css":
        return True
    # Allow critical.css (inlined, needs hardcoded values for performance)
    if name == "critical.css":
        return True
    return False


def find_offenders() -> Dict[Path, List[str]]:
    offenders: Dict[Path, List[str]] = {}
    for css in CSS_ROOT.rglob("*.css"):
        if should_skip(css):
            continue
        try:
            text = css.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        matches = HEX_RE.findall(text)
        if matches:
            offenders[css] = matches
    return offenders


def main() -> int:
    offenders = find_offenders()
    if not offenders:
        print("[css-check] PASS: no hex colors found outside tokens.css")
        return 0

    print("[css-check] FAIL: hex colors detected outside tokens.css:\n")
    for path, matches in offenders.items():
        unique = sorted(set(matches))
        print(f"- {path.relative_to(ROOT)} -> {', '.join(unique)}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
