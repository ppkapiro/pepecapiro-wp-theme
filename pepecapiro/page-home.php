<?php
/*
 * Template Name: Home
 * Template Post Type: page
 */
get_header();

$lang = function_exists('pll_current_language') ? pll_current_language('slug') : 'es';
$is_en = ($lang === 'en');

$t_hero_title = $is_en
  ? 'AI & Technology Consultant — Process optimization, AI integration, and value generation for SMBs and IT teams.'
  : 'Consultor en IA y Tecnología — Optimización de procesos, integración de IA y generación de valor para pymes y equipos IT.';
$t_hero_cta = $is_en ? 'Discover how AI can optimize your business' : 'Descubre cómo la IA puede optimizar tu negocio';
$t_hero_cta_url = $is_en ? home_url('/en/contact/') : home_url('/contacto/');

$pilares = [
  [
    'title' => $is_en ? 'Practical Automation' : 'Automatización práctica',
    'desc' => $is_en
      ? 'We identify repetitive tasks and automate them with accessible tools to save time and improve quality.'
      : 'Identificamos tareas repetitivas y las automatizamos con herramientas accesibles para ganar tiempo y calidad.'
  ],
  [
    'title' => $is_en ? 'Applied AI in Miami' : 'IA aplicada en Miami',
    'desc' => $is_en
      ? 'Real cases of AI integration in SMBs and IT teams, focused on impact and adoption.'
      : 'Casos reales de integración de IA en pymes y equipos IT, con foco en impacto y adopción.'
  ],
  [
    'title' => $is_en ? 'Measurable Results' : 'Resultados medibles',
    'desc' => $is_en
      ? 'Clear metrics and tracking to ensure return on investment and continuous improvement.'
      : 'Métricas claras y seguimiento para asegurar retorno de inversión y mejora continua.'
  ]
];
?>

<main id="main" class="site-main">
  <section class="hero" style="padding:var(--space-6) 0; background:linear-gradient(135deg, var(--color-bg) 0%, var(--color-surface) 100%);">
    <div class="container hero__inner" style="display:flex; flex-wrap:wrap; align-items:center; gap:var(--space-5);">
      <div class="hero__text" style="flex:1 1 55%; min-width:280px;">
        <h1 class="hero__title" style="font-family:var(--font-title); font-size:var(--font-size-step-4); line-height:1.2; color:var(--color-fg); margin-bottom:var(--space-4);">
          <?php echo esc_html($t_hero_title); ?>
        </h1>
        <a class="cta-button" href="<?php echo esc_url($t_hero_cta_url); ?>" style="display:inline-block; padding:var(--space-2) var(--space-4); background:var(--color-accent); color:var(--color-bg); font-weight:700; border-radius:var(--radius-button); text-decoration:none; transition:opacity 0.2s; outline:none; border:2px solid transparent;">
          <?php echo esc_html($t_hero_cta); ?>
        </a>
      </div>
      <div class="hero__media" style="flex:1 1 40%; min-width:280px; display:flex; align-items:center; justify-content:center;">
        <?php
          // SVG placeholder inline para evitar 403 de imágenes del tema
          echo '<svg class="hero__img" viewBox="0 0 800 500" role="img" aria-label="Hero placeholder" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto;">'
             . '<defs><linearGradient id="g" x1="0" x2="1" y1="0" y2="1"><stop offset="0%" stop-color="#d0e6ff"/><stop offset="100%" stop-color="#e6f2ff"/></linearGradient></defs>'
             . '<rect width="800" height="500" fill="url(#g)"/>'
             . '<circle cx="650" cy="120" r="50" fill="#c5d9f1"/>'
             . '<rect x="60" y="360" width="300" height="24" rx="6" fill="#b0c8e6"/>'
             . '</svg>';
        ?>
      </div>
    </div>
  </section>

  <section class="container pilares" style="padding:var(--space-6) 0; display:grid; gap:var(--space-4); grid-template-columns:repeat(auto-fit, minmax(280px,1fr));">
    <?php foreach ($pilares as $p): ?>
      <div class="pilar-card" style="padding:var(--space-4); background:var(--color-surface); border:1px solid var(--color-border); border-radius:var(--radius-card); transition:transform 0.2s, box-shadow 0.2s;">
        <span class="icon-placeholder" aria-hidden="true" style="display:block; width:48px; height:48px; background:var(--color-border); border-radius:var(--radius-button); margin-bottom:var(--space-2);"></span>
        <h3 style="font-family:var(--font-title); font-size:var(--font-size-step-1); color:var(--color-fg); margin-bottom:var(--space-2);">
          <?php echo esc_html($p['title']); ?>
        </h3>
        <p style="color:var(--color-fg-muted); line-height:1.6;">
          <?php echo esc_html($p['desc']); ?>
        </p>
      </div>
    <?php endforeach; ?>
  </section>
</main>

<?php get_footer(); ?>

