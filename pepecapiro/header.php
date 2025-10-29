<!doctype html>
<html <?php language_attributes(); ?>>
<head>
  <meta charset="<?php bloginfo('charset'); ?>">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <!-- Preload fuente crítica del LCP (hero H1) -->
  <link rel="preload" href="<?php echo esc_url( get_stylesheet_directory_uri() ); ?>/assets/fonts/montserrat/Montserrat-Bold.woff2" as="font" type="font/woff2" crossorigin>
  <!-- Preconnect para recursos externos si los hubiera -->
  <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<a href="#main" class="sr-only focusable">Saltar al contenido</a>
<header class="site-header">
  <div class="container site-header__inner">
    <a class="brand" href="<?php echo esc_url(function_exists('pll_home_url') ? pll_home_url() : home_url('/')); ?>">Pepecapiro</a>
    <?php 
      $lang = function_exists('pll_current_language') ? pll_current_language('slug') : 'es';
      $is_en = ($lang === 'en');
    ?>
    <button class="nav-toggle" aria-expanded="false" aria-controls="primary-menu">
      <span class="sr-only"><?php echo $is_en ? 'Open menu' : 'Abrir menú'; ?></span>
      <span aria-hidden="true">☰</span>
    </button>
    <div class="site-nav">
      <div id="primary-menu" class="site-nav__panel">
        <nav><?php
        $fallback = function(){ wp_nav_menu(['theme_location'=>'primary','container'=>false]); };
        if (function_exists('pll_current_language')) {
          $lang = pll_current_language('slug');
          $map  = ['es' => 'Principal ES', 'en' => 'Main EN'];
            $menu_name = $map[$lang] ?? null;
            if ($menu_name && wp_get_nav_menu_object($menu_name)) {
              wp_nav_menu(['menu'=>$menu_name,'container'=>false]);
            } else { $fallback(); }
        } else { $fallback(); }
      ?></nav>
      <?php if (function_exists('pll_the_languages')): ?>
        <div class="lang-switcher" aria-label="<?php echo $is_en ? 'Change language' : 'Cambiar idioma'; ?>"><?php pll_the_languages(['show_flags'=>1,'show_names'=>0]); ?></div>
      <?php endif; ?>
      </div>
    </div>
  </div>
</header>

<script>
(function(){
  try {
    var header = document.querySelector('.site-header');
    var btn = document.querySelector('.nav-toggle');
    var panel = document.getElementById('primary-menu');
    if (!header || !btn || !panel) return;
    btn.addEventListener('click', function(){
      var expanded = this.getAttribute('aria-expanded') === 'true';
      this.setAttribute('aria-expanded', String(!expanded));
      header.classList.toggle('nav-open');
    });
  } catch(e) { /* no-op */ }
})();
</script>
