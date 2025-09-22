<?php get_header(); ?>
<main style="max-width:960px;margin:40px auto;padding:0 16px;">
  <h1>Pepecapiro — Tema base</h1>
  <p>Si ves esto, el tema está activo.</p>
  <?php if (have_posts()) : while (have_posts()) : the_post(); ?>
    <article>
      <h2><?php the_title(); ?></h2>
      <div><?php the_content(); ?></div>
    </article>
  <?php endwhile; else: ?>
    <p>No hay contenidos aún.</p>
  <?php endif; ?>
</main>
<?php get_footer(); ?>
