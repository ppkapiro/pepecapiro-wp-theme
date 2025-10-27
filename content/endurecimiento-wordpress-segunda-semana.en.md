# WordPress Second Week: Hardening and Priority Stabilization

In the first week after the launch, you mitigated urgent risks. Now it's time to consolidate, close residual gaps, and establish basic health signals.

## Objectives of this phase
1. Reduce exposed surface area.
2. Gain minimum visibility (logs and light monitoring).
3. Eliminate debris that may degrade performance.
4. Prepare the foundation for content scaling.

## 1. Review of accounts and roles
- Remove temporary users created for the launch.
- Verify that there are no leftover administrators.
- Force update of weak passwords.

## 2. Endpoints and XML-RPC
- If you are not using mobile apps or Jetpack, disable XML-RPC.
- Limit sensitive REST endpoints (security plugins or WAF rules).

## 3. Consistent backups
- Schedule daily incremental backups + weekly full backups.
- Test a partial restoration (table `wp_options`) to validate.

## 4. Minimum monitoring
- Activate error logging (WP_DEBUG_LOG in a controlled environment).
- Implement a simple alert (cron job that searches for "Fatal error" and sends an email if it appears).

## 5. Tactical cleanup
- Remove unused themes (leave one as a fallback).
- Delete inactive plugins.
- Review the media library for unreferenced duplicates.

## 6. Sustainable performance
- Generate a new Lighthouse report for the home page and a post template.
- Compare against the initial baseline (tolerable variation < 5%).
- Adjust font preloading only if it improves LCP.

## 7. Additional hardening of the dashboard
- Limit login attempts.
- Adjust session expiration.
- Restrict access to wp-admin by country/IP if applicable.

## 8. Minimum content checklist
- Define 3 upcoming pieces (title + objective + CTA).
- Tag drafts with a prefix to group them (e.g., `draft-*`).

## 9. SEO and Discoverability
- Review Search Console (coverage + errors).
- Verify that the generated sitemap is accessible.
- Check that canonical + hreflang work on new pieces.

## 10. Prepare phase 3 (Continuous Optimization)
- Document lessons from the first fortnight.
- List pending risks and assign due dates.

---
**Expected outcome:** A site that is harder to compromise, stable in performance, and with a clear content backlog.