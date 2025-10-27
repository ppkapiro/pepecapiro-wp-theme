#!/usr/bin/env python3
"""Interactive helper to configure local WordPress credentials.

The script prompts the user for WP_URL, WP_USER and WP_APP_PASSWORD if any of
those values are missing from the current environment or the local secrets
file (`secrets/.wp_env.local`). Collected values are stored in that file, which
must remain ignored by Git.
"""
from __future__ import annotations

import os
import sys
from getpass import getpass
from pathlib import Path
from typing import Dict

CREDENTIALS_FILE = Path("secrets/.wp_env.local")
KEYS = ("WP_URL", "WP_USER", "WP_APP_PASSWORD")


def read_existing() -> Dict[str, str]:
    data: Dict[str, str] = {}
    if not CREDENTIALS_FILE.is_file():
        return data
    try:
        for raw in CREDENTIALS_FILE.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if key in KEYS and value:
                data[key] = value
    except OSError:
        pass
    return data


def prompt_missing(existing: Dict[str, str]) -> Dict[str, str]:
    updated = dict(existing)
    print("[configure] Introduce los valores solicitados. No se mostrarán en pantalla.")
    if not existing.get("WP_URL"):
        url = input("WP_URL (ej. https://pepecapiro.com): ").strip()
        updated["WP_URL"] = url
    if not existing.get("WP_USER"):
        user = input("WP_USER (usuario con permiso de publicación): ").strip()
        updated["WP_USER"] = user
    if not existing.get("WP_APP_PASSWORD"):
        app_pass = getpass("WP_APP_PASSWORD (Application Password): ").strip()
        updated["WP_APP_PASSWORD"] = app_pass
    return updated


def validate(data: Dict[str, str]) -> None:
    missing = [key for key in KEYS if not data.get(key)]
    if missing:
        raise ValueError(f"Faltan datos obligatorios: {', '.join(missing)}")
    url = data["WP_URL"].strip()
    if not url.startswith("https://"):
        raise ValueError("WP_URL debe iniciar con https://")
    if url.endswith("/"):
        url = url.rstrip("/")
    data["WP_URL"] = url
    if "pepecapiro.com" not in url:
        raise ValueError("WP_URL debe apuntar a pepecapiro.com")


def persist(data: Dict[str, str]) -> None:
    CREDENTIALS_FILE.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{key}={data[key]}" for key in KEYS]
    CREDENTIALS_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    try:
        CREDENTIALS_FILE.chmod(0o600)
    except OSError:
        pass


def main() -> int:
    existing_env = {key: os.getenv(key, "").strip() for key in KEYS if os.getenv(key)}
    existing_file = read_existing()
    merged = dict(existing_file)
    merged.update(existing_env)
    if len(merged) == len(KEYS) and all(merged.get(key) for key in KEYS):
        print("[configure] Ya existen credenciales completas en el entorno o archivo local.")
        return 0

    merged = prompt_missing(merged)
    try:
        validate(merged)
    except ValueError as exc:
        print(f"[fatal] {exc}")
        return 2
    persist(merged)
    print("[configure] Credenciales guardadas en secrets/.wp_env.local")
    print("[configure] Recarga el entorno con: source secrets/.wp_env.local")
    print("[configure] En PowerShell: Get-Content secrets/.wp_env.local | ForEach-Object { if ($_ -match '=' ) { $name, $value = $_.Split('=',2); setx $name $value } }")
    return 0


if __name__ == "__main__":
    sys.exit(main())
