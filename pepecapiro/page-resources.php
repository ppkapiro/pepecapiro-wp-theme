<?php
/*
 * Template Name: Resources
 * Template Post Type: page
 */
get_header();

$lang = function_exists('pll_current_language') ? pll_current_language('slug') : 'es';
$is_en = ($lang === 'en');

$t_title = $is_en ? 'Resources' : 'Recursos';
$t_intro = $is_en
  ? 'Useful tools, guides, and references for technical support and automation.'
  : 'Herramientas, guías y referencias útiles para soporte técnico y automatización.';

// Placeholder resources (estructura estática)
$resources = [
  [
    'icon' => '📚',
    'title' => $is_en ? 'WordPress Hardening Guide' : 'Guía de Endurecimiento de WordPress',
    'desc' => $is_en
      ? 'Checklist and best practices for securing WordPress sites.'
      : 'Checklist y buenas prácticas para asegurar sitios WordPress.',
    'link' => '#'
  ],
  [
    'icon' => '🔧',
    'title' => $is_en ? 'CI/CD Automation Template' : 'Plantilla de Automatización CI/CD',
    'desc' => $is_en
      ? 'GitHub Actions workflows for deployment and testing.'
      : 'Flujos de GitHub Actions para despliegue y pruebas.',
    'link' => '#'
  ],
  [
    'icon' => '⚡',
    'title' => $is_en ? 'Performance Checklist' : 'Checklist de Rendimiento',
    'desc' => $is_en
      ? 'Quick wins for reducing page load times and improving Core Web Vitals.'
      : 'Mejoras rápidas para reducir tiempos de carga y optimizar Core Web Vitals.',
    'link' => '#'
  ],
  [
    'icon' => '📊',
    'title' => $is_en ? 'SEO Technical Audit' : 'Auditoría Técnica SEO',
    'desc' => $is_en
      ? 'Scripts and methods for validating metadata and structured data.'
      : 'Scripts y métodos para validar metadatos y datos estructurados.',
    'link' => '#'
  ]
];
?>

<main class="container" style="padding:var(--space-5) 0;">
  <header class="page-header" style="margin-bottom:var(--space-5);">
    <h1 style="font-family:var(--font-title); color:var(--color-fg);"><?php echo esc_html($t_title); ?></h1>
    <p style="font-size:var(--font-size-step-1); color:var(--color-fg-muted); margin-top:var(--space-2);">
      <?php echo esc_html($t_intro); ?>
    </p>
  </header>

  <div class="grid" style="gap:var(--space-4);">
    <?php foreach ($resources as $res): ?>
      <article class="card" style="padding:var(--space-4); background:var(--color-surface); border:1px solid var(--color-border); border-radius:var(--radius-card);">
        <div style="font-size:2rem; margin-bottom:var(--space-2);"><?php echo $res['icon']; ?></div>
        <h2 style="font-family:var(--font-title); font-size:var(--font-size-step-1); color:var(--color-fg); margin-bottom:var(--space-2);">
          <?php echo esc_html($res['title']); ?>
        </h2>
        <p style="color:var(--color-fg-muted); margin-bottom:var(--space-3);">
          <?php echo esc_html($res['desc']); ?>
        </p>
        <?php if ($res['link'] !== '#'): ?>
          <a href="<?php echo esc_url($res['link']); ?>" class="cta-button" style="display:inline-block;">
            <?php echo $is_en ? 'View resource' : 'Ver recurso'; ?>
          </a>
        <?php endif; ?>
      </article>
    <?php endforeach; ?>
  </div>
</main>

<?php get_footer(); ?>
