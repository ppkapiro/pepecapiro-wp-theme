<?php
/*
 * Template Name: About
 * Template Post Type: page
 */
get_header();

$lang = function_exists('pll_current_language') ? pll_current_language('slug') : 'es';
$is_en = ($lang === 'en');

$t_title = $is_en ? 'About' : 'Sobre mí';
$t_intro = $is_en
  ? "I'm Pepe Capiro, AI and Technology consultant. I help SMBs and IT teams optimize processes with practical automation and applied AI, generating measurable results."
  : 'Soy Pepe Capiro, consultor en IA y Tecnología. Ayudo a pymes y equipos IT a optimizar procesos con automatización práctica y IA aplicada, generando resultados medibles.';
$t_cta_linkedin = $is_en ? 'Connect on LinkedIn' : 'Conecta en LinkedIn';
$t_cta_contact = $is_en ? 'Schedule a call' : 'Agendar llamada';
$t_cta_contact_url = $is_en ? home_url('/en/contact/') : home_url('/contacto/');
$linkedin_url = 'https://linkedin.com/in/pepecapiro';
?>

<main id="main" class="site-main container" role="main" style="padding:var(--space-5) 0;">
  <h1 style="font-family:var(--font-title); font-size:var(--font-size-step-3); color:var(--color-fg); margin-bottom:var(--space-5);">
    <?php echo esc_html($t_title); ?>
  </h1>
  <div class="about-grid" style="display:grid; gap:var(--space-5); grid-template-columns:1fr 1fr; align-items:center;">
    <div>
      <p style="font-size:var(--font-size-step-1); color:var(--color-fg); line-height:1.6; margin-bottom:var(--space-4);">
        <?php echo esc_html($t_intro); ?>
      </p>
      <div class="about-ctas" style="display:flex; flex-wrap:wrap; gap:var(--space-3);">
        <a class="cta-button" href="<?php echo esc_url($linkedin_url); ?>" target="_blank" rel="noopener" style="display:inline-block; padding:var(--space-2) var(--space-4); background:var(--color-accent); color:var(--color-bg); font-weight:700; border-radius:var(--radius-button); text-decoration:none; transition:opacity 0.2s; outline:none; border:2px solid transparent;">
          <?php echo esc_html($t_cta_linkedin); ?>
        </a>
        <a class="cta-button cta-secondary" href="<?php echo esc_url($t_cta_contact_url); ?>" style="display:inline-block; padding:var(--space-2) var(--space-4); background:var(--color-surface); color:var(--color-fg); font-weight:700; border-radius:var(--radius-button); border:2px solid var(--color-border); text-decoration:none; transition:opacity 0.2s; outline:none;">
          <?php echo esc_html($t_cta_contact); ?>
        </a>
      </div>
    </div>
    <div style="display:flex; align-items:center; justify-content:center;">
      <?php
        // SVG placeholder inline para evitar 403 de imágenes del tema
        echo '<svg class="about__img" viewBox="0 0 800 500" role="img" aria-label="Placeholder" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto;">'
           . '<rect width="800" height="500" fill="#e6e6e6"/>'
           . '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#888" font-family="var(--font-title)" font-size="24">Imagen temporal</text>'
           . '</svg>';
      ?>
    </div>
  </div>
</main>

<?php get_footer(); ?>

