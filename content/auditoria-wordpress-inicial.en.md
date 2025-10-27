# Initial WordPress Audit: 12 Critical Checks

> Minimum list to understand the real state before making any changes.

## 1. Versions
- Core updated
- Plugins and themes without known vulnerabilities

## 2. Access
- Minimum admin users
- No generic accounts like `admin`

## 3. Backups
- Existing and restoration tested
- Frequency ≥ daily

## 4. Plugins
- Remove inactive ones
- Avoid functional duplication (cache/SEO)

## 5. Themes
- Only active theme + necessary parent
- Versioned child theme

## 6. Basic Security
- Table prefix not `wp_`
- `wp-config.php` file with unique salts

## 7. Base Performance
- Page cache active
- Minified fonts and assets

## 8. Measurement
- Correct Analytics (no duplicates)
- Verified Search Console

## 9. Technical SEO
- Clean sitemaps
- `robots.txt` without undue blocks

## 10. Content
- No visible lorem ipsum
- Legal pages present

## 11. Forms
- Correct submission (test success/error)
- Basic spam protection

## 12. Logs / Errors
- WP_DEBUG disabled in production
- No visible warnings

---
Checklist usable as a basis for a report prior to improvements.