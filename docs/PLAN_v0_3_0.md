# Plan v0.3.0 — pepecapiro.com

**Objetivo:** habilitar contacto real (SMTP), publicar el primer artículo (ES/EN) y cumplir básicos legales (cookies/privacidad).

## 1) SMTP / Formularios (WPForms)
- [ ] Revisar proveedor SMTP (Hostinger SMTP/Zoho/GSuite).
- [ ] Instalar y configurar plugin SMTP (WP Mail SMTP o similar).
- [ ] Variables: host, puerto, cifrado, usuario, app password.
- [ ] Prueba: envío real a contacto@pepecapiro.com (ES/EN).
- [ ] Actualizar página Contacto con estado “Operativo”.

Criterio de cierre: entregas llegan en < 1 min y quedan en Inbox (no Spam).

## 2) Primer artículo (ES/EN)
- [ ] Estructura: problema → mini-solución → beneficio → CTA a contacto/checklist.
- [ ] Longitud: 800–1200 palabras; imágenes `.webp`; metadatos Rank Math.
- [ ] Duplicado EN con adaptación (no literal).
- [ ] Publicar y enlazar desde Home (sección Blog).

Criterio de cierre: 2 URLs publicadas con `hreflang` correcto y OG cards.

## 3) Legales básicos
- [ ] Página de **Privacidad** (plantilla sencilla; contacto y base legal).
- [ ] Banner de **cookies** con consentimiento (plugin ligero).
- [ ] Enlaces en footer (ES/EN).

Criterio de cierre: páginas visibles, enlaces en footer, banner activo.

## 4) Medición y SEO
- [ ] GA4 verificado; eventos: clic CTA, envío formularios.
- [ ] Search Console: sitemap enviado y sin errores.
- [ ] Revalidar Lighthouse (Mobile) tras cambios.

Umbrales: Perf ≥ 90 en Home ES/EN; LCP ≤ 2.5s global.

## 5) Entregables
- Checklists marcadas en este archivo.
- Evidencia (capturas/links) pegadas al final.

## Cierre de etapa: Auditoría Lighthouse + PSI

- Estado: **CERRADO**
- Evidencia final: https://github.com/ppkapiro/pepecapiro-wp-theme/actions/workflows/lighthouse_docs.yml
- Próximo hito: v0.3.0 (SMTP, primer artículo ES/EN, legales).
- Fecha de cierre: actualizado al crear la release estable.
