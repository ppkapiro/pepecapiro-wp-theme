# Initial WordPress Audit: 12 Critical Checks

> Minimal list to understand real status before changing anything.

## 1. Versions
- Core up to date
- Plugins & themes free of known vulns

## 2. Access
- Minimal admin accounts
- No generic `admin` user

## 3. Backups
- Exist and restore tested
- Frequency ≥ daily

## 4. Plugins
- Remove inactive ones
- Avoid overlapping functionality (cache/SEO)

## 5. Themes
- Only active theme + required parent
- Child theme versioned

## 6. Basic Security
- Table prefix not `wp_`
- `wp-config.php` with unique salts

## 7. Performance Baseline
- Page cache enabled
- Fonts & assets minified

## 8. Measurement
- Analytics correct (no duplicates)
- Search Console verified

## 9. Technical SEO
- Clean sitemaps
- `robots.txt` no unintended blocks

## 10. Content
- No visible lorem ipsum
- Legal pages present

## 11. Forms
- Successful submit (test success/error)
- Basic spam protection

## 12. Logs / Errors
- WP_DEBUG off in prod
- No visible warnings

---
Checklist can seed a pre‑improvement report.
