<?php get_header(); ?>
<main>
  <section class="hero">
    <div class="container">
      <h1>Soporte técnico y automatización, sin drama.</h1>
      <p class="subtitle">Arreglo lo urgente hoy y dejo procesos más simples para mañana.</p>
      <a class="btn" href="<?php echo esc_url(home_url('/contacto')); ?>">Hablemos</a>
    </div>
  </section>

  <section class="container cards">
    <div class="grid">
      <div class="card">
        <h3>Automatización práctica</h3>
        <p>Problema: tareas repetitivas. Solución: flujos simples. Entregables: scripts y documentado.</p>
        <a class="btn btn--ghost" href="<?php echo esc_url(home_url('/proyectos/')); ?>">Ver servicios</a>
      </div>
      <div class="card">
        <h3>IA aplicada</h3>
        <p>Problema: baja eficiencia. Solución: IA en procesos. Entregables: pilotos y SOPs.</p>
        <a class="btn btn--ghost" href="<?php echo esc_url(home_url('/proyectos/')); ?>">Ver servicios</a>
      </div>
      <div class="card">
        <h3>Resultados</h3>
        <p>Problema: falta de métricas. Solución: KPIs y trazabilidad. Entregables: tableros y guías.</p>
        <a class="btn btn--ghost" href="<?php echo esc_url(home_url('/proyectos/')); ?>">Ver servicios</a>
      </div>
    </div>
  </section>

  <section class="container">
    <h2>Proyectos destacados</h2>
    <div class="grid">
      <div class="card"><h3>Notefy</h3><p>Contexto → acción → resultado (placeholder).</p></div>
      <div class="card"><h3>Automations</h3><p>Contexto → acción → resultado (placeholder).</p></div>
    </div>
  </section>

  <section class="container">
    <h2>Confían en mí</h2>
    <div class="grid">
      <div class="card"><p class="muted">Logos / Testimonio (placeholder)</p></div>
    </div>
  </section>

  <section class="container" style="margin: var(--space-6) auto; text-align:center;">
    <h2>¿Listos para empezar?</h2>
    <p class="subtitle">Conversemos 15 minutos para identificar el siguiente paso.</p>
    <a class="btn" href="<?php echo esc_url(home_url('/contacto')); ?>">Hablemos</a>
  </section>
</main>
<?php get_footer(); ?>
