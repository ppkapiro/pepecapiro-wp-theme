#!/usr/bin/env python3
"""Herramienta CLI para traducir contenido Markdown ES→EN (u otras combinaciones).

Admite proveedores OpenAI y DeepL mediante variables de entorno y modo "dummy"
para pruebas locales. Se usa en Fase 1 para generar borradores EN antes de
publicarlos en WordPress.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

import requests

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
DEFAULT_GLOSSARY = (
    "Mantén el tono profesional positivo. Respeta tecnicismos (WordPress, Polylang,"
    " CI/CD, Lighthouse). No inventes enlaces ni datos. Si el texto ya está en el"
    " idioma destino, devuélvelo tal cual."
)


class TranslationError(RuntimeError):
    """Errores provenientes del proveedor de traducción."""


@dataclass
class TranslationResult:
    source_path: Path
    target_path: Path
    status: str
    details: Optional[str] = None


class BaseTranslator:
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        raise NotImplementedError


class DummyTranslator(BaseTranslator):
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        return (
            f"[TRANSLATION PLACEHOLDER {source_lang}->{target_lang}]\n\n" + text
        )


class OpenAITranslator(BaseTranslator):
    def __init__(self, api_key: str, model: str = DEFAULT_MODEL, glossary: str = DEFAULT_GLOSSARY):
        self.api_key = api_key
        self.model = model
        self.glossary = glossary

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        system_prompt = (
            "You are a bilingual copywriter. Translate the user's Markdown from "
            f"{source_lang.upper()} into {target_lang.upper()} maintaining structure,"
            " plain Markdown, and professional tone."
        )
        user_prompt = (
            f"Translation context:\nGlossary:{self.glossary}\n\n"
            f"Text ({source_lang}):\n{text}"
        )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 1600,
        }
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                data=json.dumps(payload),
                timeout=40,
            )
        except requests.RequestException as exc:  # pragma: no cover - network
            raise TranslationError(f"Fallo de red con OpenAI: {exc}") from exc
        if response.status_code >= 400:
            raise TranslationError(
                f"OpenAI devolvió {response.status_code}: {response.text[:200]}"
            )
        data = response.json()
        try:
            message = data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as exc:
            raise TranslationError(f"Respuesta inesperada de OpenAI: {data}") from exc
        return message


class DeepLTranslator(BaseTranslator):
    def __init__(self, api_key: str, custom_glossary: str = DEFAULT_GLOSSARY):
        self.api_key = api_key
        self.glossary = custom_glossary

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        payload = {
            "auth_key": self.api_key,
            "text": text,
            "source_lang": source_lang.upper(),
            "target_lang": target_lang.upper(),
            "preserve_formatting": 1,
            "tag_handling": "xml",
            "context": self.glossary,
        }
        try:
            response = requests.post(
                "https://api-free.deepl.com/v2/translate",
                data=payload,
                timeout=40,
            )
        except requests.RequestException as exc:  # pragma: no cover - network
            raise TranslationError(f"Fallo de red con DeepL: {exc}") from exc
        if response.status_code >= 400:
            raise TranslationError(
                f"DeepL devolvió {response.status_code}: {response.text[:200]}"
            )
        data = response.json()
        try:
            return data["translations"][0]["text"].strip()
        except (KeyError, IndexError) as exc:
            raise TranslationError(f"Respuesta inesperada de DeepL: {data}") from exc


def discover_markdown(root: Path, source_lang: str, slugs: Optional[Iterable[str]]) -> List[Path]:
    pattern = f"*.{source_lang}.md"
    candidates = list(root.rglob(pattern))
    if not slugs:
        return sorted(candidates)
    wanted = {slug.strip() for slug in slugs if slug.strip()}
    filtered: List[Path] = []
    for path in candidates:
        base_slug = path.name[: -len(f".{source_lang}.md")]
        if base_slug in wanted:
            filtered.append(path)
    return sorted(filtered)


def ensure_target_path(source_path: Path, source_lang: str, target_lang: str) -> Path:
    suffix = f".{source_lang}.md"
    name = source_path.name
    if name.endswith(suffix):
        slug = name[: -len(suffix)]
    else:
        slug = source_path.stem
    return source_path.with_name(f"{slug}.{target_lang}.md")


def select_translator(provider: str) -> BaseTranslator:
    provider = provider.lower()
    if provider in {"auto", "openai"}:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            return OpenAITranslator(api_key)
        if provider == "openai":
            raise TranslationError("OPENAI_API_KEY no configurada")
    if provider in {"auto", "deepl"}:
        api_key = os.getenv("DEEPL_API_KEY")
        if api_key:
            return DeepLTranslator(api_key)
        if provider == "deepl":
            raise TranslationError("DEEPL_API_KEY no configurada")
    if provider in {"auto", "dummy"}:
        return DummyTranslator()
    raise TranslationError(f"Proveedor no soportado: {provider}")


def translate_files(
    content_dir: Path,
    source_lang: str,
    target_lang: str,
    provider: str,
    slugs: Optional[Iterable[str]] = None,
    force: bool = False,
    dry_run: bool = False,
    limit: Optional[int] = None,
) -> List[TranslationResult]:
    translator = select_translator(provider)
    files = discover_markdown(content_dir, source_lang, slugs)
    if limit is not None:
        files = files[:limit]
    results: List[TranslationResult] = []
    for source_path in files:
        target_path = ensure_target_path(source_path, source_lang, target_lang)
        target_exists = target_path.exists()
        if target_exists and not force:
            results.append(
                TranslationResult(
                    source_path=source_path,
                    target_path=target_path,
                    status="skipped",
                    details="target-exists",
                )
            )
            continue
        if dry_run:
            results.append(
                TranslationResult(
                    source_path=source_path,
                    target_path=target_path,
                    status="planned",
                    details="dry-run",
                )
            )
            continue
        try:
            raw_text = source_path.read_text(encoding="utf-8")
        except OSError as exc:
            results.append(
                TranslationResult(
                    source_path=source_path,
                    target_path=target_path,
                    status="error",
                    details=f"No se pudo leer: {exc}",
                )
            )
            continue
        try:
            translated = translator.translate(raw_text, source_lang, target_lang)
        except TranslationError as exc:
            results.append(
                TranslationResult(
                    source_path=source_path,
                    target_path=target_path,
                    status="error",
                    details=str(exc),
                )
            )
            continue
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(translated, encoding="utf-8")
        results.append(
            TranslationResult(
                source_path=source_path,
                target_path=target_path,
                status="updated" if target_exists else "created",
            )
        )
    return results


def write_report(results: List[TranslationResult], report_dir: Path) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"translation_run_{timestamp}.md"
    lines: List[str] = ["# Translation Run", f"Generado: {datetime.utcnow().isoformat()}Z", ""]
    summary = {
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "planned": 0,
        "error": 0,
    }
    for item in results:
        summary[item.status] = summary.get(item.status, 0) + 1
    lines.append("## Resumen")
    for key, value in summary.items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## Detalle")
    for item in results:
        lines.append(
            f"- {item.status.upper()} {item.source_path} -> {item.target_path}" +
            (f" ({item.details})" if item.details else "")
        )
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Traductor de markdown bilingüe")
    parser.add_argument("--content-dir", default="content", help="Directorio base del contenido")
    parser.add_argument("--source-lang", default="es", help="Idioma origen (por defecto ES)")
    parser.add_argument("--target-lang", default="en", help="Idioma destino (por defecto EN)")
    parser.add_argument("--provider", default=os.getenv("TRANSLATION_PROVIDER", "auto"),
                        choices=["auto", "openai", "deepl", "dummy"],
                        help="Proveedor de traducción")
    parser.add_argument("--slug", action="append", help="Slug específico a traducir (puede repetirse)")
    parser.add_argument("--force", action="store_true", help="Sobrescribir archivos destino existentes")
    parser.add_argument("--dry-run", action="store_true", help="Solo planificar, sin escribir archivos")
    parser.add_argument("--limit", type=int, help="Limitar número de archivos a procesar")
    parser.add_argument("--report-dir", default="reports/operations", help="Directorio de reportes")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    content_dir = Path(args.content_dir)
    if not content_dir.exists():
        print(f"[fatal] No existe {content_dir}")
        return 2
    try:
        results = translate_files(
            content_dir=content_dir,
            source_lang=args.source_lang,
            target_lang=args.target_lang,
            provider=args.provider,
            slugs=args.slug,
            force=args.force,
            dry_run=args.dry_run,
            limit=args.limit,
        )
    except TranslationError as exc:
        print(f"[fatal] {exc}")
        return 1
    for item in results:
        detail = f" ({item.details})" if item.details else ""
        print(f"[{item.status}] {item.source_path} -> {item.target_path}{detail}")
    if not args.dry_run:
        report_path = write_report(results, Path(args.report_dir))
        print(f"[ok] Reporte generado en {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
