# WordPress Second Week: Priority Hardening & Stabilization

You survived the launch window. Now you lock things down, add minimal visibility, and set a sustainable baseline.

## Phase Objectives
1. Reduce exposed surface.
2. Gain minimal monitoring signals.
3. Remove residue that may hurt performance.
4. Prepare a content pipeline.

## 1. Accounts & Roles Review
- Remove temporary launch users.
- Trim excess administrators.
- Enforce password updates for weak credentials.

## 2. Endpoints and XML-RPC
- Disable XML-RPC if no mobile/app integrations required.
- Limit sensitive REST endpoints (security plugin or WAF rules).

## 3. Consistent Backups
- Schedule daily incremental + weekly full.
- Test a partial restore (e.g. `wp_options` table) to prove validity.

## 4. Minimal Monitoring
- Enable error logging (controlled WP_DEBUG_LOG).
- Simple alert: cron greps for "Fatal error" and emails if found.

## 5. Tactical Cleanup
- Remove unused themes (keep one fallback).
- Delete inactive plugins.
- Review media library for orphaned duplicates.

## 6. Sustainable Performance
- Run new Lighthouse for home + a single post template.
- Compare versus early baseline (target variance < 5%).
- Adjust font preload only if it measurably improves LCP.

## 7. Additional Dashboard Hardening
- Limit login attempts.
- Shorten session lifetime.
- Restrict wp-admin by country/IP if justified.

## 8. Content Minimum Pipeline
- Define next 3 pieces (title + purpose + CTA).
- Tag drafts with a common prefix (e.g. `draft-*`).

## 9. SEO & Discoverability
- Check Search Console (coverage + errors).
- Verify sitemap accessible.
- Confirm canonical + hreflang OK on new items.

## 10. Prepare Phase 3 (Continuous Optimization)
- Document first-fortnight lessons.
- List pending risks with due dates.

---
**Expected outcome:** Harder to compromise, stable performance curve, and clear forward content queue.
