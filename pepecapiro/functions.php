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
  // Enqueue tokens CSS (Design System) primero, para que las variables estén disponibles
  $tokens_file = $theme_dir . '/assets/css/tokens.css';
  if ( file_exists($tokens_file) ) {
    wp_enqueue_style('pepecapiro-tokens', get_stylesheet_directory_uri() . '/assets/css/tokens.css', [], filemtime($tokens_file));
  }

  // Encolar CSS de tema dependiendo de tokens (para usar las variables)
  $public_path = get_stylesheet_directory_uri() . '/assets/css/' . basename($preferred);
  wp_enqueue_style('pepecapiro-theme', $public_path, ['pepecapiro-tokens'], $version);

  // Utilidades pequeñas (p.ej., .sr-only)
  $utils_file = $theme_dir . '/assets/css/utilities.css';
  if ( file_exists($utils_file) ) {
    wp_enqueue_style('pepecapiro-utils', get_stylesheet_directory_uri() . '/assets/css/utilities.css', ['pepecapiro-theme'], filemtime($utils_file));
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

// Preload de fuentes críticas (woff2) para mejorar LCP
add_action('wp_head', function(){
  if (is_admin()) return;
  $base = get_stylesheet_directory_uri() . '/assets/fonts/';
  $fonts = [
    'montserrat/Montserrat-SemiBold.woff2',
    'opensans/OpenSans-Regular.woff2',
    'opensans/OpenSans-SemiBold.woff2',
  ];
  foreach ($fonts as $rel) {
    echo '<link rel="preload" href="'.esc_url($base.$rel).'" as="font" type="font/woff2" crossorigin />' . "\n";
  }
}, 1);

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

  // Canonical tag (simple). Si Polylang provee canonical, esto es complementario.
  $canonical = $url;
  echo '<link rel="canonical" href="'.esc_url($canonical).'" />' . "\n";

  // hreflang alternates si Polylang está activo
  if (function_exists('pll_the_languages')) {
    $langs = pll_the_languages(['raw'=>1]); // array con info
    if (is_array($langs)) {
      foreach($langs as $code=>$data){
        if (!empty($data['url'])){
          // normalizar: pll devuelve slug (es,en). Añadimos region genérica.
          $hreflang = $code; // se podría mapear a es-ES, en-US si se desea
          echo '<link rel="alternate" hreflang="'.esc_attr($hreflang).'" href="'.esc_url($data['url']).'" />' . "\n";
        }
      }
      // x-default apuntando a home root
      $home_default = function_exists('pll_home_url') ? pll_home_url() : home_url('/');
      echo '<link rel="alternate" hreflang="x-default" href="'.esc_url($home_default).'" />' . "\n";
    }
  }

  // JSON-LD: Organization/WebSite en Home + BreadcrumbList + (Article si singular post)
  $json_ld = [];
  if ($is_home) {
    $json_ld[] = [
      '@context' => 'https://schema.org',
      '@type' => 'Organization',
      'name' => 'Pepecapiro',
      'url' => home_url('/'),
      'logo' => get_stylesheet_directory_uri() . '/assets/og/og-home-es.png'
    ];
    $json_ld[] = [
      '@context' => 'https://schema.org',
      '@type' => 'WebSite',
      'url' => home_url('/'),
      'name' => 'Pepecapiro',
      'potentialAction' => [
        '@type' => 'SearchAction',
        'target' => home_url('/?s={search_term_string}'),
        'query-input' => 'required name=search_term_string'
      ]
    ];
  }
  // Breadcrumbs
  $breadcrumbs_items = [];
  $position = 1;
  $home_url = function_exists('pll_home_url') ? pll_home_url() : home_url('/');
  $breadcrumbs_items[] = [ 'position'=>$position++, 'name'=> ($is_en ? 'Home' : 'Inicio'), 'item'=>$home_url ];
  if (is_singular('post')) {
    $posts_page = get_option('page_for_posts');
    if ($posts_page) {
      $breadcrumbs_items[] = [ 'position'=>$position++, 'name'=> ($is_en ? 'Blog' : 'Blog'), 'item'=> get_permalink($posts_page) ];
    }
  }
  if (is_singular()) {
    $breadcrumbs_items[] = [ 'position'=>$position++, 'name'=> get_the_title(), 'item'=> get_permalink() ];
  } elseif (is_archive()) {
    $breadcrumbs_items[] = [ 'position'=>$position++, 'name'=> strip_tags(get_the_archive_title()), 'item'=> $url ];
  }
  if (count($breadcrumbs_items) > 1) {
    $json_ld[] = [
      '@context' => 'https://schema.org',
      '@type' => 'BreadcrumbList',
      'itemListElement' => array_map(function($it){
        return [
          '@type' => 'ListItem',
          'position' => $it['position'],
          'name' => wp_strip_all_tags($it['name']),
          'item' => $it['item']
        ];
      }, $breadcrumbs_items)
    ];
  }
  // Article schema
  if (is_singular('post')) {
    $author_name = get_the_author();
    $published = get_the_date('c');
    $modified = get_the_modified_date('c');
    $article = [
      '@context' => 'https://schema.org',
      '@type' => 'Article',
      'mainEntityOfPage' => [
        '@type' => 'WebPage',
        '@id' => get_permalink()
      ],
      'headline' => wp_strip_all_tags( get_the_title() ),
      'datePublished' => $published,
      'dateModified' => $modified,
      'author' => [
        '@type' => 'Person',
        'name' => $author_name
      ],
      'publisher' => [
        '@type' => 'Organization',
        'name' => 'Pepecapiro',
        'logo' => [
          '@type' => 'ImageObject',
          'url' => get_stylesheet_directory_uri() . '/assets/og/og-home-es.png'
        ]
      ],
      'inLanguage' => ( $is_en ? 'en' : 'es' ),
      'url' => get_permalink()
    ];
    if (has_post_thumbnail()) {
      $thumb_id = get_post_thumbnail_id();
      $img = wp_get_attachment_image_src($thumb_id, 'full');
      if ($img) {
        $article['image'] = [$img[0]];
      }
    }
    $json_ld[] = $article;
  }
  if (!empty($json_ld)) {
    echo '<script type="application/ld+json">'.wp_json_encode( count($json_ld)===1 ? $json_ld[0] : $json_ld , JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE ).'</script>' . "\n";
  }

  // Imagen OG dinámica según página y idioma
  $og_img_url = null;
  if ($is_home) {
    $og_img_url = get_stylesheet_directory_uri() . ( $is_en ? '/assets/og/og-home-en.png' : '/assets/og/og-home-es.png' );
  } elseif (is_page_template('page-about.php')) {
    $og_img_url = get_stylesheet_directory_uri() . ( $is_en ? '/assets/og/og-about-en.png' : '/assets/og/og-about-es.png' );
  } elseif (is_page_template('page-projects.php')) {
    $og_img_url = get_stylesheet_directory_uri() . ( $is_en ? '/assets/og/og-projects-en.png' : '/assets/og/og-projects-es.png' );
  } elseif (is_page_template('page-resources.php')) {
    $og_img_url = get_stylesheet_directory_uri() . ( $is_en ? '/assets/og/og-resources-en.png' : '/assets/og/og-resources-es.png' );
  }
  if ($og_img_url) {
    // Fallback si la imagen específica no existe en disco
    $path_guess = str_replace(get_stylesheet_directory_uri(), get_stylesheet_directory(), $og_img_url);
    if (!@file_exists($path_guess)) {
      $og_img_url = get_stylesheet_directory_uri() . ( $is_en ? '/assets/og/og-home-en.png' : '/assets/og/og-home-es.png' );
    }
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

// ===== SMTP config centralizada (env/constantes) =====
function pc_get_smtp_config(): array {
  // Leer de variables de entorno; wp-config.php puede definir putenv() como fallback
  $host   = getenv('SMTP_HOST') ?: '';
  $port   = getenv('SMTP_PORT') ?: '';
  $user   = getenv('SMTP_USER') ?: '';
  $pass   = getenv('SMTP_PASS') ?: '';
  $secure = getenv('SMTP_SECURE') ?: 'tls'; // ssl|tls
  $from_es = getenv('SMTP_FROM_ES') ?: '';
  $from_en = getenv('SMTP_FROM_EN') ?: '';

  return [
    'host' => $host,
    'port' => $port,
    'user' => $user,
    'pass' => $pass,
    'secure' => $secure,
    'from_es' => $from_es,
    'from_en' => $from_en,
    // flags de presencia (no exponen valores)
    '_present' => [
      'host' => !empty($host),
      'port' => !empty($port),
      'user' => !empty($user),
      'pass' => !empty($pass),
      'secure' => !empty($secure),
      'from_es' => !empty($from_es),
      'from_en' => !empty($from_en),
    ],
  ];
}

// ===== SMTP (PHPMailer) configurable por env; respeta plugins SMTP =====
add_action('phpmailer_init', function($phpmailer){
  // Si hay plugin SMTP conocido, no interferir
  if (has_action('wp_mail_smtp_core_before_send') || class_exists('WPMailSMTP\\Core') || class_exists('Postman\\Postman')) {
    return;
  }
  $cfg = pc_get_smtp_config();
  if (!$cfg['_present']['host'] || !$cfg['_present']['user'] || !$cfg['_present']['pass'] || !$cfg['_present']['port']) {
    return; // No configurar si no está completo
  }
  $phpmailer->isSMTP();
  $phpmailer->Host = $cfg['host'];
  $phpmailer->Port = (int)$cfg['port'];
  $phpmailer->SMTPAuth = true;
  $phpmailer->Username = $cfg['user'];
  $phpmailer->Password = $cfg['pass'];
  $phpmailer->SMTPSecure = $cfg['secure']; // 'ssl' o 'tls'
});

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
  // FROM preferido por env (sin exponer ni guardar en BD); fallback a opciones o estáticos
  $env = pc_get_smtp_config();
  $env_from = $is_en ? ($env['from_en'] ?? '') : ($env['from_es'] ?? '');
  $from = $env_from ?: ( $is_en ? (get_option('pc_contact_from_en') ?: 'contact@pepecapiro.com') : (get_option('pc_contact_from_es') ?: 'contacto@pepecapiro.com') );
  $headers[] = 'From: Pepecapiro <' . $from . '>';
  $headers[] = 'Reply-To: ' . $name . ' <' . $email . '>';

  $sent = wp_mail($to, $subject, $body, $headers);
  $status = $sent ? 'ok' : 'error';
  wp_safe_redirect( add_query_arg('status',$status,$redirect) );
  exit;
}
add_action('admin_post_pc_contact_submit', 'pc_contact_handle_submit');
add_action('admin_post_nopriv_pc_contact_submit', 'pc_contact_handle_submit');

// ===== Admin UI: Herramientas → Correo (Estado y Prueba) =====
add_action('admin_menu', function(){
  add_submenu_page(
    'tools.php',
    __('Correo — Estado y Prueba','pepecapiro'),
    __('Correo','pepecapiro'),
    'manage_options',
    'pc-mail',
    'pc_mail_admin_page'
  );
});

function pc_mail_admin_page(){
  if (!current_user_can('manage_options')) return;
  $cfg = pc_get_smtp_config();
  $page_url = add_query_arg(['page' => 'pc-mail'], admin_url('tools.php'));
  $status = isset($_GET['pcmt']) ? sanitize_text_field($_GET['pcmt']) : '';
  echo '<div class="wrap"><h1>'.esc_html__('Correo — Estado y Prueba','pepecapiro').'</h1>';
  if ($status === 'ok') {
    echo '<div class="notice notice-success"><p>'.esc_html__('Correo de prueba enviado. Revisa tu bandeja.','pepecapiro').'</p></div>';
  } elseif ($status === 'error') {
    echo '<div class="notice notice-error"><p>'.esc_html__('Error al enviar el correo de prueba. Revisa credenciales SMTP o usa el fallback mailto.','pepecapiro').'</p></div>';
  }

  echo '<h2>'.esc_html__('Estado de variables (presente/ausente)','pepecapiro').'</h2>';
  echo '<table class="widefat"><tbody>';
  $rows = [
    'SMTP_HOST' => $cfg['_present']['host'],
    'SMTP_PORT' => $cfg['_present']['port'],
    'SMTP_USER' => $cfg['_present']['user'],
    'SMTP_PASS' => $cfg['_present']['pass'],
    'SMTP_SECURE' => $cfg['_present']['secure'],
    'SMTP_FROM_ES' => $cfg['_present']['from_es'],
    'SMTP_FROM_EN' => $cfg['_present']['from_en'],
  ];
  foreach($rows as $k=>$present){
    echo '<tr><th>'.esc_html($k).'</th><td>'.($present?'<span style="color:green">presente</span>':'<span style="color:#c00">ausente</span>').'</td></tr>';
  }
  echo '</tbody></table>';

  echo '<h2 style="margin-top:16px;">'.esc_html__('Enviar correo de prueba','pepecapiro').'</h2>';
  echo '<form method="post" action="'.esc_url( admin_url('admin-post.php') ).'" class="card" style="padding:16px; max-width:640px;">';
  wp_nonce_field('pc_mail_test','pc_mail_test_nonce');
  echo '<input type="hidden" name="action" value="pc_mail_test" />';
  echo '<p><label for="pcmt_to">'.esc_html__('Enviar prueba a','pepecapiro').' *</label><br />';
  echo '<input type="email" id="pcmt_to" name="to" required style="width:100%; max-width:420px;" /></p>';
  echo '<p><button type="submit" class="button button-primary">'.esc_html__('Enviar correo de prueba','pepecapiro').'</button></p>';
  echo '</form>';
  echo '</div>';
}

function pc_mail_test_handler(){
  if (!current_user_can('manage_options')) wp_die('forbidden');
  if (!isset($_POST['pc_mail_test_nonce']) || !wp_verify_nonce($_POST['pc_mail_test_nonce'], 'pc_mail_test')) wp_die('invalid nonce');
  $to = isset($_POST['to']) ? sanitize_email($_POST['to']) : '';
  $redirect = add_query_arg(['page'=>'pc-mail'], admin_url('tools.php'));
  if (!$to || !is_email($to)){
    wp_safe_redirect( add_query_arg('pcmt','error',$redirect) ); exit;
  }
  $subject = '[pepecapiro] SMTP Test';
  $body = 'SMTP test at '.date('c')."\nSite: ".home_url('/')."\nUser agent: ".($_SERVER['HTTP_USER_AGENT'] ?? 'n/a')."\nIf you see this, SMTP works.";
  $cfg = pc_get_smtp_config();
  // Preferir FROM por idioma ES; si no, EN; luego fallback a dominio actual
  $from = $cfg['from_es'] ?: ($cfg['from_en'] ?: ('no-reply@'.parse_url(home_url(), PHP_URL_HOST)));
  $headers = [ 'From: Pepecapiro <'.$from.'>' ];
  $ok = wp_mail($to, $subject, $body, $headers);
  if (defined('WP_DEBUG') && WP_DEBUG && function_exists('error_log')){
    error_log('[pc-mail-test] to='.$to.' status=' . ($ok?'ok':'error'));
  }
  wp_safe_redirect( add_query_arg('pcmt', ($ok?'ok':'error'), $redirect) );
  exit;
}
add_action('admin_post_pc_mail_test','pc_mail_test_handler');

