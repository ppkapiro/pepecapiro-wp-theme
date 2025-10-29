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
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="primary-menu">
      <span class="sr-only"><?php echo $is_en ? 'Open menu' : 'Abrir menú'; ?></span>
      <svg class="icon icon-menu" aria-hidden="true" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" focusable="false">
        <path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
      <svg class="icon icon-close" aria-hidden="true" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" focusable="false">
        <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
    </button>
    <div class="site-nav">
      <div id="primary-menu" class="site-nav__panel">
  <nav aria-label="<?php echo esc_attr($is_en ? 'Primary navigation' : 'Navegación principal'); ?>"><?php
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
    // Progresivo: marcar que hay JS
    document.documentElement.classList.add('js');
    var header = document.querySelector('.site-header');
    var btn = document.querySelector('.nav-toggle');
    var panel = document.getElementById('primary-menu');
    if (!header || !btn || !panel) return;

    // Inicial: colapsar panel cuando hay JS
    panel.setAttribute('hidden','');

    var overlay;
    function ensureOverlay(){
      if (!overlay){
        overlay = document.createElement('div');
        overlay.className = 'nav-overlay';
        overlay.setAttribute('aria-hidden','true');
      }
      return overlay;
    }

    function openMenu(){
      btn.setAttribute('aria-expanded','true');
      panel.removeAttribute('hidden');
      // Forzar reflow antes de abrir para transiciones de max-height/opacity
      void panel.offsetHeight;
      header.classList.add('nav-open');
      // foco al primer enlace del menú
      var firstLink = panel.querySelector('a');
      if (firstLink) setTimeout(function(){ firstLink.focus(); }, 0);
      // overlay clicable
      var ov = ensureOverlay();
      document.body.appendChild(ov);
      ov.addEventListener('click', closeMenu, { once: true });
      document.addEventListener('keydown', onKeyDown);
      document.addEventListener('click', onDocClick);
    }
    function closeMenu(){
      btn.setAttribute('aria-expanded','false');
      header.classList.remove('nav-open');
      // Esperar a que termine la transición para aplicar hidden
      var onEnd = function(){
        panel.setAttribute('hidden','');
        panel.removeEventListener('transitionend', onEnd);
      };
      panel.addEventListener('transitionend', onEnd);
      if (overlay && overlay.parentNode) overlay.parentNode.removeChild(overlay);
      document.removeEventListener('keydown', onKeyDown);
      document.removeEventListener('click', onDocClick);
    }
    function toggleMenu(){
      var expanded = btn.getAttribute('aria-expanded') === 'true';
      expanded ? closeMenu() : openMenu();
    }
    function onKeyDown(e){ if (e.key === 'Escape') { closeMenu(); btn.focus(); } }
    function onDocClick(e){
      if (!header.contains(e.target) && btn.getAttribute('aria-expanded') === 'true') closeMenu();
    }
    btn.addEventListener('click', toggleMenu);
    // Cerrar al hacer click en enlace
    panel.addEventListener('click', function(e){ if (e.target.closest('a')) closeMenu(); });
  } catch(e) { /* no-op */ }
})();
</script>
