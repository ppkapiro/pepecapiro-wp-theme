# Flags de auto-disparo (GitHub Actions)

Estos archivos sirven como interruptores sencillos para lanzar workflows sin usar la UI de Actions.
No contienen información sensible; basta con modificar su contenido y hacer push a `main`.

Archivos:
- `.github/auto/publish_test_post.flag`: dispara "Publish Test Post" (crea ES/EN en estado `private`).
- `.github/auto/publish_prod.flag`: dispara "Publish Prod Post" (crea ES/EN en `publish`, enlaza y asigna categorías si existen).

Uso:
1. Edita el archivo correspondiente y añade una línea con una marca temporal (p. ej., `$(date -u +%FT%TZ)`).
2. Haz commit y push a la rama `main`.
3. Verifica el Job Summary del workflow para ver Auth, IDs, links, vínculo y categorías.

Notas:
- No añadas secretos ni credenciales a estos archivos.
- Los workflows también se pueden ejecutar manualmente con "Run workflow" desde la UI.
- Si falta algún secret requerido, el job falla antes de publicar y lo verás en el resumen.
