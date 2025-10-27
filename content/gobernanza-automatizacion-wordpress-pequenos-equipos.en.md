# Governance and Automation of WordPress for Small Teams

> How to maintain speed without losing control when there are only 1–3 people.

## Executive Summary
The key: explicitly decide what you will NOT do yet. A lightweight framework of 5 pillars allows for growth with less fire.

## 1. Code and Assets
- Single repository for the theme + scripts
- Semantic versioning (disciplined CHANGELOG)
- Small commits → small deployments
- Controlled critical assets like fonts, images, and CSS (do not rely on arbitrary CDNs)

## 2. Content
- Automate idempotent creation (bilingual posts/pages) via API
- Versioned source Markdown → reproducibility
- Stable slugs, avoid renaming
- Audit: script compares content hash

## 3. Deliveries and CI
- Pipeline: build -> validations -> deploy
- Health checks: blog page ready, detectable markers
- Packaged releases (.zip + .sha256)
- Quick review: scheduled Lighthouse

## 4. Lightweight Observability
- Retained deployment logs
- Minimum metric: home/blog response time
- Health check CRON (HTTP 200 + posts_found)
- Alerts only on critical failures

## 5. Risk and Changes
- Rule of “1 functional change per release” when there is uncertainty
- Simple feature flags (WP options + theme conditionals)
- Verified daily automatic backups
- Rollback policy: reinstall previously verified zip

## Proposed Daily Workflow
1. Create short branch (feature/blog-categories)
2. Adjust + markdown content
3. Run publication script (idempotent)
4. Review health + Lighthouse
5. Merge + tag version
6. Automatic deploy

## Initial Health Metrics
| Metric | Goal | Frequency |
|--------|----------|------------|
| TTFB Time | < 600ms | Daily |
| Mobile Lighthouse | ≥ 90 | Weekly |
| Health check failures | 0 | Continuous |
| Failed releases | 0 | Per release |

## Key Anti-Pattern
“I upload manual changes via FTP” → not auditable, not reversible, not scalable.

## Next Increments
- Lightweight visual testing (basic diff screenshots)
- Object cache (Redis) if complexity increases
- Synthetic form monitoring

---
Governance is not bureaucracy: it is reducing future friction by documenting minimal decisions now.