<?php get_header(); ?>
<main class="container" style="padding:32px 0;">
  <h1 style="font-family:var(--ff-title)">Buscar</h1>
  <?php get_search_form(); ?>
  <div style="margin-top:20px;">
  <?php if (have_posts()): while(have_posts()): the_post(); ?>
    <article style="margin:12px 0;">
      <h3><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
      <div><?php the_excerpt(); ?></div>
    </article>
  <?php endwhile; the_posts_pagination(); else: ?>
    <p>Sin resultados.</p>
  <?php endif; ?>
  </div>
</main>
<?php get_footer(); ?>
