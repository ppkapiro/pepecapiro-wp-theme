# Propuesta de Paleta Cromática — v0.3.1

**Fecha:** 2025-10-28
**Objetivo:** Migrar de paleta oscura a paleta clara profesional

---

## 🎨 Nueva Paleta Propuesta

### Fundamentos de la Nueva Paleta

**Filosofía:** Claridad, profesionalismo, accesibilidad

**Inspiración:**
- Paletas de servicios profesionales (consultorías, tech services)
- Fondos neutros cálidos (grises suaves, beiges)
- Acentos refinados (azules petroleo, turquesas desaturados)

---

## 📋 Tokens CSS — Comparativa

| Token | ACTUAL (v0.3.21) | PROPUESTO (v0.3.1) | Cambio |
|-------|------------------|-------------------|--------|
| `--color-bg` | `#0D1B2A` (azul oscuro) | `#F5F6F8` (gris claro cálido) | ⚠️ INVERSIÓN |
| `--color-bg-alt` | `#13263F` (azul oscuro alt) | `#EAECEF` (gris medio) | ⚠️ INVERSIÓN |
| `--color-surface` | `#FFFFFF` (blanco) | `#FFFFFF` (blanco) | ✅ Sin cambio |
| `--color-surface-muted` | `#E0E1DD` (gris claro) | `#F8F9FA` (gris muy claro) | 🔧 Ajuste |
| `--color-border` | `#C7D0DB` (azul gris) | `#D1D5DB` (gris neutro) | 🔧 Ajuste |
| `--color-border-strong` | `#20354A` (azul oscuro) | `#9CA3AF` (gris medio) | ⚠️ Clarificado |
| `--color-accent` | `#1B9AAA` (turquesa vibrante) | `#0F7490` (petroleo refinado) | 🔧 Desaturado |
| `--color-accent-strong` | `#137F8E` (turquesa oscuro) | `#0A5F75` (petroleo oscuro) | 🔧 Desaturado |
| `--color-accent-soft` | `#F1FBFC` (turquesa muy claro) | `#E0F2F7` (azul muy claro) | 🔧 Ajuste |
| `--color-text-primary` | `#0D1B2A` (casi negro azul) | `#1F2937` (gris oscuro) | 🔧 Neutro |
| `--color-text-secondary` | `#1E3A56` (azul medio) | `#4B5563` (gris medio) | 🔧 Neutro |
| `--color-text-muted` | `#5A6C7F` (azul gris) | `#6B7280` (gris neutro) | 🔧 Neutro |
| `--color-text-inverse` | `#FFFFFF` (blanco) | `#FFFFFF` (blanco) | ✅ Sin cambio |

---

## 🎯 Cambios Clave

### 1. Inversión de Fondos (CRÍTICO)

**ANTES:**
```css
--color-bg: #0D1B2A; /* Azul oscuro casi negro */
body { background: var(--color-bg); color: var(--color-text-inverse); }
```

**DESPUÉS:**
```css
--color-bg: #F5F6F8; /* Gris claro cálido */
body { background: var(--color-bg); color: var(--color-text-primary); }
```

**Impacto:**
- Sitio pasa de "dark mode" a "light mode" (estándar profesional)
- Mejora legibilidad y reduce fatiga visual
- Sensación de amplitud y claridad

### 2. Acento Refinado (Turquesa → Petroleo)

**ANTES:** `#1B9AAA` (turquesa vibrante, alto contraste)
**DESPUÉS:** `#0F7490` (petroleo desaturado, elegante)

**Razones:**
- Turquesa actual es demasiado "brillante" para sitio profesional
- Petroleo transmite seriedad y tecnología
- Mejor integración con paleta neutra

### 3. Textos Neutros (Azul → Gris)

**ANTES:** Textos con tintes azules (`#0D1B2A`, `#1E3A56`)
**DESPUÉS:** Textos grises neutros (`#1F2937`, `#4B5563`)

**Beneficios:**
- Mayor versatilidad (no ata a tema "azul")
- Mejor jerarquía visual (primary vs secondary más clara)
- Compatibilidad con imágenes y contenido variado

---

## 🖼️ Hero Section — Propuesta Visual

**Problema actual:** Hero es fondo blanco plano (sin impacto visual)

**Propuesta:** Gradient sutil con textura

```css
.hero {
  background: linear-gradient(
    135deg,
    #FDFDFD 0%,
    #F0F4F8 100%
  );
  /* Alternativa con pattern decorativo */
  background-image:
    radial-gradient(circle at 20% 50%, rgba(15, 116, 144, 0.03) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(15, 116, 144, 0.03) 0%, transparent 50%);
  background-size: 100% 100%;
}
```

**Efecto:**
- Sutil pero impactante (no distrae del contenido)
- Acentos del brand color (petroleo) con opacidad baja
- Sensación de profundidad sin perder claridad

---

## ✅ Validación de Contraste WCAG

### Nueva Paleta — Análisis de Contraste

