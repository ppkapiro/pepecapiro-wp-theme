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
  $url   = esc_url(home_url(add_query_arg([], $_SERVER['REQUEST_URI'] ?? '')));
  $is_home = (is_front_page() || is_page_template('page-home.php'));
  $is_en = function_exists('pll_current_language') ? (pll_current_language('slug') === 'en') : (strpos($url, '/en/') !== false);

  // Base
  $title = wp_get_document_title();
  $desc  = get_bloginfo('description');

  // Overrides para Home con copy definido
  if ($is_home) {
    if ($is_en) {
      $title = 'Technical support and automation—without the headache.';
      $desc  = 'I fix what’s urgent today and simplify your processes for tomorrow.';
    } else {
      $title = 'Soporte técnico y automatización, sin drama.';
      $desc  = 'Arreglo lo urgente hoy y dejo procesos más simples para mañana.';
    }
  }

  echo "\n<!-- SEO base -->\n";
  echo '<meta property="og:title" content="'.esc_attr($title).'" />' . "\n";
  echo '<meta property="og:description" content="'.esc_attr($desc).'" />' . "\n";
  echo '<meta property="og:type" content="'. (is_singular() ? 'article' : 'website') .'" />' . "\n";
  echo '<meta property="og:url" content="'.$url.'" />' . "\n";
  echo '<meta name="twitter:card" content="summary_large_image" />' . "\n";

  // Imagen OG para Home
  if ($is_home) {
    $og_img_url  = get_stylesheet_directory_uri() . ( $is_en ? '/assets/og/og-home-en.png' : '/assets/og/og-home-es.png' );
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

// ===== Contact form handler (admin-post.php) =====
function pc_contact_handle_submit(){
  $lang = function_exists('pll_current_language') ? pll_current_language('slug') : 'es';
  $is_en = ($lang === 'en');
  $redirect = $is_en ? home_url('/en/contact') : home_url('/contacto');

  if ( ! isset($_POST['pc_contact_nonce']) || ! wp_verify_nonce( $_POST['pc_contact_nonce'], 'pc_contact_form') ){
    wp_safe_redirect( add_query_arg('status','error',$redirect) );
    exit;
  }
  $hp = isset($_POST['hp']) ? trim((string)$_POST['hp']) : '';
  if ($hp !== ''){
    wp_safe_redirect( add_query_arg('status','ok',$redirect) ); // simular éxito para bots
    exit;
  }

  $name = isset($_POST['name']) ? sanitize_text_field($_POST['name']) : '';
  $email = isset($_POST['email']) ? sanitize_email($_POST['email']) : '';
  $message = isset($_POST['message']) ? wp_kses_post($_POST['message']) : '';

  if ( empty($name) || empty($email) || !is_email($email) || empty($message) ){
    wp_safe_redirect( add_query_arg('status','error',$redirect) );
    exit;
  }

  $to = $is_en ? (get_option('pc_contact_to_en') ?: 'contact@pepecapiro.com') : (get_option('pc_contact_to_es') ?: 'contacto@pepecapiro.com');
  $subject = $is_en ? 'New contact from website' : 'Nuevo contacto desde la web';
  $body  = ( $is_en ? "Name" : "Nombre" ) . ": $name\n";
  $body .= "Email: $email\n\n";
  $body .= ( $is_en ? "Message:" : "Mensaje:" ) . "\n" . wp_strip_all_tags($message) . "\n";

  $headers = [];
  $from = $is_en ? (get_option('pc_contact_from_en') ?: 'contact@pepecapiro.com') : (get_option('pc_contact_from_es') ?: 'contacto@pepecapiro.com');
  $headers[] = 'From: Pepecapiro <' . $from . '>';
  $headers[] = 'Reply-To: ' . $name . ' <' . $email . '>';

  $sent = wp_mail($to, $subject, $body, $headers);
  $status = $sent ? 'ok' : 'error';
  wp_safe_redirect( add_query_arg('status',$status,$redirect) );
  exit;
}
add_action('admin_post_pc_contact_submit', 'pc_contact_handle_submit');
add_action('admin_post_nopriv_pc_contact_submit', 'pc_contact_handle_submit');

// ===== SMTP (PHPMailer) configurable =====
add_action('phpmailer_init', function($phpmailer){
  // Si ya hay un plugin de SMTP activo, no forzar
  if (has_action('wp_mail_smtp_core_before_send') || class_exists('WPMailSMTP\Core')) { return; }

  $host = getenv('SMTP_HOST') ?: get_option('pc_smtp_host');
  $port = getenv('SMTP_PORT') ?: get_option('pc_smtp_port');
  $user = getenv('SMTP_USER') ?: get_option('pc_smtp_user');
  $pass = getenv('SMTP_PASS') ?: get_option('pc_smtp_pass');
  $secure = getenv('SMTP_SECURE') ?: (get_option('pc_smtp_secure') ?: 'tls'); // 'ssl' o 'tls'

  if (!$host || !$port || !$user || !$pass) { return; }

  $phpmailer->isSMTP();
  $phpmailer->Host = $host;
  $phpmailer->Port = (int)$port;
  $phpmailer->SMTPAuth = true;
  $phpmailer->Username = $user;
  $phpmailer->Password = $pass;
  $phpmailer->SMTPSecure = $secure; // 'ssl' o 'tls'
});
