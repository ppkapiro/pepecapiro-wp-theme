<?php
/*
Template Name: Sobre mí (MVP)
*/
get_header();
?>

<main id="main" class="site-main container">
  <h1>Sobre mí</h1>
  <div class="about-grid">
    <div>
      <p>Soy Pepe Capiro, consultor en IA y Tecnología. Ayudo a pymes y equipos IT a optimizar procesos con automatización práctica y IA aplicada, generando resultados medibles.</p>
      <div class="about-ctas">
        <a class="cta-button" href="https://linkedin.com/in/pepecapiro" target="_blank" rel="noopener">Conecta en LinkedIn</a>
        <a class="cta-button cta-secondary" href="<?php echo esc_url( home_url('/contacto/') ); ?>">Agendar llamada</a>
      </div>
    </div>
    <div>
      <?php
        // Nota: Evitamos servir imágenes desde la carpeta del tema porque el host las bloquea (403) en producción.
        // Usamos un placeholder inline (SVG) para no generar peticiones adicionales ni 404/403.
        echo '<svg class="about__img" viewBox="0 0 800 500" role="img" aria-label="Placeholder" xmlns="http://www.w3.org/2000/svg">'
           . '<rect width="800" height="500" fill="#e6e6e6"/>'
           . '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#888" font-family="sans-serif" font-size="24">Imagen temporal</text>'
           . '</svg>';
      ?>
    </div>
  </div>
</main>

<?php get_footer(); ?>
