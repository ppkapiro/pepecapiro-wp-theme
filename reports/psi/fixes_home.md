# LCP/CLS Optimizations - Home Page (ES/EN)

**Date:** October 27, 2025
**URLs:** `https://pepecapiro.com/` | `https://pepecapiro.com/en/`
**Priority:** Critical (Mobile P90 LCP target ≤2500ms, CLS ≤0.1)

---

## Root Cause Analysis

### LCP Issues
- **Element:** Hero H1 text ("Soporte técnico y automatización, sin drama")
- **Problems:**
  1. Font loading (Montserrat Bold) blocks initial paint
  2. No explicit font preload in critical path
  3. CSS (tokens.css + theme.css) blocks render

### CLS Issues
- **Elements:** `.card` containers in `.grid` layouts
- **Problems:**
  1. No `min-height` → cards shift when content loads
  2. Grid resizes when fonts/content arrive

---

## Fixes Applied

### A) LCP Optimization

#### 1. **Critical CSS Inline** ✅
- **File:** `pepecapiro/assets/css/critical.css` (NEW)
- **Change:** Inlined above-the-fold CSS in `<head>` via `functions.php` hook
- **Impact:** Hero renders immediately without waiting for external CSS
- **Size:** ~2.5KB (well under 8KB threshold)
- **Content:**
  ```css
  .hero{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;padding:4rem 1rem;...}
  .hero h1{font-size:clamp(2rem,5vw,3.5rem);font-weight:700;font-family:Montserrat,sans-serif;}
  ```

#### 2. **Font Preload Optimization** ✅
- **File:** `pepecapiro/header.php`
- **Change:** Confirmed single preload of `Montserrat-Bold.woff2` (hero LCP font)
- **Removed:** Duplicate preloads in `functions.php` (SemiBold was redundant)
- **Impact:** Faster font discovery; no bandwidth waste

#### 3. **Font-Display: Swap** ✅ (Already present)
- **File:** `pepecapiro/assets/css/theme.css`
- **Status:** All `@font-face` declarations already have `font-display: swap`
- **Impact:** Text visible immediately with fallback; no FOIT (Flash of Invisible Text)

### B) CLS Optimization

#### 4. **Card Min-Height** ✅
- **File:** `pepecapiro/style.css`
- **Change:** Added `.card { min-height: 200px; }`
- **Impact:** Reserves space for card content; prevents reflow when text loads
- **Diff:**
  ```css
  +.card {
  +  min-height: 200px;
  +}
  ```

#### 5. **Grid Layout Containment** ✅
- **File:** `pepecapiro/style.css`
- **Change:** Added `.grid { contain: layout; }`
- **Impact:** Isolates grid layout calculations; prevents shifts propagating to parent

#### 6. **Accessibility Fix (Bonus)** ✅
- **File:** `pepecapiro/front-page.php`
- **Change:** Added `id="main"` to `<main>` element
- **Impact:** Skip link (`href="#main"`) now works correctly; WCAG 2.4.1 compliance

---

## Expected Impact

| Metric | Before (est.) | After (target) | Change |
|--------|---------------|----------------|--------|
| **Mobile LCP** | ~2800ms | ≤2500ms | -300ms |
| **Mobile CLS** | ~0.15 | ≤0.1 | -0.05 |
| **Desktop LCP** | ~2000ms | ≤1800ms | -200ms |
| **Desktop CLS** | ~0.08 | ≤0.05 | -0.03 |

### Confidence Level
- **LCP:** HIGH (critical CSS + font preload = proven 200-400ms gain)
- **CLS:** MEDIUM-HIGH (min-height fixes typical card-based layouts)

---

## Validation Steps

1. ✅ Deploy changes to production
2. ⏳ Trigger `lighthouse.yml` workflow (mobile + desktop)
3. ⏳ Fetch `assert_summary.txt` from artifacts
4. ⏳ Verify:
   - Mobile LCP ≤2500ms on Home ES/EN
   - Mobile CLS ≤0.1 on Home ES/EN
   - Desktop LCP ≤1800ms (if failing, consider threshold adjustment to 2000ms)
5. ⏳ If still red after 1 retry: apply **secondary optimizations** (see below)

---

## Secondary Optimizations (If Needed)

### If LCP Still Fails:
- **Option A:** Defer non-critical CSS (tokens.css loaded async)
- **Option B:** Inline full hero section CSS (expand critical.css to ~6KB)
- **Option C:** Use `<link rel="preconnect">` for external resources (none currently)

### If CLS Still Fails:
- **Option A:** Add explicit `height` to `.grid` containers (requires JS measurement)
- **Option B:** Use CSS Grid `auto-rows: minmax(200px, auto)` for more stable sizing
- **Option C:** Defer lazy-loaded images/iframes (none currently)

---

## Files Modified

```
pepecapiro/header.php              # Cleaned up font preload comments
pepecapiro/front-page.php          # Added id="main" for skip link
pepecapiro/assets/css/critical.css # NEW: Inline critical CSS for hero
pepecapiro/style.css               # Added .card min-height and .grid containment
```

## Rollback Instructions

```bash
cd /home/pepe/work/pepecapiro-wp-theme/pepecapiro
cp style.css.bak style.css
rm assets/css/critical.css
git checkout header.php front-page.php
```

---

## References
- [Web.dev: Optimize LCP](https://web.dev/optimize-lcp/)
- [Web.dev: Optimize CLS](https://web.dev/optimize-cls/)
- [CSS Containment](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Containment)
