# BKLG-005 Deuda visual y CSS/JS suelto

## 2025-10-27 — Tokens v0.3.0 normalizados

### Antes
- Paleta declarada dos veces (`style.css` vs `tokens.css`) con valores hex duplicados y sin escalas de espaciado.
- Botones y enlaces sin estados `:focus-visible`, lo que dificultaba navegación por teclado.
- Cartas y gradientes definidos con colores fijos (#eee, #fff) que no heredaban el sistema base documentado en el DTC §4.

### Después
- `pepecapiro/assets/css/tokens.css` concentra colores, tipografías, espaciados, radios y sombras (`--color-*`, `--space-*`, `--radius-*`, `--shadow-*`).
- `pepecapiro/style.css` consume los tokens para header, hero, botones, grid y formularios; elimina valores hardcodeados y añade transiciones/focos accesibles.
- Focus ring accesible (`--focus-ring`) visible en enlaces/botones; contraste AA asegurado para CTAs (`var(--color-text-inverse)` sobre `var(--color-accent)`).
- Layout responsive usa `var(--max-width-content)` y espaciados (`var(--space-lg)`, `var(--space-xl)`) consistentes.

### Reglas migradas
- Colores: `#0D1B2A`, `#1B9AAA`, `#E0E1DD`, `#ffffff`, `#eee` → `--color-*`.
- Tipografías: `Montserrat`/`Open Sans` → `--font-title` / `--font-body`.
- Espaciado: `padding:56px`, `gap:16px`, `margin:32px` → `var(--space-*)`.
- Bordes y radios: valores de 8px/12px/16px → `--radius-sm|md|lg` y `--color-border`.
- Sombras: `box-shadow` genérico reemplazado por `--shadow-soft`.

### Evidencia
- Capturas generadas (Fase 2):
  - Desktop: `evidence/ui/home-desktop-20251027.png`
  - Mobile: `evidence/ui/home-mobile-20251027.png`
- Capturas generadas (Fase 3):
  - Home ES: `evidence/ui/fase3_home-es-desktop.png`, `evidence/ui/fase3_home-es-mobile.png`
  - About ES: `evidence/ui/fase3_about-es-desktop.png`
  - Projects ES: `evidence/ui/fase3_projects-es-desktop.png`
  - Resources ES: `evidence/ui/fase3_resources-es-desktop.png`
- Referencia histórica: `evidence/20250923_114623_css_frecuencias.txt` (antes de la migración).

## 2025-10-27 — Fase 3: Plantillas bilingües y OG dinámico

### Plantillas refactorizadas con tokens CSS
- `page-home.php`: Hero + 3 pilares con copy ES/EN, inline SVG placeholders, tokens completos.
- `page-about.php`: About grid bilingüe, CTAs ajustados (LinkedIn + contacto).
- `page-projects.php`: Grid de proyectos (3 tarjetas placeholder) con copy ES/EN.
- `page-resources.php`: Grid de recursos (4 tarjetas con íconos emoji) con copy ES/EN.
- `page-contact.php`: Auditado OK — tokens presentes, honeypot/nonce/estados funcionales.

### Open Graph
- Imágenes generadas:
  - `pepecapiro/assets/og/og-home-es.png` (215K, 1200×630)
  - `pepecapiro/assets/og/og-home-en.png` (210K, 1200×630)
- Lógica OG dinámica en `functions.php` detecta plantillas (Home, About, Projects, Resources) y sirve imagen correcta por idioma.

### Menús
- `content/menus/menus.json` actualizado con estructura completa ES/EN (6 ítems: Inicio, Sobre mí, Proyectos, Recursos, Blog, Contacto).

### Validación
- Anti-hex CSS: **PASS** — ningún color hardcodeado fuera de `tokens.css`.
