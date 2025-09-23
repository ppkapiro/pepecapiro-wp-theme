<footer class="site-footer">
  <div class="container footer-grid">
    <div class="footer-col">
      <h3>Pepecapiro</h3>
      <p class="muted">Soporte técnico y automatización con enfoque práctico.</p>
    </div>
    <div class="footer-col">
      <h3>Enlaces</h3>
      <nav>
        <a href="<?php echo esc_url(home_url('/')); ?>">Inicio</a><br>
        <a href="<?php echo esc_url(home_url('/proyectos/')); ?>">Proyectos</a><br>
        <a href="<?php echo esc_url(home_url('/blog/')); ?>">Blog</a>
      </nav>
    </div>
    <div class="footer-col">
      <h3>Contacto</h3>
      <nav>
        <a href="mailto:contacto@pepecapiro.com">contacto@pepecapiro.com</a><br>
        <a href="<?php echo esc_url(home_url('/contacto')); ?>" class="btn">Hablemos</a>
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
