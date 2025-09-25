# WordPress Governance & Automation for Very Small Teams

> How to keep shipping fast with only 1–3 people without burning out.

## Executive Summary
Discipline = choosing what NOT to build yet. A lightweight 5‑pillar frame preserves speed and control.

## 1. Code & Assets
- Single repo for theme + scripts
- Semantic versioning (disciplined CHANGELOG)
- Small commits → small deploy blast radius
- Fonts, key images, and CSS self-hosted (limit random CDNs)

## 2. Content
- Idempotent API publishing (bilingual posts/pages)
- Versioned Markdown sources → reproducibility
- Stable slugs; avoid renames
- Audit: script can hash + compare content

## 3. Delivery & CI
- Pipeline: build -> validations -> deploy
- Health checks: blog listing markers
- Packaged releases (.zip + .sha256)
- Scheduled Lighthouse run

## 4. Lightweight Observability
- Retain deploy logs
- Minimum metric: response time home/blog
- CRON health check (HTTP 200 + posts_found marker)
- Alerts only for critical failures

## 5. Risk & Change
- Rule: “1 functional risk per release” under uncertainty
- Simple feature flags (WP options + theme conditionals)
- Verified daily backups
- Rollback: re-install prior verified zip

## Proposed Daily Flow
1. Short branch (feature/blog-categories)
2. Adjust + add markdown content
3. Run publish script (idempotent)
4. Check health + Lighthouse
5. Merge + tag
6. Auto deploy

## Initial Health Metrics
| Metric | Target | Frequency |
|--------|--------|-----------|
| TTFB | < 600ms | Daily |
| Lighthouse mobile | ≥ 90 | Weekly |
| Health check failures | 0 | Continuous |
| Failed releases | 0 | Per release |

## Key Anti-Pattern
“Manual FTP tweaks” → not auditable, not reversible, not scalable.

## Next Increments
- Lightweight visual regression (screenshot diff)
- Object cache (Redis) when complexity grows
- Synthetic form monitor

---
Governance isn’t bureaucracy: it’s reducing future friction by capturing minimal present decisions.
