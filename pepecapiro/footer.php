<footer class="site-footer">
  <?php
    $lang = function_exists('pll_current_language') ? pll_current_language('slug') : 'es';
    $is_en = ($lang === 'en');
    $t_links = $is_en ? 'Links' : 'Enlaces';
    $t_contact = $is_en ? 'Contact' : 'Contacto';
    $t_home = $is_en ? 'Home' : 'Inicio';
    $t_projects = $is_en ? 'Projects' : 'Proyectos';
    $t_blog = 'Blog';
    $t_priv = $is_en ? 'Privacy' : 'Privacidad';
    $t_cookies = 'Cookies';
    $t_cta = $is_en ? "Let's talk" : 'Hablemos';

    // Helpers para resolver URLs con fallback si la versión EN no existe
    $resolve_page = function($slug){
      $p = get_page_by_path($slug);
      return $p ? get_permalink($p) : '';
    };
    $pref = function($prefer, $fallback) use ($resolve_page){
      $u = $resolve_page($prefer);
      if ($u) return $u;
      $u2 = $resolve_page($fallback);
      return $u2 ?: home_url('/');
    };

    // Enlaces base
    $url_home = function_exists('pll_home_url') ? pll_home_url($is_en ? 'en' : 'es') : ($is_en ? home_url('/en/home/') : home_url('/'));
    $url_projects = $is_en ? home_url('/en/projects/') : home_url('/proyectos/');
    $url_blog = $is_en ? home_url('/en/blog-en/') : home_url('/blog/');
    // Legales: preferir EN si $is_en y existen, si no, fallback a ES
    $url_priv = $is_en ? $pref('privacy','privacidad') : $pref('privacidad','privacy');
    $url_cookies = $is_en ? $pref('cookies','cookies') : $pref('cookies','cookies');
    $url_contact = $is_en ? home_url('/en/contact/') : home_url('/contacto/');
    $mailto = $is_en ? 'mailto:contact@pepecapiro.com' : 'mailto:contacto@pepecapiro.com';
    $brand_blurb = $is_en
      ? 'Technical support and automation with a practical approach.'
      : 'Soporte técnico y automatización con enfoque práctico.';
  ?>
  <div class="container footer-grid">
    <div class="footer-col">
      <h3>Pepecapiro</h3>
      <p class="muted"><?php echo esc_html($brand_blurb); ?></p>
    </div>
    <div class="footer-col">
      <h3><?php echo esc_html($t_links); ?></h3>
      <nav>
        <a href="<?php echo esc_url($url_home); ?>"><?php echo esc_html($t_home); ?></a><br>
        <a href="<?php echo esc_url($url_projects); ?>"><?php echo esc_html($t_projects); ?></a><br>
        <a href="<?php echo esc_url($url_blog); ?>"><?php echo esc_html($t_blog); ?></a><br>
        <a href="<?php echo esc_url($url_priv); ?>"><?php echo esc_html($t_priv); ?></a><br>
        <a href="<?php echo esc_url($url_cookies); ?>"><?php echo esc_html($t_cookies); ?></a>
      </nav>
    </div>
    <div class="footer-col">
      <h3><?php echo esc_html($t_contact); ?></h3>
      <nav>
        <a href="<?php echo esc_attr($mailto); ?>"><?php echo $is_en ? 'contact@pepecapiro.com' : 'contacto@pepecapiro.com'; ?></a><br>
        <a href="<?php echo esc_url($url_contact); ?>" class="btn"><?php echo esc_html($t_cta); ?></a>
      </nav>
    </div>
  </div>
  <div class="container footer-bottom">
    <p class="muted" style="font-size:var(--step--1);">© <?php echo date('Y'); ?> Pepecapiro</p>
  </div>
</footer>
<?php wp_footer(); ?>
</body>
</html>
