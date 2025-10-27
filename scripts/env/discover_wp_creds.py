#!/usr/bin/env python3
"""Probe for existing WordPress credentials without exposing secrets.

This script inspects environment variables and common local secret files to
identify whether WP_URL, WP_USER and WP_APP_PASSWORD are available. It writes
its findings to `reports/operations/wp_creds_probe.json`.

Exit codes:
 0 -> All three credentials found.
 2 -> At least one missing (fallback interactive flow should run).
 1 -> Unexpected error.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Dict, Iterable, Tuple

KEYS = ("WP_URL", "WP_USER", "WP_APP_PASSWORD")
CANDIDATE_FILES = (
    ".env.local",
    ".env",
    ".env.development.local",
    ".env.staging.local",
    "config/local.env",
    "configs/wp_env.local",
    "secrets/.wp_env.local",
)
SFTP_FILE = Path(".vscode/sftp.json")
OUTPUT_PATH = Path("reports/operations/wp_creds_probe.json")


def read_key_values(path: Path) -> Dict[str, str]:
    data: Dict[str, str] = {}
    try:
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if key in KEYS and value:
                data[key] = value
    except OSError:
        pass
    return data


def gather_from_env() -> Tuple[Dict[str, str], Dict[str, str]]:
    values: Dict[str, str] = {}
    sources: Dict[str, str] = {}
    for key in KEYS:
        val = os.getenv(key)
        if val:
            values[key] = val
            sources[key] = "env"
    return values, sources


def gather_from_files(missing_keys: Iterable[str]) -> Dict[str, Tuple[str, str]]:
    found: Dict[str, Tuple[str, str]] = {}
    for rel_path in CANDIDATE_FILES:
        path = Path(rel_path)
        if not path.is_file():
            continue
        kv = read_key_values(path)
        for key in missing_keys:
            value = kv.get(key)
            if value and key not in found:
                found[key] = (value, f"file:{rel_path}")
    return found


def discover_sftp_hint() -> str | None:
    if not SFTP_FILE.is_file():
        return None
    try:
        import json as _json

        data = _json.loads(SFTP_FILE.read_text(encoding="utf-8"))
        host = data.get("host") if isinstance(data, dict) else None
        if isinstance(host, str) and host:
            return host
    except Exception:
        return None
    return None


def gather_script_hint() -> str | None:
    candidates = (
        "scripts/publish_content.py",
        "docs/DEPLOY_RUNBOOK.md",
        "docs/OPERATIONS_OVERVIEW.md",
        "README.md",
    )
    for rel_path in candidates:
        path = Path(rel_path)
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if "https://pepecapiro.com" in text:
            return "https://pepecapiro.com"
    return None


def main() -> int:
    values, sources = gather_from_env()
    missing_keys = [k for k in KEYS if k not in values]
    if missing_keys:
        file_hits = gather_from_files(missing_keys)
        for key, (value, origin) in file_hits.items():
            values[key] = value
            sources[key] = origin

    has_all = all(key in values for key in KEYS)
    source_label = "none"
    if has_all:
        if all(sources.get(key) == "env" for key in KEYS):
            source_label = "env"
        else:
            source_label = "file"
    elif any(key in sources and sources[key].startswith("file") for key in KEYS):
        source_label = "file"
    elif any(sources.get(key) == "env" for key in KEYS):
        source_label = "env"

    hint_host = discover_sftp_hint()
    hint_url = gather_script_hint()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    probe = {
        "has_url": "WP_URL" in values,
        "has_user": "WP_USER" in values,
        "has_app_password": "WP_APP_PASSWORD" in values,
        "source": source_label,
        "sources_detail": sources,
        "hints": {
            "sftp_host": hint_host,
            "likely_url": hint_url,
        },
    }
    OUTPUT_PATH.write_text(json.dumps(probe, ensure_ascii=True, indent=2), encoding="utf-8")

    if has_all:
        print("[probe] Credenciales WP localizadas (ver reports/operations/wp_creds_probe.json)")
        return 0

    print("[probe] Faltan credenciales WP. Ejecuta configure_wp_creds.py si procede.")
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # pragma: no cover
        print(f"[fatal] Error inesperado en discover_wp_creds: {exc}")
        sys.exit(1)
