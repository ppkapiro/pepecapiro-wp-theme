<?php get_header(); ?>
<main class="container" style="padding:32px 0;">
  <h1 style="font-family:var(--ff-title)"><?php the_archive_title(); ?></h1>
  <?php if (have_posts()): ?>
    <?php while(have_posts()): the_post(); ?>
      <article style="margin:12px 0;">
        <h3><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
        <div><?php the_excerpt(); ?></div>
      </article>
    <?php endwhile; the_posts_pagination(); ?>
  <?php else: ?>
    <p>Sin entradas.</p>
  <?php endif; ?>
</main>
<?php get_footer(); ?>
