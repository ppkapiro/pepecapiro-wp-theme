<?php
/*
 * Template Name: Projects
 * Template Post Type: page
 */
get_header();

$lang = function_exists('pll_current_language') ? pll_current_language('slug') : 'es';
$is_en = ($lang === 'en');

$t_title = $is_en ? 'Projects' : 'Proyectos';
$t_intro = $is_en
  ? 'Selected projects showcasing practical solutions and automation.'
  : 'Proyectos seleccionados que muestran soluciones prácticas y automatización.';

// Placeholder projects (estructura estática)
$projects = [
  [
    'title' => $is_en ? 'Automation System' : 'Sistema de Automatización',
    'desc' => $is_en
      ? 'Automated deployment and monitoring workflows for small businesses.'
      : 'Flujos de despliegue y monitoreo automatizados para pequeñas empresas.',
    'link' => '#'
  ],
  [
    'title' => $is_en ? 'Legacy Migration' : 'Migración de Legado',
    'desc' => $is_en
      ? 'Migrated a WordPress site to modern infrastructure with zero downtime.'
      : 'Migración de un sitio WordPress a infraestructura moderna sin tiempo de inactividad.',
    'link' => '#'
  ],
  [
    'title' => $is_en ? 'Performance Optimization' : 'Optimización de Rendimiento',
    'desc' => $is_en
      ? 'Reduced page load times by 60% through targeted caching and asset optimization.'
      : 'Reducción de tiempos de carga en 60% mediante caché y optimización de assets.',
    'link' => '#'
  ]
];
?>

<main class="container" role="main">
  <header class="page-header">
    <h1><?php echo esc_html($t_title); ?></h1>
    <p>
      <?php echo esc_html($t_intro); ?>
    </p>
  </header>

  <div class="grid" role="list" aria-label="<?php echo $is_en ? 'Project list' : 'Lista de proyectos'; ?>">
    <?php foreach ($projects as $proj): ?>
      <article class="card" role="listitem">
        <h2>
          <?php echo esc_html($proj['title']); ?>
        </h2>
        <p style="color:var(--color-text-secondary); margin-bottom:var(--space-md);">
          <?php echo esc_html($proj['desc']); ?>
        </p>
        <?php if ($proj['link'] !== '#'): ?>
          <a href="<?php echo esc_url($proj['link']); ?>" class="btn">
            <?php echo $is_en ? 'Learn more' : 'Ver más'; ?>
          </a>
        <?php endif; ?>
      </article>
    <?php endforeach; ?>
  </div>
</main>

<?php get_footer(); ?>