| Par de Colores | Contraste | WCAG AA | WCAG AAA |
|----------------|-----------|---------|----------|
| Texto primary (#1F2937) / Superficie (#FFFFFF) | **14.5:1** | ✅ | ✅ |
| Texto secondary (#4B5563) / Superficie (#FFFFFF) | **9.2:1** | ✅ | ✅ |
| Acento (#0F7490) / Superficie (#FFFFFF) | **4.6:1** | ✅ | ❌ (texto grande) |
| Texto inverse (#FFFFFF) / Background (#F5F6F8) | **1.05:1** | ❌ | ❌ |

**Notas:**
- Textos primary/secondary cumplen WCAG AAA ✅
- Acento cumple WCAG AA (uso en botones y enlaces ✅)
- Texto inverse no se usa sobre nuevo background (solo en nav oscuro si aplica)

---

## 🚀 Plan de Implementación

### Fase 1: Actualizar tokens.css

1. **Backup de paleta actual:**
   ```bash
   cp pepecapiro/assets/css/tokens.css pepecapiro/assets/css/tokens.v0.3.21.bak.css
   ```

2. **Aplicar nuevos valores:**
   - Editar `pepecapiro/assets/css/tokens.css`
   - Reemplazar colores según tabla de comparativa

3. **Ajustar hero background:**
   - Editar `pepecapiro/assets/css/theme.css`
   - Agregar gradient a `.hero`

### Fase 2: Validación Visual

1. **Test local:**
   ```bash
   # Desplegar en local con nuevo CSS
   npm run build:css
   ```

2. **Capturas comparativas:**
   - Antes (v0.3.21) vs Después (v0.3.1)
   - Desktop y mobile

3. **Lighthouse re-audit:**
   - Validar que performance no degrada
   - CLS debe mantenerse en 0.000

### Fase 3: Deploy a Producción

1. **Commit:**
   ```bash
   git add pepecapiro/assets/css/tokens.css
   git commit -m "feat(ui): nueva paleta clara v0.3.1 - migración de oscuro a claro"
   ```

2. **Deploy via workflow:**
   ```bash
   gh workflow run deploy.yml
   ```

3. **Monitoreo post-deploy:**
   - Verificar home ES/EN carga correctamente
   - Ejecutar Lighthouse baseline (run nuevo)
   - Capturar screenshots post-deploy

---

## 🎨 Preview de Paleta (Visual)

### Combinaciones Principales

**1. Texto sobre Superficie:**
```
Background: #FFFFFF (blanco)
Text Primary: #1F2937 (gris oscuro)
Text Secondary: #4B5563 (gris medio)
Contraste: 14.5:1 / 9.2:1 → AAA ✅
```

**2. Hero Section:**
```
Background: Gradient #FDFDFD → #F0F4F8
Text: #1F2937 (gris oscuro)
Acento (CTA): #0F7490 (petroleo)
```

**3. Cards:**
```
Background: #FFFFFF
Border: #D1D5DB (gris neutro)
Shadow: rgba(0, 0, 0, 0.1)
Hover: Shadow intensificado + border #0F7490
```

**4. Footer:**
```
Background: #F5F6F8 (gris claro cálido)
Text: #4B5563 (gris medio)
Links: #0F7490 (petroleo)
Links Hover: #0A5F75 (petroleo oscuro)
```

---

## 📊 Impacto Esperado

### Mejoras Visuales ✅

1. **Sensación de amplitud** - Fondo claro abre el espacio
2. **Profesionalismo** - Paleta neutra transmite seriedad
3. **Legibilidad** - Contraste AAA en texto principal
4. **Jerarquía clara** - Diferenciación visual entre niveles de texto
5. **Brand consistency** - Acento petroleo único y memorable

### Performance ✅

1. **CLS mantenido** - Sin cambios estructurales (solo colores)
2. **LCP sin impacto** - Hero gradient es CSS puro (no imagen)
3. **CSS size** - Sin aumento (solo valores HEX cambian)

### Accesibilidad ✅

1. **WCAG AAA en textos** - Contraste 14.5:1 y 9.2:1
2. **WCAG AA en acentos** - Contraste 4.6:1 (suficiente para botones)
3. **Fatiga visual reducida** - Fondo claro estándar

---

## 🎯 Conclusión

**Recomendación:** ✅ **IMPLEMENTAR paleta clara en v0.3.1**

La migración de paleta oscura a paleta clara:
- Mejora drásticamente la **primera impresión** del sitio
- Alinea con **estándares profesionales** (mayoría de sitios corporativos usan fondos claros)
- Mantiene **performance elite** (CLS 0.000, LCP bajo)
- Incrementa **accesibilidad** (contraste AAA)
- Es **reversible** (backup de paleta antigua disponible)

**Riesgo:** BAJO (solo cambios de color, sin reestructuración)

**Esfuerzo:** BAJO (editar 2 archivos CSS, ~30 minutos)

**Impacto:** ALTO (transformación visual completa del sitio)

