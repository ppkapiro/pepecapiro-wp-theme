<!doctype html>
<html <?php language_attributes(); ?>>
<head>
  <meta charset="<?php bloginfo('charset'); ?>">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <!-- Preload de la fuente crítica del LCP -->
  <link rel="preload" href="<?php echo esc_url( get_stylesheet_directory_uri() ); ?>/assets/fonts/montserrat/Montserrat-Bold.woff2" as="font" type="font/woff2" crossorigin>
  <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<header class="site-header">
  <div class="container site-header__inner">
    <a class="brand" href="<?php echo esc_url(function_exists('pll_home_url') ? pll_home_url() : home_url('/')); ?>">Pepecapiro</a>
  <div class="site-nav">
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
  <div class="lang-switcher"><?php pll_the_languages(['show_flags'=>1,'show_names'=>0]); ?></div>
      <?php else: ?>
        <div class="lang-switcher">
          <a href="<?php echo esc_url(home_url('/')); ?>">ES</a> |
          <a href="<?php echo esc_url(home_url('/en/')); ?>">EN</a>
        </div>
      <?php endif; ?>
    </div>
  </div>
</header>
