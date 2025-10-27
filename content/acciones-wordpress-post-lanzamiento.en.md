# WordPress Post-Launch: 7 Key Actions in the First 7 Days

A newly published site is often "correct" but not optimized. This checklist prioritizes high-impact actions (security, performance, observability, and governance) that solidify the foundation before scaling content or traffic.

## 1. Harden Access Surface
**Problem:** Unnecessary exposure of login and weak credentials.  
**Action:** Enforce strong passwords, enable 2FA for high-role accounts, limit login attempts (fail2ban/Nginx rate limit), and move `/wp-admin` behind a WAF/IP rule if feasible.  
**Result:** Reduced automated attack vectors and decreased noise in logs.

## 2. Freeze Unnecessary Plugins and Clean Up
**Problem:** Bloat = more surface area, more queries, more vulnerabilities.  
**Action:** Inventory → classify (core, essential, dispensable). Deactivate and remove what is dispensable. Document decisions in version control (README section plugins/justification).  
**Result:** Lower TTFB, fewer potential CVEs, simpler update cycle.

## 3. Cache and Critical Asset Policy
**Problem:** Slow initial load and static resources without clear expiration.  
**Action:** Enable page cache (Object cache if applicable), define `cache-control` headers for CSS/JS/images (hash in filename), evaluate preloading critical fonts (`preload`) only if it measurably reduces LCP.  
**Result:** Improved LCP and reduced server load during peaks.

## 4. Minimum Observability and Performance Metrics
**Problem:** Failing to detect regressions until they are visible to users.  
**Action:** Set up Lighthouse + PSI pipeline (already integrated) and establish explicit thresholds (`perf_thresholds.json`). Maintain historical data and enable auto-issues.  
**Result:** Early detection and a foundation for data-driven decisions.

## 5. Content and Media Protection
**Problem:** Duplicate uploads and unversioned media cause chaos and excessive backup size.  
**Action:** Use hash deduplication (`.media_map.json`), naming conventions, CDN alternatives if scaling. Periodically review the reuse report.  
**Result:** Clean library + faster backups.

## 6. Configuration Hardening and Quick Scan
**Problem:** Initial configuration without file validation or integrity checks.  
**Action:** Verify `DISALLOW_FILE_EDIT`, secure salts, enforce HTTPS, check for residual installation files (`wp-admin/install.php` blocked). Conduct a quick scan with an external tool (wpscan or similar) and document findings.  
**Result:** Foundation aligned with best practices and verifiable documentation.

## 7. Define Automated Publishing Cycle
**Problem:** Manual changes in the dashboard create hard-to-track divergences.  
**Action:** Consolidate “content as code” (this repo): plan/apply, preflight gates (links, taxonomies, completeness), soft gating performance, and auto-issues.  
**Result:** Predictable, auditable, and scalable operation with minimal human capital.

## Quick Checklist
- [ ] 2FA and rate limit login
- [ ] Inventoried plugins and bloat removed
- [ ] Cache + static headers active
- [ ] PSI thresholds defined and monitored
- [ ] Media deduplicated and report reviewed
- [ ] Hardened config (salts, HTTPS, file edit off)
- [ ] Publishing pipeline without ad-hoc manual actions

## Key Metrics to Monitor
- Mobile LCP (target < 2.5s, ideal < 2.0s)
- CLS (< 0.1 consistent)
- Media reuse (increasing ratio)
- Content drift (0 unexpected)
- Consecutive runs with threshold failures (avoid scaling)

## Next Step
After these 7 days, focus on advanced technical SEO (JSON-LD, hreflang) and light load testing.

---
*This article is part of the site's governance and continuous automation series.*