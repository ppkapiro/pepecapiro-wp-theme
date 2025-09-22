<?php get_header(); ?>
<main class="container" style="padding:32px 0;">
  <?php if (have_posts()): while(have_posts()): the_post(); ?>
    <article>
      <h1 style="font-family:var(--ff-title)"><?php the_title(); ?></h1>
      <div><?php the_content(); ?></div>
    </article>
  <?php endwhile; else: ?>
    <p>No hay contenidos.</p>
  <?php endif; ?>
</main>
<?php get_footer(); ?>
