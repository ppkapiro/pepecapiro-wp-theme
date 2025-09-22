<?php get_header(); ?>
<main>
  <section class="hero">
    <?php if (has_post_thumbnail()): ?>
      <div style="margin:0 0 24px;">
        <?php the_post_thumbnail('large', [
          'fetchpriority' => 'high',
          'decoding' => 'async',
          'style' => 'width:100%;height:auto;display:block;border-radius:16px;'
        ]); ?>
      </div>
    <?php endif; ?>
    <div class="container">
      <h1 class="title">Consultor en IA y Tecnología</h1>
      <p class="subtitle">Optimización de procesos, integración de IA y valor para pymes y equipos IT en Miami.</p>
      <a class="btn btn-primary" href="<?php echo esc_url(home_url('/contacto')); ?>">Descubre cómo</a>
    </div>
  </section>

  <section class="container">
    <div class="grid3">
      <div class="card">
        <h3>Automatización práctica</h3>
        <p>Flujos simples que ahorran horas cada semana.</p>
      </div>
      <div class="card">
        <h3>IA aplicada</h3>
        <p>Casos reales con impacto medible.</p>
      </div>
      <div class="card">
        <h3>Resultados</h3>
        <p>Métricas claras y documentación limpia.</p>
      </div>
    </div>
  </section>
</main>
<?php get_footer(); ?>
