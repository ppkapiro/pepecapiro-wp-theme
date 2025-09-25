# WordPress Governance & Automation for Small Teams

> Sustain delivery speed with control when you are just 1–3 people.

## Executive Summary
Decide explicitly what you will NOT tackle yet. A lightweight 5‑pillar frame keeps fires down.

## 1. Code & Assets
- Single repo (theme + scripts)
- Semantic versioning (disciplined CHANGELOG)
- Small commits → small deploys
- Fonts, key images & CSS under version control (avoid random CDNs)

## 2. Content
- Idempotent creation (bilingual posts/pages) through API
- Markdown as source → reproducibility
- Stable slugs; avoid renames
- Audit script can diff content hash

## 3. Delivery & CI
- Pipeline: build -> validations -> deploy
- Health checks: blog page ready, detectable markers
- Packaged releases (.zip + .sha256)
- Fast review: scheduled Lighthouse

## 4. Lightweight Observability
- Deployment logs retained
- Minimum metric: home/blog response time
- CRON health check (HTTP 200 + posts_found)
- Alerts only on critical failures

## 5. Risk & Change
- "One functional change per release" rule when uncertain
- Simple feature flags (WP options + theme conditionals)
- Verified daily backups
- Rollback policy: reinstall last verified zip

## Daily Flow
1. Short-lived branch (feature/blog-categories)
2. Change + content markdown
3. Run publication script (idempotent)
4. Review health + Lighthouse
5. Merge + tag version
6. Automatic deploy

## Initial Health Metrics
| Metric | Target | Frequency |
|--------|--------|-----------|
| TTFB | < 600ms | Daily |
| Lighthouse mobile | ≥ 90 | Weekly |
| Health check failures | 0 | Continuous |
| Failed releases | 0 | Per release |

## Key Anti-Pattern
"I upload manual FTP changes" → not auditable, not reversible, not scalable.

## Next Increments
- Light visual diff test
- Object cache (Redis) if complexity grows
- Synthetic monitoring for contact form

---
Governance ≠ bureaucracy: it's minimizing future friction by documenting minimal decisions now.
