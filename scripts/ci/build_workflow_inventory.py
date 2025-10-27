#!/usr/bin/env python3
"""Build workflow inventory and documentation artifacts.

Outputs:
- reports/ci/workflows_matrix.json
- reports/ci/workflows_inventory.md
- reports/ci/workflows_gaps.md
- reports/ci/missing_secrets.md
- docs/WORKFLOWS_INDEX.md
- docs/RUNBOOK_CI.md

The script is deterministic; running it in CI allows detecting undocumented
workflow changes (via git diff).
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS_DIR = REPO_ROOT / '.github' / 'workflows'
OUTPUT_DIR = REPO_ROOT / 'reports' / 'ci'
DOCS_DIR = REPO_ROOT / 'docs'
DTC_PATH = DOCS_DIR / 'DOCUMENTO_DE_TRABAJO_CONTINUO_Pepecapiro.md'

WORKFLOW_DESCRIPTIONS: Dict[str, str] = {
    'api-automation-trigger.yml': 'Dispara pipelines externos vía API para sincronizaciones específicas.',
    'cleanup-test-posts.yml': 'Elimina contenido de prueba en el entorno remoto tras ejecuciones QA.',
    'content-ops.yml': 'Orquesta tareas de contenido (inventarios, validaciones y exportaciones).',
    'content-sync.yml': 'Publica contenido ES/EN en producción usando GitHub Actions (plan/apply).',
    'deploy.yml': 'Despliega el tema y assets principales hacia producción.',
    'external_links.yml': 'Verifica enlaces externos y reporta roturas.',
    'health-dashboard.yml': 'Genera el dashboard de salud general del sitio.',
    'hub-aggregation.yml': 'Agrega métricas desde servicios externos para informes consolidados.',
    'lighthouse.yml': 'Ejecuta auditorías Lighthouse en producción.',
    'lighthouse_cli.yml': 'Corre Lighthouse desde CLI para smoke tests rápidos.',
    'lighthouse_docs.yml': 'Genera informes Lighthouse en formato HTML y los publica en docs/.',
    'prune-runs.yml': 'Limpia ejecuciones antiguas de GitHub Actions para reducir ruido.',
    'psi_metrics.yml': 'Consulta PageSpeed Insights y guarda métricas históricas.',
    'publish-prod-menu.yml': 'Aplica cambios de menús en producción.',
    'publish-prod-page.yml': 'Publica páginas en producción (ES/EN).',
    'publish-prod-post.yml': 'Publica posts en producción (ES/EN).',
    'publish-test-menu.yml': 'Publica menús en entorno de prueba.',
    'publish-test-page.yml': 'Publica páginas en entorno de prueba.',
    'publish-test-post.yml': 'Publica posts en entorno de prueba.',
    'release.yml': 'Genera releases versionadas con artefactos finales.',
    'rollback.yml': 'Revierte un deployment de emergencia.',
    'rotate-app-password.yml': 'Asiste en la rotación del Application Password de WordPress.',
    'run-repair.yml': 'Reaplica contenido/ajustes para reparar drift detectado.',
    'runs-summary.yml': 'Resume ejecuciones recientes y publica un reporte.',
    'seo_audit.yml': 'Auditoría SEO técnica (hreflang, canonical, schema, etc.).',
    'set-home.yml': 'Configura la página inicial del sitio.',
    'site-health.yml': 'Ejecuta el informe de salud del sitio desde WP.',
    'site-settings.yml': 'Sincroniza configuraciones clave del sitio.',
    'smoke-tests.yml': 'Ejecución de smoke tests end-to-end.',
    'status.yml': 'Actualiza public/status.json con métricas actuales.',
    'upload-media.yml': 'Sincroniza assets multimedia optimizados.',
    'verify-home.yml': 'Smoke test para la portada (contenido + links).',
    'verify-media.yml': 'Verifica assets y referencias multimedia.',
    'verify-menus.yml': 'Comprueba consistencia de menús.',
    'verify-settings.yml': 'Valida settings críticos en WP.',
    'webhook-github-to-wp.yml': 'Entrega webhook hacia WordPress para acciones remotas.',
    'weekly-audit.yml': 'Auditoría semanal de drift y disparo de verificaciones clave.',
}

WORKFLOW_SECTION_MAP: Dict[str, str] = {
    'content-sync.yml': 'Fase 1 – Contenido Bilingüe',
    'publish-prod-post.yml': 'Fase 1 – Contenido Bilingüe',
    'publish-prod-page.yml': 'Fase 1 – Contenido Bilingüe',
    'publish-prod-menu.yml': 'Fase 1 – Contenido Bilingüe',
    'upload-media.yml': 'Fase 1 – Contenido Bilingüe',
    'verify-home.yml': 'QA y Auditoría Continua',
    'verify-media.yml': 'QA y Auditoría Continua',
    'verify-menus.yml': 'QA y Auditoría Continua',
    'verify-settings.yml': 'QA y Auditoría Continua',
    'lighthouse_docs.yml': 'Fase 4 – SEO/Performance',
    'lighthouse.yml': 'Fase 4 – SEO/Performance',
    'lighthouse_cli.yml': 'Fase 4 – SEO/Performance',
    'psi_metrics.yml': 'Fase 4 – SEO/Performance',
    'seo_audit.yml': 'Fase 4 – SEO/Performance',
    'site-health.yml': 'Monitoreo Técnico',
    'health-dashboard.yml': 'Monitoreo Técnico',
    'status.yml': 'Monitoreo Técnico',
    'weekly-audit.yml': 'Gobernanza y Auditorías',
    'run-repair.yml': 'Gobernanza y Auditorías',
    'rotate-app-password.yml': 'Seguridad y Accesos',
    'smoke-tests.yml': 'QA y Auditoría Continua',
    'deploy.yml': 'Operaciones / Releases',
    'release.yml': 'Operaciones / Releases',
    'rollback.yml': 'Operaciones / Releases',
    'set-home.yml': 'Operaciones / Releases',
    'site-settings.yml': 'Operaciones / Releases',
    'content-ops.yml': 'Operaciones de Contenido',
    'runs-summary.yml': 'Gobernanza y Auditorías',
    'prune-runs.yml': 'Gobernanza y Auditorías',
    'cleanup-test-posts.yml': 'QA y Auditoría Continua',
    'publish-test-post.yml': 'QA y Auditoría Continua',
    'publish-test-page.yml': 'QA y Auditoría Continua',
    'publish-test-menu.yml': 'QA y Auditoría Continua',
    'external_links.yml': 'Fase 4 – SEO/Performance',
    'api-automation-trigger.yml': 'Integraciones Externas',
    'webhook-github-to-wp.yml': 'Integraciones Externas',
    'hub-aggregation.yml': 'Integraciones Externas',
}

SECTION_ANCHORS: Dict[str, str] = {
    'Fase 1 – Contenido Bilingüe': 'Fase 1 – Limpieza y contenido bilingüe',
    'QA y Auditoría Continua': 'QA y Auditoría Continua',
    'Fase 4 – SEO/Performance': 'Fase 4 – SEO, OG, performance y accesibilidad',
    'Monitoreo Técnico': 'Publicación y Métricas',
    'Gobernanza y Auditorías': 'QA y Auditoría Continua',
    'Seguridad y Accesos': 'Integraciones y Monitoreo Externo',
    'Operaciones / Releases': 'Publicación y Métricas',
    'Operaciones de Contenido': 'Fase 1 – Limpieza y contenido bilingüe',
    'Integraciones Externas': 'Integraciones y Monitoreo Externo',
}

STANDARD_SECRETS = {
    'WP_URL', 'WP_USER', 'WP_APP_PASSWORD', 'WP_APP_PASSWORD_NEW', 'WP_PATH',
    'PSI_API_KEY', 'PSI_API_TOKEN', 'GSC_API_KEY', 'GSC_CLIENT_ID', 'GSC_CLIENT_SECRET',
    'GA_MEASUREMENT_ID', 'GA_API_SECRET', 'META_TOKEN', 'SMTP_PASSWORD',
    'HEALTH_API_TOKEN', 'LIGHTHOUSE_GH_TOKEN', 'WP_DEPLOY_KEY', 'GITHUB_TOKEN',
    'WP_HOST', 'WP_SFTP_PASSWORD', 'WP_SFTP_USER'
}

SECRET_REGEX = re.compile(r"secrets\.([A-Z0-9_]+)", re.IGNORECASE)
VAR_REGEX = re.compile(r"vars\.([A-Z0-9_]+)")


@dataclass
class WorkflowRecord:
    file: str
    name: str
    triggers: List[str]
    jobs: List[str]
    needs: Dict[str, List[str]]
    uses: Set[str]
    reusable_workflows: Set[str]
    secrets: Set[str]
    variables: Set[str]
    artifacts: List[str]
    outputs: Dict[str, List[str]]
    paths: List[str]
    dispatch_inputs: Dict[str, Dict[str, Any]]
    section: str
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            'file': self.file,
            'workflow_name': self.name,
            'triggers': self.triggers,
            'jobs': self.jobs,
            'needs': self.needs,
            'uses': sorted(self.uses),
            'reusable_workflows': sorted(self.reusable_workflows),
            'secrets': sorted(self.secrets),
            'variables': sorted(self.variables),
            'artifacts': self.artifacts,
            'outputs': self.outputs,
            'paths': self.paths,
            'dispatch_inputs': self.dispatch_inputs,
            'dtc_section': self.section,
            'description': self.description,
        }


def load_yaml(path: Path) -> Dict[Any, Any]:
    try:
        with path.open('r', encoding='utf-8') as handle:
            return yaml.safe_load(handle)
    except yaml.YAMLError as exc:  # pragma: no cover
        raise RuntimeError(f'No se pudo parsear {path}: {exc}')


def ensure_sorted(lines: List[str]) -> List[str]:
    return sorted(set(lines))


def _unique_preserve_order(items: Iterable[str]) -> List[str]:
    seen: Set[str] = set()
    ordered: List[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def summarize_triggers(on_field: Any) -> List[str]:
    if on_field is None:
        return []
    if isinstance(on_field, list):
        return _unique_preserve_order(str(item) for item in on_field)
    if isinstance(on_field, str):
        return [on_field]
    summary: List[str] = []
    if isinstance(on_field, dict):
        for event, value in on_field.items():
            if value is None:
                summary.append(event)
            elif isinstance(value, list):
                details = []
                for item in value:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            details.append(f"{k}:{v}")
                    else:
                        details.append(str(item))
                summary.append(f"{event}({'; '.join(details)})")
            elif isinstance(value, dict):
                details = []
                for k, v in value.items():
                    details.append(f"{k}:{v}")
                summary.append(f"{event}({'; '.join(details)})")
            else:
                summary.append(f"{event}:{value}")
    return _unique_preserve_order(summary)


def extract_paths(on_field: Any) -> List[str]:
    paths_ordered: List[str] = []
    if isinstance(on_field, dict):
        for event, value in on_field.items():
            if isinstance(value, dict):
                for key in ('paths', 'paths-ignore'):
                    if key in value:
                        entries = value[key]
                        if isinstance(entries, list):
                            for entry in entries:
                                paths_ordered.append(f"{event}:{key}:{entry}")
                        else:
                            paths_ordered.append(f"{event}:{key}:{entries}")
    return _unique_preserve_order(paths_ordered)


def collect_secrets(raw_text: str) -> Set[str]:
    return {match.group(1).upper() for match in SECRET_REGEX.finditer(raw_text)}


def collect_vars(raw_text: str) -> Set[str]:
    return {match.group(1).upper() for match in VAR_REGEX.finditer(raw_text)}


def collect_artifacts(jobs: Dict[str, Any]) -> List[str]:
    artifacts: List[str] = []
    for job_data in jobs.values():
        steps = job_data.get('steps', [])
        for step in steps or []:
            if isinstance(step, dict) and step.get('uses', '').startswith('actions/upload-artifact'):
                info = step.get('with', {})
                name = info.get('name', 'artifact') if isinstance(info, dict) else 'artifact'
                artifacts.append(name)
    return artifacts


def collect_uses(jobs: Dict[str, Any]) -> Tuple[Set[str], Set[str]]:
    uses: Set[str] = set()
    reusable: Set[str] = set()
    for job_name, job_data in jobs.items():
        if 'uses' in job_data and isinstance(job_data['uses'], str):
            reusable.add(job_data['uses'])
        steps = job_data.get('steps', [])
        for step in steps or []:
            if isinstance(step, dict) and 'uses' in step:
                uses.add(step['uses'])
    return uses, reusable


def collect_outputs(jobs: Dict[str, Any]) -> Dict[str, List[str]]:
    outputs: Dict[str, List[str]] = {}
    for job_name, job_data in jobs.items():
        job_outputs = job_data.get('outputs')
        if isinstance(job_outputs, dict):
            outputs[job_name] = list(job_outputs.keys())
    return outputs


def collect_dispatch_inputs(on_field: Any) -> Dict[str, Dict[str, Any]]:
    if not isinstance(on_field, dict):
        return {}
    dispatch = on_field.get('workflow_dispatch')
    if not isinstance(dispatch, dict):
        return {}
    inputs = dispatch.get('inputs')
    if not isinstance(inputs, dict):
        return {}
    result: Dict[str, Dict[str, Any]] = {}
    for name, data in inputs.items():
        if isinstance(data, dict):
            result[name] = {k: data.get(k) for k in ('description', 'default', 'required')}  # type: ignore[dict-item]
        else:
            result[name] = {'description': data}
    return result


def make_slug(file_name: str) -> str:
    return file_name.replace('.yml', '').replace('.yaml', '').replace('-', '_')


def map_section(file_name: str) -> str:
    return WORKFLOW_SECTION_MAP.get(file_name, 'Operaciones Generales')


def describe(file_name: str) -> str:
    return WORKFLOW_DESCRIPTIONS.get(file_name, 'Workflow sin descripción específica (añadir en WORKFLOW_DESCRIPTIONS).')


def parse_workflow(path: Path) -> WorkflowRecord:
    data = load_yaml(path)
    if not isinstance(data, dict):
        raise RuntimeError(f'{path} no contiene un workflow válido')
    workflow_name = data.get('name', path.stem)
    on_field = data.get('on')
    if on_field is None and True in data:
        on_field = data[True]
    triggers = summarize_triggers(on_field)
    jobs = data.get('jobs', {}) or {}
    job_names = list(jobs.keys())
    needs: Dict[str, List[str]] = {}
    for job_name, job_data in jobs.items():
        job_needs = job_data.get('needs')
        if isinstance(job_needs, list):
            needs[job_name] = job_needs
        elif isinstance(job_needs, str):
            needs[job_name] = [job_needs]
        else:
            needs[job_name] = []
    uses, reusable = collect_uses(jobs)
    raw_text = path.read_text(encoding='utf-8')
    secrets = collect_secrets(raw_text)
    variables = collect_vars(raw_text)
    artifacts = collect_artifacts(jobs)
    outputs = collect_outputs(jobs)
    paths = extract_paths(on_field)
    dispatch_inputs = collect_dispatch_inputs(on_field)
    section = map_section(path.name)
    description = describe(path.name)
    return WorkflowRecord(
        file=path.name,
        name=workflow_name,
        triggers=triggers,
        jobs=job_names,
        needs=needs,
        uses=uses,
        reusable_workflows=reusable,
        secrets=secrets,
        variables=variables,
        artifacts=artifacts,
        outputs=outputs,
        paths=paths,
        dispatch_inputs=dispatch_inputs,
        section=section,
        description=description,
    )


def build_inventory() -> List[WorkflowRecord]:
    records: List[WorkflowRecord] = []
    for path in sorted(WORKFLOWS_DIR.glob('*.y*ml')):
        records.append(parse_workflow(path))
    return records


def render_inventory_markdown(records: List[WorkflowRecord], generated_at: str, workflow_count: int, job_count: int) -> str:
    header = [
        '# Inventario de Workflows',
        f'Generado: {generated_at}',
        '',
        '| Archivo | Workflow | Eventos | Jobs | Needs | Uses | Secrets | Artefactos | Paths | Outputs |',
        '|---------|----------|---------|------|-------|------|---------|------------|-------|---------|',
    ]
    rows = []
    for record in records:
        needs_summary = []
        for job, deps in record.needs.items():
            if deps:
                needs_summary.append(f"{job}→{','.join(deps)}")
        row = ' | '.join([
            f'`{record.file}`',
            record.name,
            '<br>'.join(record.triggers) if record.triggers else '—',
            '<br>'.join(record.jobs) if record.jobs else '—',
            '<br>'.join(needs_summary) if needs_summary else '—',
            '<br>'.join(sorted(record.uses)) if record.uses else '—',
            '<br>'.join(sorted(record.secrets)) if record.secrets else '—',
            '<br>'.join(record.artifacts) if record.artifacts else '—',
            '<br>'.join(record.paths) if record.paths else '—',
            '<br>'.join(f"{job}:{','.join(outputs)}" for job, outputs in record.outputs.items()) if record.outputs else '—',
        ])
        rows.append(f"| {row} |")
    footer = [
        '',
        '## Cambios recientes',
        '',
        f'- Fecha: {generated_at}',
        f'- Workflows inventariados: {workflow_count}',
        f'- Jobs totales: {job_count}',
        '- Nota: Normalización de triggers/paths sin duplicados',
    ]
    return '\n'.join(header + rows + footer) + '\n'


def render_index(records: List[WorkflowRecord], generated_at: str) -> str:
    lines = [
        '# Índice de Workflows CI/CD',
        f'Generado: {generated_at}',
        '',
        'Este índice resume cada workflow disponible en `.github/workflows/`.',
        '',
    ]
    for record in records:
        lines.extend([
            f"## {record.name} — `{record.file}`",
            '',
            f"**Descripción:** {record.description}",
            f"**Disparadores:** {', '.join(record.triggers) if record.triggers else 'Manual / reusable'}",
            f"**Jobs:** {', '.join(record.jobs) if record.jobs else '—'}",
            f"**Artefactos:** {', '.join(record.artifacts) if record.artifacts else '—'}",
            f"**Secrets:** {', '.join(sorted(record.secrets)) if record.secrets else '—'}",
            f"**Sección DTC:** {record.section}",
            '',
            f"[Ver workflow](../.github/workflows/{record.file})",
            '',
        ])
    return '\n'.join(lines)


def render_runbook(records: List[WorkflowRecord], generated_at: str) -> str:
    lines = [
        '# Runbook CI/CD — Ejecución Manual',
        f'Generado: {generated_at}',
        '',
        'Guía para disparar manualmente cada workflow y revisar sus resultados.',
        '',
        '## Uso general',
        '- Ejecutar workflows manuales: `gh workflow run <archivo>`.',
        '- Para `workflow_dispatch` con inputs: `gh workflow run <archivo> --field clave=valor`.',
        '- Revisar estado: `gh run watch --exit-status` y artefactos vía `gh run download`.',
        '',
        '## Gestión de secrets',
        '- Ubicación: GitHub Actions (`Settings > Secrets and variables > Actions`) en `ppkapiro/pepecapiro-wp-theme`.',
        '- Responsables: equipo de operaciones/seguridad (propietarios del entorno Hostinger + WordPress); solicitar altas vía ticket interno.',
        '- Rotación: usar `rotate-app-password.yml` para credenciales WP y actualizar tokens externos (PSI, GA4, GSC) coordinando con `docs/SECURITY_NOTES.md`. Tras cada rotación, regenerar el inventario con `python scripts/ci/build_workflow_inventory.py` y validar `reports/ci/missing_secrets.md`.',
        '',
    ]
    for record in records:
        lines.extend([
            f"### {record.name} (`{record.file}`)",
            '',
            f"- **Propósito:** {record.description}",
            f"- **Disparadores:** {', '.join(record.triggers) if record.triggers else 'Solo manual / reusable'}",
        ])
        if record.dispatch_inputs:
            inputs_detail = ', '.join(f"{name}(default={data.get('default', '∅')})" for name, data in record.dispatch_inputs.items())
            lines.append(f"- **Inputs `workflow_dispatch`:** {inputs_detail}")
        if record.artifacts:
            lines.append(f"- **Artefactos clave:** {', '.join(record.artifacts)}")
        if record.secrets:
            lines.append(f"- **Secrets requeridos:** {', '.join(sorted(record.secrets))}")
        lines.append(f"- **Sección DTC relacionada:** {record.section}")
        lines.append('')
        lines.append(f"Comando sugerido: `gh workflow run {record.file}`")
        lines.append('')
    return '\n'.join(lines)


def render_missing_secrets(records: List[WorkflowRecord], generated_at: str) -> str:
    secrets_by_workflow = {record.file: sorted(record.secrets) for record in records if record.secrets}
    all_secrets: Set[str] = set()
    for secrets in secrets_by_workflow.values():
        all_secrets.update(secrets)
    unknown = sorted(secret for secret in all_secrets if secret not in STANDARD_SECRETS)
    unused_standard = sorted(secret for secret in STANDARD_SECRETS if secret not in all_secrets)
    lines = [
        '# Estado de Secrets en Workflows',
        f'Generado: {generated_at}',
        '',
        '## Secrets por workflow',
    ]
    if secrets_by_workflow:
        for file, secrets in sorted(secrets_by_workflow.items()):
            lines.append(f"- `{file}`: {', '.join(secrets)}")
    else:
        lines.append('- Ningún workflow refiere secrets. (Verificar)')
    lines.extend([
        '',
        '## Estado por secret',
    ])
    if all_secrets:
        for secret in sorted(all_secrets):
            status = '**OK**' if secret in STANDARD_SECRETS else '**FALTANTE** (nomenclatura no estándar)'
            lines.append(f'- `{secret}`: {status}')
    else:
        lines.append('- No se detectaron secrets en los workflows.')
    lines.extend([
        '',
        '## Secrets estándar no referenciados',
        '- ' + (', '.join(unused_standard) if unused_standard else 'Todos en uso'),
        '',
        '## Observaciones',
        f'- Secrets no estándar detectados: {", ".join(unknown) if unknown else "Ninguno"}',
        '- Actualiza la nomenclatura o documenta los nombres de infraestructura cuando aplique.',
    ])
    return '\n'.join(lines)


def compute_gaps(records: List[WorkflowRecord], generated_at: str) -> str:
    dtc_text = ''
    if DTC_PATH.is_file():
        dtc_text = DTC_PATH.read_text(encoding='utf-8')
    missing_in_dtc = []
    for record in records:
        if record.file not in dtc_text and record.name not in dtc_text:
            missing_in_dtc.append(record.file)
    sections_with_workflow: Dict[str, Set[str]] = defaultdict(set)
    for record in records:
        sections_with_workflow[record.section].add(record.file)
    missing_sections = []
    for section, anchor in SECTION_ANCHORS.items():
        if section not in sections_with_workflow or not sections_with_workflow[section]:
            missing_sections.append((section, anchor))
    all_secrets = {secret for record in records for secret in record.secrets}
    non_standard = sorted(secret for secret in all_secrets if secret not in STANDARD_SECRETS)
    unused_standard = sorted(secret for secret in STANDARD_SECRETS if secret not in all_secrets)
    lines = [
        '# Brechas entre Workflows y DTC',
        f'Generado: {generated_at}',
        '',
        '## Workflows sin mención en el DTC',
    ]
    if missing_in_dtc:
        for file in missing_in_dtc:
            lines.append(f'- {file}')
    else:
        lines.append('- Todos los workflows tienen referencia en el DTC (verificar cohesión).')
    lines.extend([
        '',
        '## Secciones del DTC sin workflow asignado',
    ])
    if missing_sections:
        for section, anchor in missing_sections:
            lines.append(f'- {section} (buscar referencia en sección "{anchor}")')
    else:
        lines.append('- Todas las secciones principales están cubiertas por al menos un workflow.')
    lines.extend([
        '',
        '## Secrets y nomenclatura',
    ])
    if non_standard or unused_standard:
        if non_standard:
            lines.append(f'- Secrets no estándar en uso: {", ".join(non_standard)}')
        if unused_standard:
            lines.append(f'- Secrets estándar aún no referenciados: {", ".join(unused_standard)}')
    else:
        lines.append('- Nomenclatura normalizada y sin pendientes.')
    return '\n'.join(lines)


def main() -> int:
    records = build_inventory()
    generated_at = datetime.utcnow().isoformat() + 'Z'
    workflow_count = len(records)
    job_count = sum(len(record.jobs) for record in records)
    matrix = {
        'generated_at': generated_at,
        'workflow_count': len(records),
        'workflows': [record.to_dict() for record in records],
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / 'workflows_matrix.json').write_text(json.dumps(matrix, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (OUTPUT_DIR / 'workflows_inventory.md').write_text(render_inventory_markdown(records, generated_at, workflow_count, job_count), encoding='utf-8')
    (OUTPUT_DIR / 'workflows_gaps.md').write_text(compute_gaps(records, generated_at), encoding='utf-8')
    (OUTPUT_DIR / 'missing_secrets.md').write_text(render_missing_secrets(records, generated_at), encoding='utf-8')
    (DOCS_DIR / 'WORKFLOWS_INDEX.md').write_text(render_index(records, generated_at), encoding='utf-8')
    (DOCS_DIR / 'RUNBOOK_CI.md').write_text(render_runbook(records, generated_at), encoding='utf-8')
    print('[ok] Inventario de workflows actualizado.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
