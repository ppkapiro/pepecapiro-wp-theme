<?php
add_action('after_setup_theme', function(){
  add_theme_support('title-tag');
  add_theme_support('post-thumbnails');
  // Carga de textdomain para i18n
  load_theme_textdomain('pepecapiro', get_template_directory() . '/languages');
  register_nav_menus([
    'primary' => __('Menú principal','pepecapiro')
  ]);
});

add_action('wp_enqueue_scripts', function(){
  $theme_version = wp_get_theme()->get('Version');
  $theme_dir = get_stylesheet_directory();
  $css_base = $theme_dir . '/assets/css/theme';
  $preferred = file_exists($css_base . '.min.css') ? $css_base . '.min.css' : $css_base . '.css';
  $version = $theme_version;
  if ( file_exists( $preferred ) ) {
      $version = filemtime( $preferred );
  }
  $public_path = get_stylesheet_directory_uri() . '/assets/css/' . basename($preferred);
  wp_enqueue_style('pepecapiro-theme', $public_path, [], $version);

  // Enqueue tokens CSS (Design System) después del CSS principal
  $tokens_file = $theme_dir . '/assets/css/tokens.css';
  if ( file_exists($tokens_file) ) {
    wp_enqueue_style('pepecapiro-tokens', get_stylesheet_directory_uri() . '/assets/css/tokens.css', ['pepecapiro-theme'], filemtime($tokens_file));
  }

  // Critical CSS opcional
  $critical_file = $theme_dir . '/assets/css/critical.css';
  if ( file_exists( $critical_file ) ) {
    $crit_ver = filemtime($critical_file);
    $crit_uri = get_stylesheet_directory_uri() . '/assets/css/critical.css?ver=' . $crit_ver;
    echo '<link rel="preload" as="style" href="' . esc_url($crit_uri) . '" />' . "\n";
    $css_inline = file_get_contents($critical_file);
    if ( strlen($css_inline) < 12000 ) { // salvaguarda tamaño
      echo '<style>' . wp_kses_post($css_inline) . '</style>' . "\n";
    }
  }
});

// Resource hints adicionales podrían agregarse aquí si se usan CDNs

// SEO mínimo OpenGraph / Twitter
add_action('wp_head', function(){
  if (is_admin()) return;
  $title = wp_get_document_title();
  $desc  = get_bloginfo('description');
  $url   = esc_url(home_url(add_query_arg([], $_SERVER['REQUEST_URI'] ?? '')));
  echo "\n<!-- SEO base -->\n";
  echo '<meta property="og:title" content="'.esc_attr($title).'" />' . "\n";
  echo '<meta property="og:type" content="'. (is_singular() ? 'article' : 'website') .'" />' . "\n";
  echo '<meta property="og:url" content="'.$url.'" />' . "\n";
  echo '<meta name="twitter:card" content="summary_large_image" />' . "\n";
  
  // OG específico para Home ES/EN
  if (is_front_page() || is_page_template('page-home.php')) {
    $is_en = function_exists('pll_current_language') ? (pll_current_language('slug') === 'en') : (strpos($url, '/en/') !== false);
    if ($is_en) {
      $og_title = 'Technical support and automation—without the headache.';
      $og_desc  = 'I fix what’s urgent today and simplify your processes for tomorrow.';
    } else {
      $og_title = 'Soporte técnico y automatización, sin drama.';
      $og_desc  = 'Arreglo lo urgente hoy y dejo procesos más simples para mañana.';
    }
    $og_img_path = get_stylesheet_directory() . '/assets/og/og-home.png';
    $og_img_url  = get_stylesheet_directory_uri() . '/assets/og/og-home.png';
    echo '<meta property="og:title" content="'.esc_attr($og_title).'" />' . "\n";
    echo '<meta property="og:description" content="'.esc_attr($og_desc).'" />' . "\n";
    echo '<meta property="og:image" content="'.esc_url($og_img_url).'" />' . "\n";
    echo '<meta property="og:image:width" content="1200" />' . "\n";
    echo '<meta property="og:image:height" content="630" />' . "\n";
  }
}, 5);

// Desregistrar CSS de bloques y global-styles en el FRONT (no afecta editor)
add_action('wp_enqueue_scripts', function () {
  if (!is_admin()) {
    // Librería base de bloques
    wp_dequeue_style('wp-block-library');
    wp_deregister_style('wp-block-library');

    // Algunas instalaciones usan estas handles adicionales
    wp_dequeue_style('wp-block-library-theme');
    wp_deregister_style('wp-block-library-theme');

    // Estilos globales (theme.json) en WP >= 5.9
    wp_dequeue_style('global-styles');
    wp_deregister_style('global-styles');
  }
}, 100);

// Breadcrumbs simples
function pc_breadcrumbs(){
  if (is_front_page()) return;
  echo '<nav aria-label="breadcrumb" class="container" style="font-size:14px;margin:12px 0;">';
  echo '<a href="'.esc_url(home_url('/')).'">Inicio</a> » ';
  if (is_singular('post')){
    $posts_page = get_option('page_for_posts');
    if ($posts_page) {
      echo '<a href="'.esc_url(get_permalink($posts_page)).'">Blog</a> » ';
    }
  }
  if (is_archive()){
    the_archive_title('<span>','</span>');
  } elseif (is_singular()){
    the_title('<span>','</span>');
  } elseif (is_404()) {
    echo '<span>404</span>';
  }
  echo '</nav>';
}
add_action('wp_body_open','pc_breadcrumbs');
