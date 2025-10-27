# 🔍 Workflows Health Report

**Generated**: 2025-10-27T18:05:25.512984

## Summary

| Metric | Count |
|--------|-------|
| **Total workflows** | 39 |
| **Valid YAML** | 39 |
| **With workflow_dispatch** | 38 |
| **Disabled (remote)** | 0 |
| **Sync Issues** | 0 |

## Status

✅ **All workflows synced**: Local and remote inventories match (0 only-local, 0 only-remote)

✅ **YAML Validation**: All 39/39 workflows parse correctly

✅ **Manual Trigger**: 38/39 workflows have workflow_dispatch

✅ **Remote State**: 39/39 workflows active

## Details

See full inventories:
- [workflows_local.json](workflows_local.json) — Local YAML parse with feature detection
- [workflows_remote.json](workflows_remote.json) — GitHub API snapshot
- [workflows_diff.md](workflows_diff.md) — Cross-check report

## Notes

- PyYAML parses unquoted `on:` as boolean `True` (not string key "on")
- Detection logic accounts for both `data.get('on')` and `data.get(True)`
