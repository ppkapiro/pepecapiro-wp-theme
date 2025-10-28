<?php
/*
Template Name: Contacto (Bilingüe)
*/
get_header();
$lang = function_exists('pll_current_language') ? pll_current_language('slug') : 'es';
$is_en = ($lang === 'en');

$title = $is_en ? 'Contact' : 'Contacto';
$intro = $is_en ? 'Prefer email? It’s okay — use the link below. Otherwise, fill this form.' : '¿Prefieres correo? Usa el enlace abajo. Si no, completa este formulario.';
$mailto = $is_en ? 'mailto:contact@pepecapiro.com?subject=Contact' : 'mailto:contacto@pepecapiro.com?subject=Contacto';
$mailto_label = $is_en ? 'Write me by email' : 'Escríbeme por correo';
$success = $is_en ? "Thanks, I’ll get back to you soon." : 'Gracias, te respondo pronto.';
$error = $is_en ? "Couldn’t send. Please email me at contact@pepecapiro.com" : 'No se pudo enviar. Escríbeme a contacto@pepecapiro.com';

// Estado desde query vars (admin-post redirige aquí con ?status=ok|error)
$status = isset($_GET['status']) ? sanitize_text_field($_GET['status']) : '';
?>

<main class="container">
  <h1><?php echo esc_html($title); ?></h1>
  <p class="muted"><?php echo esc_html($intro); ?></p>

  <p><a class="btn btn--ghost" href="<?php echo esc_url($mailto); ?>"><?php echo esc_html($mailto_label); ?></a></p>

  <div class="card">
    <div role="status" aria-live="polite" class="muted" style="min-height:1.2em; margin-bottom: var(--space-md);">
      <?php if ($status === 'ok'): ?>
        <span><?php echo esc_html($success); ?></span>
      <?php elseif ($status === 'error'): ?>
        <span><?php echo esc_html($error); ?></span>
      <?php endif; ?>
    </div>

    <form method="post" action="<?php echo esc_url( admin_url('admin-post.php') ); ?>" novalidate>
      <?php wp_nonce_field('pc_contact_form','pc_contact_nonce'); ?>
      <input type="hidden" name="action" value="pc_contact_submit" />
      <div class="form-row">
        <label for="pc_name"><?php echo $is_en ? 'Name' : 'Nombre'; ?> *</label>
        <input id="pc_name" name="name" type="text" required />
      </div>
      <div class="form-row">
        <label for="pc_email">Email *</label>
        <input id="pc_email" name="email" type="email" required />
      </div>
      <div class="form-row">
        <label for="pc_message"><?php echo $is_en ? 'Message' : 'Mensaje'; ?> *</label>
        <textarea id="pc_message" name="message" rows="6" required></textarea>
      </div>
      <!-- honeypot -->
      <div class="hp-field" aria-hidden="true">
        <label for="pc_hp">Leave this field empty</label>
        <input id="pc_hp" name="hp" type="text" tabindex="-1" autocomplete="off" />
      </div>
      <button class="btn" type="submit"><?php echo esc_html( $is_en ? "Send" : "Enviar" ); ?></button>
    </form>
  </div>
</main>

<?php get_footer(); ?>
