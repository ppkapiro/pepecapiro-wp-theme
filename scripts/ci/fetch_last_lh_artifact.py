#!/usr/bin/env python3
"""
Fetch last Lighthouse workflow run artifact (assert_summary.txt) and generate Markdown report.
Usage: python3 scripts/ci/fetch_last_lh_artifact.py [--workflow lighthouse.yml] [--branch main]
- First tries GitHub CLI (gh run download)
- If it fails, falls back to GitHub REST API using GH_TOKEN / GITHUB_TOKEN
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def run_cmd(cmd, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout + result.stderr)
    return result.stdout.strip()


def get_repo_slug():
    # Try env
    repo = os.getenv('GITHUB_REPOSITORY')
    if repo:
        return repo
    # Try git remote
    try:
        url = run_cmd('git config --get remote.origin.url')
        # Examples: https://github.com/owner/repo.git or git@github.com:owner/repo.git
        url = url.replace('.git', '')
        if url.startswith('git@github.com:'):
            return url.split(':', 1)[1]
        if 'github.com/' in url:
            return url.split('github.com/', 1)[1]
    except Exception:
        pass
    return None


def get_last_run(workflow, branch):
    output = run_cmd(f'gh run list --workflow={workflow} --branch={branch} --limit=1 --json databaseId,conclusion,createdAt')
    runs = json.loads(output) if output else []
    if not runs:
        print(f"[error] No runs found for workflow {workflow} on branch {branch}", file=sys.stderr)
        sys.exit(1)
    return runs[0]


def try_cli_download(run_id, artifact_name, tmpdir):
    try:
        run_cmd(f'gh run download {run_id} --name {artifact_name} --dir {tmpdir}')
        return True
    except subprocess.CalledProcessError as e:
        print(f"[warn] gh run download failed: {e}", file=sys.stderr)
        return False


def api_download_artifact(run_id, artifact_name, tmpdir):
    token = os.getenv('GH_TOKEN') or os.getenv('GITHUB_TOKEN')
    if not token:
        print('[error] GH_TOKEN/GITHUB_TOKEN not set for API fallback', file=sys.stderr)
        return False
    repo = get_repo_slug()
    if not repo:
        print('[error] Could not determine repo slug for API fallback', file=sys.stderr)
        return False
    base = f'https://api.github.com/repos/{repo}'
    list_cmd = (
        f"curl -sSfL -H 'Authorization: Bearer {token}' "
        f"-H 'Accept: application/vnd.github+json' "
        f"{base}/actions/runs/{run_id}/artifacts"
    )
    try:
        raw = run_cmd(list_cmd)
        data = json.loads(raw)
    except Exception as e:
        print(f'[error] API list artifacts failed: {e}', file=sys.stderr)
        return False
    arts = data.get('artifacts', [])
    target = None
    for a in arts:
        if a.get('name') == artifact_name:
            target = a
            break
    if not target:
        print(f"[error] Artifact '{artifact_name}' not found in run {run_id}", file=sys.stderr)
        return False
    dl_url = target.get('archive_download_url')
    if not dl_url:
        print('[error] No archive_download_url in artifact', file=sys.stderr)
        return False
    zip_path = Path(tmpdir) / f'{artifact_name}.zip'
    dl_cmd = (
        f"curl -sSfL -H 'Authorization: Bearer {token}' "
        f"-H 'Accept: application/vnd.github+json' "
        f"-o '{zip_path}' '{dl_url}'"
    )
    try:
        run_cmd(dl_cmd)
    except subprocess.CalledProcessError as e:
        print(f'[error] API download failed: {e}', file=sys.stderr)
        return False
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(tmpdir)
        return True
    except Exception as e:
        print(f'[error] Unzip failed: {e}', file=sys.stderr)
        return False


def download_summary_from(tmpdir, dest_dir):
    summary_file = None
    for root, _, files in os.walk(tmpdir):
        if 'assert_summary.txt' in files:
            summary_file = Path(root) / 'assert_summary.txt'
            break
    if not summary_file or not summary_file.exists():
        print('[warn] assert_summary.txt not found in downloaded artifact', file=sys.stderr)
        return None
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / 'assert_summary_last.txt'
    dest_file.write_text(summary_file.read_text())
    print(f"[OK] Downloaded {summary_file} -> {dest_file}")
    return dest_file


def parse_assert_summary(summary_file):
    lines = summary_file.read_text().splitlines()
    results = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('===') or line.startswith('[warn]') or line.startswith('[error]'):
            continue
        if line.startswith('- '):
            parts = line[2:].split(':', 1)
            if len(parts) != 2:
                continue
            page = parts[0].strip()
            issue = parts[1].strip()
            device = 'mobile' if 'mobile' in issue else 'desktop'
            if 'performance' in issue:
                metric = 'Performance'
                if '<' in issue:
                    val, thr = issue.split('performance', 1)[1].split('<', 1)
                    value = val.strip()
                    threshold = thr.strip()
                else:
                    value = '?'; threshold = '?'
            elif 'LCP' in issue:
                metric = 'LCP'
                if '>' in issue:
                    val, thr = issue.split('LCP', 1)[1].split('>', 1)
                    value = val.strip()
                    threshold = thr.strip()
                else:
                    value = '?'; threshold = '?'
            elif 'CLS' in issue:
                metric = 'CLS'
                if '>' in issue:
                    val, thr = issue.split('CLS', 1)[1].split('>', 1)
                    value = val.strip()
                    threshold = thr.strip()
                else:
                    value = '?'; threshold = '?'
            else:
                metric = 'Unknown'; value = '?'; threshold = '?'
            results.append({'page': page, 'device': device, 'metric': metric, 'value': value, 'threshold': threshold, 'status': '❌ FAIL'})
    return results


def generate_markdown_report(results, output_file):
    md_lines = [
        '# Lighthouse Assert Summary (Last Run)',
        '',
        f"**Generated:** {__import__('datetime').datetime.now().isoformat()}",
        '',
        '## Failed Metrics',
        '',
        '| Page | Device | Metric | Value | Threshold | Status |',
        '|------|--------|--------|-------|-----------|--------|'
    ]
    if not results:
        md_lines.append('| — | — | — | — | — | ✅ ALL PASS |')
    else:
        for r in results:
            md_lines.append(f"| {r['page']} | {r['device']} | {r['metric']} | {r['value']} | {r['threshold']} | {r['status']} |")
    output_file.write_text('\n'.join(md_lines) + '\n')
    print(f"[OK] Markdown report generated: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Fetch last Lighthouse artifact and generate report')
    parser.add_argument('--workflow', default='lighthouse.yml', help='Workflow file name')
    parser.add_argument('--branch', default='main', help='Branch name')
    args = parser.parse_args()

    print(f"[INFO] Fetching last run for workflow {args.workflow} on branch {args.branch}...")
    last_run = get_last_run(args.workflow, args.branch)
    run_id = last_run['databaseId']
    conclusion = last_run.get('conclusion')
    created_at = last_run.get('createdAt')
    print(f"[INFO] Last run: {run_id} (conclusion: {conclusion}, created: {created_at})")

    dest_dir = Path.cwd() / 'reports' / 'psi'
    with tempfile.TemporaryDirectory() as tmpdir:
        ok = try_cli_download(run_id, 'lighthouse_reports', tmpdir)
        if not ok:
            print('[INFO] Falling back to GitHub API download...')
            ok = api_download_artifact(run_id, 'lighthouse_reports', tmpdir)
        if not ok:
            print('[error] Could not download artifact via CLI nor API', file=sys.stderr)
            sys.exit(1)
        summary_file = download_summary_from(tmpdir, dest_dir)
        if not summary_file:
            print('[error] assert_summary.txt not found in artifact', file=sys.stderr)
            sys.exit(2)

    results = parse_assert_summary(summary_file)
    md_file = dest_dir / 'assert_summary_last.md'
    generate_markdown_report(results, md_file)
    print('SUCCESS: Artifact fetched and report generated')


if __name__ == '__main__':
    main()
