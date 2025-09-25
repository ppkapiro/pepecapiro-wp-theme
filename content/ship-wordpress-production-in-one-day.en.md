# Checklist to Ship a WordPress Site to Production in 1 Day

> Initial concise version. Add deeper technical appendices only if needed.

## 1. Base & Access
- Domain DNS propagated
- Hosting ready (PHP 8.2, HTTPS enabled)
- Admin user + strong password

## 2. Minimum Security
- Core + plugins updated
- Remove unused plugins/themes
- Set permalink to "/%postname%/"

## 3. Performance Baseline
- Page cache (LiteSpeed or similar) on
- Self-hosted WOFF2 fonts
- Images compressed (prefer WebP)

## 4. SEO & Structure
- Rank Math configured (sitemaps OK)
- Clean `robots.txt`
- Coherent title + meta description

## 5. Minimum Content
- Home + About + Contact (ES/EN)
- First post (ES/EN) with excerpt
- Legal pages (privacy, cookies)

## 6. Final Verification
- Sitemap clean (no hello-world)
- Lighthouse mobile ≥90
- Contact form works

---
Executable within 24h if visual scope is constrained and stability + measurement are prioritized.
