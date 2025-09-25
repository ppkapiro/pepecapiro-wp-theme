# WordPress Post-Launch: 7 High-Impact Actions in the First 7 Days

A newly launched site is usually “fine” but rarely resilient or performance-focused. This guide prioritizes high-leverage steps (defense, performance, observability, governance) before scaling content or traffic.

## 1. Harden access surface
**Problem:** Predictable login endpoint + weak credentials invite automated attacks.
**Action:** Enforce strong passwords, enable 2FA for privileged roles, limit attempts (fail2ban / rate limiting), optionally shield `/wp-admin` behind WAF/IP rules.
**Outcome:** Reduced brute-force noise and lower risk footprint.

## 2. Freeze and prune plugins
**Problem:** Plugin bloat increases attack surface, DB queries, update pressure.
**Action:** Inventory → classify (core / essential / removable). Remove optional plugins. Document decisions in version control.
**Outcome:** Lower TTFB, fewer CVEs to track, simpler patch cadence.

## 3. Caching & critical asset policy
**Problem:** Slow first render and static assets without explicit caching.
**Action:** Enable page cache (and object cache if useful), set proper `cache-control` for CSS/JS/images with hashed filenames, selectively `preload` only truly critical fonts.
**Outcome:** Better LCP and lighter server load under peaks.

## 4. Minimum performance observability
**Problem:** Regressions only visible after user complaints.
**Action:** Run automated Lighthouse + PSI collection (already in pipeline), define thresholds in `perf_thresholds.json`, keep history + auto-issue escalation.
**Outcome:** Data-driven iteration path and early warning.

## 5. Media discipline & deduplication
**Problem:** Duplicate uploads inflate storage and backup time.
**Action:** Hash-based dedup (`.media_map.json`), naming conventions, consider CDN when scaling. Periodically review reuse report.
**Outcome:** Lean library and faster backup cycles.

## 6. Configuration hardening & quick scan
**Problem:** Default config leaves lateral risk vectors.
**Action:** Ensure `DISALLOW_FILE_EDIT`, valid salts, forced HTTPS, remove/deny leftover installer files. Run an external scan (e.g. wpscan) and log findings.
**Outcome:** Solid baseline aligned with practical security hygiene.

## 7. Codified publishing workflow
**Problem:** Manual panel edits create silent drift and inconsistencies.
**Action:** Adopt repository-driven content: plan/apply, preflight gates (links, taxonomies, completeness), performance soft gating, auto-issues.
**Outcome:** Predictable, auditable and low-friction operations.

## Quick Checklist
- [ ] 2FA + rate limited login
- [ ] Plugin inventory & bloat removed
- [ ] Page/object cache + static cache headers
- [ ] PSI thresholds defined & monitored
- [ ] Media dedup reuse tracked
- [ ] Config hardened (salts, HTTPS, file edit off)
- [ ] Automated publish pipeline in place

## Key Metrics to Watch
- Mobile LCP (target < 2.5s, ideal < 2.0s)
- CLS (< 0.1 stable)
- Media reuse ratio trending upward
- Zero unexpected content drift
- Consecutive threshold failures (avoid escalation)

## Next Step
After week one: advance technical SEO (JSON-LD, hreflang) and introduce light load testing.

---
*Part of the continuous governance & automation series.*
