<?php get_header(); ?>
<main class="container" style="padding:32px 0;">
  <?php if (have_posts()): while(have_posts()): the_post(); ?>
    <article>
      <?php if (has_post_thumbnail()): ?>
        <div style="margin-bottom:16px;"><?php the_post_thumbnail('large', ['style'=>'width:100%;height:auto;border-radius:12px;']); ?></div>
      <?php endif; ?>
      <h1 style="font-family:var(--ff-title)"><?php the_title(); ?></h1>
      <div><?php the_content(); ?></div>
    </article>
  <?php endwhile; endif; ?>
</main>
<?php get_footer(); ?>
