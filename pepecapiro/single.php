<?php get_header(); ?>
<main class="container">
  <?php if (have_posts()): while(have_posts()): the_post(); ?>
    <article class="post-content">
      <?php if (has_post_thumbnail()): ?>
        <div style="margin-bottom:var(--space-lg);"><?php the_post_thumbnail('large', ['style'=>'width:100%;height:auto;border-radius:var(--radius-md);']); ?></div>
      <?php endif; ?>
      <h1><?php the_title(); ?></h1>
      <div><?php the_content(); ?></div>
    </article>
  <?php endwhile; endif; ?>
</main>
<?php get_footer(); ?>
