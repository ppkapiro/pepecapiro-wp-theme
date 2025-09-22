<form role="search" method="get" action="<?php echo esc_url(home_url('/')); ?>" style="display:flex;gap:8px;">
  <label class="screen-reader-text" for="s">Buscar:</label>
  <input type="search" id="s" name="s" value="<?php echo get_search_query(); ?>" placeholder="Buscar…" style="flex:1;padding:10px;border:1px solid #ccc;border-radius:8px;">
  <button type="submit" class="btn btn-primary">Buscar</button>
</form>
