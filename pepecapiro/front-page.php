<?php 
get_header(); 
$lang = function_exists('pll_current_language') ? pll_current_language('slug') : 'es';
$is_en = ($lang === 'en');
// Textos por idioma
$H1 = $is_en ? 'Technical support and automation—without the headache.' : 'Soporte técnico y automatización, sin drama.';
$SUB = $is_en ? "I fix what’s urgent today and simplify your processes for tomorrow." : "Arreglo lo urgente hoy y dejo procesos más simples para mañana.";
$CTA = $is_en ? "Let's talk" : "Hablemos";
$CTA_URL = $is_en ? home_url('/en/contact') : home_url('/contacto');
?>
<main>
  <section class="hero">
    <div class="container">
      <h1><?php echo esc_html($H1); ?></h1>
      <p class="subtitle"><?php echo esc_html($SUB); ?></p>
      <a class="btn" href="<?php echo esc_url($CTA_URL); ?>"><?php echo esc_html($CTA); ?></a>
    </div>
  </section>

  <section class="container cards">
    <div class="grid">
      <div class="card">
        <h3><?php echo $is_en ? 'Practical automation' : 'Automatización práctica'; ?></h3>
        <p><?php echo $is_en ? 'Problem: repetitive tasks. Solution: simple flows. Deliverables: scripts and documentation.' : 'Problema: tareas repetitivas. Solución: flujos simples. Entregables: scripts y documentado.'; ?></p>
        <a class="btn btn--ghost" href="<?php echo esc_url( $is_en ? home_url('/en/projects/') : home_url('/proyectos/') ); ?>"><?php echo $is_en ? 'View services' : 'Ver servicios'; ?></a>
      </div>
      <div class="card">
        <h3><?php echo $is_en ? 'Applied AI' : 'IA aplicada'; ?></h3>
        <p><?php echo $is_en ? 'Problem: low efficiency. Solution: AI in processes. Deliverables: pilots and SOPs.' : 'Problema: baja eficiencia. Solución: IA en procesos. Entregables: pilotos y SOPs.'; ?></p>
        <a class="btn btn--ghost" href="<?php echo esc_url( $is_en ? home_url('/en/projects/') : home_url('/proyectos/') ); ?>"><?php echo $is_en ? 'View services' : 'Ver servicios'; ?></a>
      </div>
      <div class="card">
        <h3><?php echo $is_en ? 'Results' : 'Resultados'; ?></h3>
        <p><?php echo $is_en ? 'Problem: lack of metrics. Solution: KPIs and traceability. Deliverables: dashboards and guides.' : 'Problema: falta de métricas. Solución: KPIs y trazabilidad. Entregables: tableros y guías.'; ?></p>
        <a class="btn btn--ghost" href="<?php echo esc_url( $is_en ? home_url('/en/projects/') : home_url('/proyectos/') ); ?>"><?php echo $is_en ? 'View services' : 'Ver servicios'; ?></a>
      </div>
    </div>
  </section>

  <section class="container">
    <h2><?php echo $is_en ? 'Featured projects' : 'Proyectos destacados'; ?></h2>
    <div class="grid">
      <div class="card"><h3>Notefy</h3><p><?php echo $is_en ? 'Context → action → outcome (placeholder).' : 'Contexto → acción → resultado (placeholder).'; ?></p></div>
      <div class="card"><h3>Automations</h3><p><?php echo $is_en ? 'Context → action → outcome (placeholder).' : 'Contexto → acción → resultado (placeholder).'; ?></p></div>
    </div>
  </section>

  <section class="container">
    <h2><?php echo $is_en ? 'Trusted by' : 'Confían en mí'; ?></h2>
    <div class="grid">
      <div class="card"><p class="muted"><?php echo $is_en ? 'Logos / Testimonial (placeholder)' : 'Logos / Testimonio (placeholder)'; ?></p></div>
    </div>
  </section>

  <section class="container section-center">
    <h2><?php echo $is_en ? 'Ready to start?' : '¿Listos para empezar?'; ?></h2>
    <p class="subtitle"><?php echo $is_en ? 'Let’s talk for 15 minutes to identify the next step.' : 'Conversemos 15 minutos para identificar el siguiente paso.'; ?></p>
    <a class="btn" href="<?php echo esc_url($CTA_URL); ?>"><?php echo esc_html($CTA); ?></a>
  </section>
</main>
<?php get_footer(); ?>
