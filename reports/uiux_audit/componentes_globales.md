# Auditoría de Componentes Globales y Tokens CSS — v0.3.0

**Fecha:** 2025-10-28  
**Archivo analizado:** `pepecapiro/assets/css/tokens.css`  
**URL analizada:** https://pepecapiro.com/

---

## 📊 Tokens CSS — Análisis de Design System

### ✅ Fortalezas

**1. Paleta de Colores Bien Definida:**
- **12 tokens de color** semánticos y coherentes
- Nomenclatura clara: `--color-bg`, `--color-accent`, `--color-text-primary`
- Contraste adecuado entre texto y fondos
- Colores de acento: `#1B9AAA` (turquesa) con variantes (`-strong`, `-soft`)

**Análisis de contraste:**
```css
--color-text-primary: #0D1B2A (oscuro)
--color-surface: #FFFFFF (blanco)
→ Ratio de contraste: 15.8:1 (WCAG AAA ✅)

--color-accent: #1B9AAA (turquesa)
--color-surface: #FFFFFF (blanco)
→ Ratio de contraste: 3.2:1 (WCAG AA para texto grande ✅)
```

**2. Tipografía Escalable:**
- Sistema `clamp()` fluid typography (5 steps: --1 to 3)
- Fuentes: Montserrat (títulos) + Open Sans (cuerpo)
- Fallback system fonts: `-apple-system, Segoe UI, Roboto`
- Font-size mínimo: `0.9rem` (14.4px @ 16px base) ✅ legible

**3. Espaciado Consistente:**
- 7 niveles de espaciado: `3xs` (0.25rem) → `xl` (3rem)
- Escala lógica y proporcional
- Uso coherente en márgenes/padding

**4. Accesibilidad:**
- `--focus-ring` definido: `0 0 0 3px rgba(27, 154, 170, 0.34)` ✅
- Estados `:focus-visible` implementados en botones y enlaces
- `color-scheme: light` declarado
- `::selection` con contraste adecuado

**5. Performance:**
- `scroll-behavior: smooth` ✅
- `-webkit-font-smoothing: antialiased` ✅
- `text-rendering: optimizeLegibility` ✅

---

## ⚠️ Hallazgos y Oportunidades de Mejora

### 1. Contraste de Enlaces en Hover (MEDIA)

**Problema:**
```css
a { color: var(--color-accent); } /* #1B9AAA */
a:hover { color: var(--color-accent-strong); } /* #137F8E */
```

El cambio de contraste entre estado normal y hover es **sutil** (3.2:1 → 2.8:1).

**Recomendación:**
- Agregar `text-decoration: underline` en estado hover ✅ (ya implementado)
- Considerar un color hover más oscuro para mayor contraste: `#0F6B78` (ratio 3.8:1)

**Prioridad:** MEDIA

---

### 2. Color de Párrafos (`--color-text-secondary`) (BAJA)

**Problema:**
```css
p, ul, ol { color: var(--color-text-secondary); } /* #1E3A56 */
```

