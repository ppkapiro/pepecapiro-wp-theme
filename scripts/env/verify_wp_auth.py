#!/usr/bin/env python3
"""Quick verification for WordPress REST authentication.

Uses local credentials (env variables or secrets/.wp_env.local) to perform a
simple authenticated request against the WP REST API. No secrets are printed.
"""
from __future__ import annotations

import base64
import os
import sys
from pathlib import Path
from typing import Dict

import requests

CREDENTIALS_FILE = Path("secrets/.wp_env.local")
KEYS = ("WP_URL", "WP_USER", "WP_APP_PASSWORD")


def read_file_credentials() -> Dict[str, str]:
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


def resolve_credentials() -> Dict[str, str]:
    creds = {key: os.getenv(key, "").strip() for key in KEYS if os.getenv(key)}
    file_data = read_file_credentials()
    for key in KEYS:
        if key not in creds and key in file_data:
            creds[key] = file_data[key]
    missing = [key for key in KEYS if key not in creds or not creds[key]]
    if missing:
        raise ValueError(f"Faltan credenciales locales: {', '.join(missing)}")
    url = creds["WP_URL"].rstrip("/")
    if not url.startswith("https://"):
        raise ValueError("WP_URL debe iniciar con https://")
    if "pepecapiro.com" not in url:
        raise ValueError("WP_URL debe apuntar a pepecapiro.com")
    creds["WP_URL"] = url
    return creds


def main() -> int:
    try:
        creds = resolve_credentials()
    except ValueError as exc:
        print(f"[fatal] {exc}")
        return 2

    endpoint = f"{creds['WP_URL']}/wp-json/wp/v2/users/me"
    auth = base64.b64encode(f"{creds['WP_USER']}:{creds['WP_APP_PASSWORD']}".encode("utf-8")).decode("utf-8")
    headers = {
        "Authorization": f"Basic {auth}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    try:
        response = requests.get(endpoint, headers=headers, timeout=15)
    except requests.RequestException as exc:
        print(f"[fatal] Error de red al verificar WP: {exc}")
        return 1

    if response.status_code == 200:
        print(f"[verify] Autenticación OK en {endpoint}")
        return 0
    print(f"[verify] Falló autenticación ({response.status_code}). Revisa credenciales o rota el Application Password.")
    return 3


if __name__ == "__main__":
    sys.exit(main())
