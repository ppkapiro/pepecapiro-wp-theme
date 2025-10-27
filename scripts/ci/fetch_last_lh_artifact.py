#!/usr/bin/env python3
"""
Fetch last Lighthouse workflow run artifact (assert_summary.txt) and generate Markdown report.
Usage: python3 scripts/ci/fetch_last_lh_artifact.py [--workflow lighthouse.yml] [--branch main]
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
    """Run shell command and return stdout."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
    return result.stdout.strip()


def get_last_run(workflow, branch):
    """Get the last workflow run ID for the given workflow and branch."""
    cmd = f'gh run list --workflow={workflow} --branch={branch} --limit=1 --json databaseId,conclusion,createdAt'
    output = run_cmd(cmd)
    if not output:
        print(f"[error] No runs found for workflow {workflow} on branch {branch}", file=sys.stderr)
        sys.exit(1)
    runs = json.loads(output)
    if not runs:
        print(f"[error] No runs found for workflow {workflow} on branch {branch}", file=sys.stderr)
        sys.exit(1)
    return runs[0]


def download_artifact(run_id, artifact_name, dest_dir):
    """Download artifact from workflow run."""
    dest_path = Path(dest_dir)
    dest_path.mkdir(parents=True, exist_ok=True)
    
    # Download artifact as zip
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / f"{artifact_name}.zip"
        cmd = f'gh run download {run_id} --name {artifact_name} --dir {tmpdir}'
        try:
            run_cmd(cmd)
        except subprocess.CalledProcessError as e:
            print(f"[error] Failed to download artifact {artifact_name}: {e}", file=sys.stderr)
            return None
        
        # Find assert_summary.txt in downloaded files
        summary_file = None
        for root, dirs, files in os.walk(tmpdir):
            if 'assert_summary.txt' in files:
                summary_file = Path(root) / 'assert_summary.txt'
                break
        
        if not summary_file or not summary_file.exists():
            print(f"[warn] assert_summary.txt not found in artifact {artifact_name}", file=sys.stderr)
            return None
        
        # Copy to destination
        dest_file = dest_path / 'assert_summary_last.txt'
        dest_file.write_text(summary_file.read_text())
        print(f"[OK] Downloaded {summary_file} -> {dest_file}")
        return dest_file


def parse_assert_summary(summary_file):
    """Parse assert_summary.txt and extract metrics."""
    lines = summary_file.read_text().splitlines()
    results = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('===') or line.startswith('[warn]') or line.startswith('[error]'):
            continue
        
        # Parse lines like: "- home: mobile performance 89 < 90"
        if line.startswith('- '):
            parts = line[2:].split(':', 1)
            if len(parts) == 2:
                page = parts[0].strip()
                issue = parts[1].strip()
                
                # Determine device (mobile/desktop)
                device = 'mobile' if 'mobile' in issue else 'desktop'
                
                # Parse metric, value, threshold
                if 'performance' in issue:
                    metric = 'Performance'
                    # Extract "89 < 90"
                    if '<' in issue:
                        val_thresh = issue.split('performance')[1].strip().split('<')
                        value = val_thresh[0].strip()
                        threshold = val_thresh[1].strip()
                    else:
                        value = '?'
                        threshold = '?'
                elif 'LCP' in issue:
                    metric = 'LCP'
                    # Extract "2600ms > 2500ms"
                    if '>' in issue:
                        val_thresh = issue.split('LCP')[1].strip().split('>')
                        value = val_thresh[0].strip()
                        threshold = val_thresh[1].strip()
                    else:
                        value = '?'
                        threshold = '?'
                elif 'CLS' in issue:
                    metric = 'CLS'
                    # Extract "0.12 > 0.1"
                    if '>' in issue:
                        val_thresh = issue.split('CLS')[1].strip().split('>')
                        value = val_thresh[0].strip()
                        threshold = val_thresh[1].strip()
                    else:
                        value = '?'
                        threshold = '?'
                else:
                    metric = 'Unknown'
                    value = '?'
                    threshold = '?'
                
                results.append({
                    'page': page,
                    'device': device,
                    'metric': metric,
                    'value': value,
                    'threshold': threshold,
                    'status': '❌ FAIL'
                })
    
    return results


def generate_markdown_report(results, output_file):
    """Generate Markdown report from parsed results."""
    md_lines = [
        "# Lighthouse Assert Summary (Last Run)",
        "",
        f"**Generated:** {__import__('datetime').datetime.now().isoformat()}",
        "",
        "## Failed Metrics",
        "",
        "| Page | Device | Metric | Value | Threshold | Status |",
        "|------|--------|--------|-------|-----------|--------|"
    ]
    
    if not results:
        md_lines.append("| — | — | — | — | — | ✅ ALL PASS |")
    else:
        for r in results:
            md_lines.append(
                f"| {r['page']} | {r['device']} | {r['metric']} | "
                f"{r['value']} | {r['threshold']} | {r['status']} |"
            )
    
    md_lines.extend([
        "",
        "## Summary",
        "",
        f"- **Total failures:** {len(results)}",
        f"- **Mobile failures:** {sum(1 for r in results if r['device'] == 'mobile')}",
        f"- **Desktop failures:** {sum(1 for r in results if r['device'] == 'desktop')}",
        "",
        "## Next Steps",
        "",
        "1. Extract failing mobile URLs → `reports/psi/failing_urls.txt`",
        "2. Run PSI diagnostics per URL → `scripts/psi/diagnose_url.py`",
        "3. Apply LCP/CLS/JS optimizations",
        "4. Re-run Lighthouse and validate PASS",
        ""
    ])
    
    output_file.write_text('\n'.join(md_lines))
    print(f"[OK] Markdown report generated: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Fetch last Lighthouse artifact and generate report')
    parser.add_argument('--workflow', default='lighthouse.yml', help='Workflow file name')
    parser.add_argument('--branch', default='main', help='Branch name')
    args = parser.parse_args()
    
    print(f"[INFO] Fetching last run for workflow {args.workflow} on branch {args.branch}...")
    last_run = get_last_run(args.workflow, args.branch)
    run_id = last_run['databaseId']
    conclusion = last_run['conclusion']
    created_at = last_run['createdAt']
    
    print(f"[INFO] Last run: {run_id} (conclusion: {conclusion}, created: {created_at})")
    
    # Download artifact
    dest_dir = Path.cwd() / 'reports' / 'psi'
    summary_file = download_artifact(run_id, 'lighthouse_reports', dest_dir)
    
    if not summary_file:
        print("[error] Could not download assert_summary.txt; workflow may not have generated it", file=sys.stderr)
        sys.exit(1)
    
    # Parse and generate report
    results = parse_assert_summary(summary_file)
    md_file = dest_dir / 'assert_summary_last.md'
    generate_markdown_report(results, md_file)
    
    print(f"\n[SUCCESS] Artifact fetched and report generated:")
    print(f"  - Raw: {summary_file}")
    print(f"  - Markdown: {md_file}")
    print(f"  - Failures: {len(results)}")


if __name__ == '__main__':
    main()
