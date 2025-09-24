<?php
/*
Template Name: Blog Listing
Description: Lista entradas recientes bilingüe sin depender de page_for_posts.
*/
get_header();
?>
<main class="container" style="padding:48px 0;max-width:960px;">
  <header style="margin-bottom:32px;">
    <h1 style="font-family:var(--ff-title);font-size:clamp(1.8rem,4vw,2.6rem);margin:0 0 8px;">
      <?php the_title(); ?>
    </h1>
    <?php if(get_the_excerpt()) : ?>
      <p style="color:var(--color-fg-muted);margin:0;"><?php echo esc_html( get_the_excerpt() ); ?></p>
    <?php endif; ?>
  </header>

  <?php
  // Soporte paginación propia de plantilla.
  $paged = (get_query_var('paged')) ? get_query_var('paged') : 1;
  $args = [
    'post_type' => 'post',
    'post_status' => 'publish',
    'paged' => $paged,
    'posts_per_page' => 10,
  ];
  if (function_exists('pll_current_language')) {
    $args['lang'] = pll_current_language();
  }
  $q = new WP_Query($args);
  echo "<!-- posts_found:" . intval($q->found_posts) . " lang:" . (function_exists('pll_current_language')?pll_current_language():'na') . " -->"; 
  // Div oculto de depuración (más fiable que comentario si el caché elimina comments)
  echo '<div id="blog-query-info" style="display:none" data-posts="'.intval($q->found_posts).'" data-lang="'.(function_exists('pll_current_language')?esc_attr(pll_current_language()):'na').'"></div>';
  ?>

  <?php if($q->have_posts()): ?>
    <div class="blog-list" style="display:grid;gap:32px;">
      <?php while($q->have_posts()): $q->the_post(); ?>
        <article style="border:1px solid var(--color-border);padding:20px;border-radius:var(--radius);background:var(--color-surface);">
          <h2 style="margin:0 0 8px;font-size:1.25rem;">
            <a href="<?php the_permalink(); ?>" style="text-decoration:none;color:var(--color-fg);">
              <?php the_title(); ?>
            </a>
          </h2>
            <p style="margin:0 0 12px;font-size:.875rem;color:var(--color-fg-muted);">
              <time datetime="<?php echo esc_attr(get_the_date('c')); ?>"><?php echo esc_html(get_the_date()); ?></time>
            </p>
            <div style="line-height:1.5;">
              <?php the_excerpt(); ?>
            </div>
            <p style="margin-top:12px;">
              <a href="<?php the_permalink(); ?>" class="btn" style="--btn-bg:var(--color-accent);--btn-fg:#000;padding:8px 14px;font-size:.85rem;border-radius:var(--radius);display:inline-block;font-weight:600;text-decoration:none;">
                <?php echo (pll_current_language() === 'en') ? 'Read more' : 'Leer más'; ?> →
              </a>
            </p>
        </article>
      <?php endwhile; wp_reset_postdata(); ?>
    </div>
    <nav class="pagination" style="margin-top:40px;">
      <?php
        echo paginate_links([
          'total' => $q->max_num_pages,
          'current' => $paged,
          'prev_text' => '«',
          'next_text' => '»'
        ]);
      ?>
    </nav>
  <?php else: ?>
    <p><?php echo (function_exists('pll_current_language') && pll_current_language()==='en') ? 'No posts yet.' : 'No hay entradas todavía.'; ?></p>
  <?php endif; ?>
</main>
<?php get_footer(); ?>
