<?php
/*
Template Name: Home (MVP)
*/
get_header();
?>

<main id="main" class="site-main">
  <section class="hero">
    <div class="container hero__inner">
      <div class="hero__text">
        <h1 class="hero__title">Consultor en IA y Tecnología — Optimización de procesos, integración de IA y generación de valor para pymes y equipos IT.</h1>
        <a class="cta-button" href="<?php echo esc_url( home_url('/contacto/') ); ?>">Descubre cómo la IA puede optimizar tu negocio</a>
      </div>
      <div class="hero__media">
        <?php
          // Evitar imágenes servidas desde la carpeta del tema (403 en producción). Usamos un SVG inline como placeholder.
          echo '<svg class="hero__img" viewBox="0 0 800 500" role="img" aria-label="Hero placeholder" xmlns="http://www.w3.org/2000/svg">'
             . '<defs><linearGradient id="g" x1="0" x2="1" y1="0" y2="1"><stop offset="0%" stop-color="#d0e6ff"/><stop offset="100%" stop-color="#e6f2ff"/></linearGradient></defs>'
             . '<rect width="800" height="500" fill="url(#g)"/>'
             . '<circle cx="650" cy="120" r="50" fill="#c5d9f1"/>'
             . '<rect x="60" y="360" width="300" height="24" rx="6" fill="#b0c8e6"/>'
             . '</svg>';
        ?>
      </div>
    </div>
  </section>

  <section class="container pilares">
    <div class="pilar-card">
      <span class="icon-placeholder" aria-hidden="true"></span>
      <h3>Automatización práctica</h3>
      <p>Identificamos tareas repetitivas y las automatizamos con herramientas accesibles para ganar tiempo y calidad.</p>
    </div>
    <div class="pilar-card">
      <span class="icon-placeholder" aria-hidden="true"></span>
      <h3>IA aplicada en Miami</h3>
      <p>Casos reales de integración de IA en pymes y equipos IT, con foco en impacto y adopción.</p>
    </div>
    <div class="pilar-card">
      <span class="icon-placeholder" aria-hidden="true"></span>
      <h3>Resultados medibles</h3>
      <p>Métricas claras y seguimiento para asegurar retorno de inversión y mejora continua.</p>
    </div>
  </section>
</main>

<?php get_footer(); ?>