Contraste contra `--color-surface` (#FFFFFF): **11.2:1** (excelente).

Sin embargo, `--color-text-secondary` es muy similar a `--color-text-primary` (#0D1B2A).

**Análisis visual:**
- `#0D1B2A` → `#1E3A56`: diferencia perceptual mínima
- No hay suficiente jerarquía visual entre h2/h3 y párrafos

**Recomendación:**
- Mantener `--color-text-primary` (#0D1B2A) para títulos
- Ajustar `--color-text-secondary` a un tono ligeramente más claro: `#2C4A64` (contraste 9.5:1, sigue siendo WCAG AAA)
- Esto crea mejor jerarquía tipográfica sin sacrificar legibilidad

**Prioridad:** BAJA

---

### 3. Sombras (`--shadow-soft`, `--shadow-sharp`) (BAJA)

**Análisis:**
```css
--shadow-soft: 0 12px 32px rgba(13, 27, 42, 0.12);
--shadow-sharp: 0 12px 24px rgba(19, 121, 144, 0.18);
```

**Observación:**
- Ambas sombras tienen **blur radius alto** (24-32px)
- En `--shadow-sharp`, el color base `rgba(19, 121, 144, ...)` es turquesa (relacionado con `--color-accent`)
- Uso en cards: genera sensación de "flotación" (buen efecto de profundidad)

**Potencial mejora:**
- Crear una tercera variante `--shadow-xs` para estados hover sutiles:
  ```css
  --shadow-xs: 0 4px 12px rgba(13, 27, 42, 0.08);
  ```
- Uso en hover de `.card`: transición suave de elevación

**Prioridad:** BAJA

---

### 4. Falta de Dark Mode Support (MEDIA - Futuro)

**Observación:**
```css
html { color-scheme: light; }
```

El sitio **no tiene soporte de dark mode**. Esto es aceptable en v0.3.0, pero debería considerarse en v0.4.0.

**Recomendación (v0.4.0):**
```css
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #FFFFFF;
    --color-bg-alt: #F5F5F5;
    --color-surface: #0D1B2A;
    --color-text-primary: #FFFFFF;
    --color-text-secondary: #C7D0DB;
    /* ... invertir paleta */
  }
}
```

**Prioridad:** MEDIA (roadmap futuro)

---

## 🎨 Análisis de Componentes HTML (Home ES)

### Header (`.site-header`)

**Estructura:**
```html
<header class="site-header">
  <div class="container site-header__inner">
    <a class="brand" href="/">Pepecapiro</a>
    <nav>...</nav>
    <div class="lang-switcher">...</div>
  </div>
</header>
```

**Observaciones:**
- ✅ Brand como enlace (accesibilidad)
- ✅ Nav con `<nav>` semántico
- ✅ Lang switcher con banderas (16x11px inline base64)
- ⚠️ **Banderas en base64**: aumentan HTML size (~500 bytes por bandera)

**Recomendación:**
- Considerar SVG sprites o archivos `.png` cacheables (reduce HTML inline)
- Agregar atributo `aria-label="Cambiar idioma"` al `.lang-switcher` (a11y)

**Prioridad:** BAJA

---

### Hero (`.hero`)

**Estructura:**
```html
<section class="hero">
  <div class="container">
    <h1>Soporte técnico y automatización, sin drama.</h1>
    <p class="subtitle">Arreglo lo urgente hoy...</p>
    <a class="btn" href="/contacto">Hablemos</a>
  </div>
</section>
```

**Observaciones:**
- ✅ Estructura clara y semántica
- ✅ CTA prominente con `.btn`
- ✅ Copy conciso y directo
- ⚠️ **Falta background visual**: Hero es solo texto sobre fondo blanco

**Recomendación:**
- Considerar:
  - Gradient background sutil: `linear-gradient(to bottom, #F1FBFC, #FFFFFF)`
  - Pattern decorativo (optional): dots/lines con `--color-border`
  - Imagen ilustrativa (automation/AI theme) en desktop

**Prioridad:** MEDIA (mejora visual)

---

### Cards (`.card`)

**Estructura:**
```html
<div class="card">
  <h3>Automatización práctica</h3>
  <p>Problema: tareas repetitivas...</p>
  <a class="btn btn--ghost" href="/proyectos/">Ver servicios</a>
</div>
```

**Observaciones:**
- ✅ **min-height implementado** (anti-CLS) → CLS 0.000 validado en Lighthouse
- ✅ Estructura consistente (h3 + p + CTA)
- ✅ `.btn--ghost` variante (good UI pattern)
- ⚠️ **Contenido placeholder**: "Contexto → acción → resultado (placeholder)"

**Análisis de layout:**
```css
/* Probable CSS (no visible en HTML pero inferido de performance) */
.card {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-lg);
  box-shadow: var(--shadow-soft);
  min-height: 18rem; /* Anti-CLS ✅ */
}
```

**Recomendación:**
- Mantener min-height (excelente para CLS)
- Agregar estado hover: `box-shadow: var(--shadow-sharp)` con `transition: box-shadow var(--transition-base)`
- Completar contenido placeholder (proyectos destacados, testimonios)

**Prioridad:** BAJA (funcional), ALTA (contenido)

---

### Footer (`.site-footer`)

**Estructura:**
```html
<footer class="site-footer">
  <div class="container footer-grid">
    <div class="footer-col">...</div> <!-- Pepecapiro -->
    <div class="footer-col">...</div> <!-- Enlaces -->
    <div class="footer-col">...</div> <!-- Contacto -->
  </div>
  <div class="container footer-bottom">
    <p class="muted">© 2025 Pepecapiro</p>
  </div>
</footer>
```

**Observaciones:**
- ✅ Grid de 3 columnas (Desktop)
- ✅ Enlaces organizados semánticamente
- ✅ `.muted` para copyright (buen uso de jerarquía)
- ⚠️ **Inconsistencia de enlaces**: 
  - "Privacidad" → `/privacidad/` (ES)
  - "Cookies" → `/en/cookies/` (EN - debería ser `/cookies/`)

**Recomendación:**
- Corregir enlace Cookies a idioma correcto
- Agregar enlaces a redes sociales (GitHub, LinkedIn, Twitter) si aplica

**Prioridad:** MEDIA (corrección de enlaces)

---

## 🔤 Tipografía — Análisis de Uso

### Familia de Fuentes

**Declaradas:**
```css
--font-title: "Montserrat", system-ui, -apple-system, ...
--font-body: "Open Sans", system-ui, -apple-system, ...
```

**Preload detectado en HTML:**
```html
<link rel="preload" href=".../Montserrat-Bold.woff2" as="font" type="font/woff2" crossorigin>
```

**Observaciones:**
- ✅ Preload de fuente crítica (Montserrat-Bold) para LCP
- ✅ Format WOFF2 (mejor compresión)
- ⚠️ **Solo Montserrat-Bold preloaded**: ¿Open Sans no se preloadea?

**Análisis de performance:**
- Lighthouse run 18877785392: LCP 1437-2007ms ✅
- Font preload contribuye a buen LCP
- Open Sans probablemente se carga después de FCP (no crítica)

**Recomendación:**
- Mantener preload actual (Montserrat-Bold es crítica para h1 en hero)
- Considerar preload de Open Sans Regular **solo si LCP degrada** en futuras auditorías
- Alternativa: usar `font-display: swap` para reducir blocking

**Prioridad:** BAJA (ya optimizado)

---

### Escalado de Fuentes (Fluid Typography)

**Análisis de clamp():**
```css
--font-size-step-0: clamp(1rem, 0.97rem + 0.35vw, 1.125rem);
/* Mobile: 16px, Desktop (1200px): 18px */

--font-size-step-3: clamp(2.1rem, 1.8rem + 1.35vw, 2.8rem);
/* Mobile: 33.6px, Desktop (1200px): 44.8px */
```

**Prueba de responsividad:**
- Mobile (375px): h1 = 33.6px ✅ legible
- Tablet (768px): h1 = 39.2px ✅ proporcionado
- Desktop (1200px): h1 = 44.8px ✅ impactante

**Observación:**
- ✅ Escalado suave sin media queries
- ✅ Tamaños mínimos garantizan legibilidad en mobile

**Recomendación:**
- Mantener sistema actual (excelente implementación)

**Prioridad:** N/A (sin cambios necesarios)

---

## 🎯 Resumen de Prioridades

| Hallazgo | Prioridad | Acción Sugerida | Impacto |
|----------|-----------|-----------------|---------|
| Contraste hover enlaces | MEDIA | Oscurecer `--color-accent-strong` a `#0F6B78` | Mejora a11y |
| Hero sin background visual | MEDIA | Agregar gradient/pattern sutil | Mejora estética |
| Enlace Cookies incorrecto | MEDIA | Corregir `/en/cookies/` → `/cookies/` | Fix funcional |
| Color text-secondary | BAJA | Ajustar a `#2C4A64` para jerarquía | Mejora visual |
| Banderas base64 | BAJA | Migrar a SVG sprites | Optimización HTML |
| Sombra hover cards | BAJA | Agregar `--shadow-xs` y hover effect | Mejora interacción |
| aria-label lang-switcher | BAJA | Agregar atributo a11y | Mejora a11y |
| Dark mode support | MEDIA (futuro) | Roadmap v0.4.0 | Feature request |

---

## ✅ Tokens CSS — Checklist de Calidad

- ✅ **12 tokens de color** semánticos
- ✅ **Contraste WCAG AAA** en texto principal (15.8:1)
- ✅ **Fluid typography** con clamp() (5 steps)
- ✅ **7 niveles de espaciado** consistentes
- ✅ **Focus ring** definido y aplicado
- ✅ **Font preload** de Montserrat-Bold (LCP optimization)
- ✅ **3 variantes de border-radius** (sm/md/lg)
- ✅ **2 sombras** (soft/sharp) con blur adecuado
- ✅ **Transiciones** con duración consistente (150ms ease-in-out)
- ✅ **Max-width** definidos (content: 60rem, wide: 75rem)

---

## 🔗 Referencias

- **Tokens CSS:** `pepecapiro/assets/css/tokens.css`
- **Performance baseline:** `reports/psi/fase4_performance_final.md` (CLS 0.000)
- **HTML analizado:** `curl https://pepecapiro.com/` (2025-10-28)
- **WCAG Guidelines:** https://www.w3.org/WAI/WCAG21/quickref/

---

_Auditoría completada: 2025-10-28 16:10 UTC_
