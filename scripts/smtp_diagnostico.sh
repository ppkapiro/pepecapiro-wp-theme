#!/usr/bin/env bash
# Diagnóstico SMTP - Verificar configuración y errores
set -euo pipefail

SITE_ROOT="/home/u525829715/domains/pepecapiro.com/public_html"

echo "=== Diagnóstico SMTP pepecapiro.com ==="
echo ""

echo "1. Estado del plugin WP Mail SMTP:"
wp --path="$SITE_ROOT" plugin list | grep -i smtp || echo "No hay plugins SMTP instalados"
echo ""

echo "2. Verificar que plugin está activo:"
if wp --path="$SITE_ROOT" plugin is-active wp-mail-smtp; then
    echo "✅ Plugin WP Mail SMTP está ACTIVO"
    wp --path="$SITE_ROOT" plugin get wp-mail-smtp --fields=name,status,version
else
    echo "❌ Plugin WP Mail SMTP NO está activo"
    exit 1
fi
echo ""

echo "3. Verificar configuración SMTP (wp_mail_smtp options):"
wp --path="$SITE_ROOT" option get wp_mail_smtp 2>/dev/null || echo "⚠️ Opción wp_mail_smtp no existe (plugin no configurado)"
echo ""

echo "4. Test simple wp_mail() sin exit on fail:"
wp --path="$SITE_ROOT" eval '
$result = wp_mail(
    "test@example.com", 
    "[TEST] pepecapiro.com SMTP", 
    "Email de prueba desde WP-CLI\n\nFecha: " . date("Y-m-d H:i:s")
);
if ($result) {
    echo "✅ wp_mail() retornó TRUE (email en cola)\n";
} else {
    echo "❌ wp_mail() retornó FALSE\n";
    // Verificar si hay error global
    global $phpmailer;
    if (isset($phpmailer) && !empty($phpmailer->ErrorInfo)) {
        echo "Error PHPMailer: " . $phpmailer->ErrorInfo . "\n";
    }
}
' || echo "⚠️ wp eval falló"
echo ""

echo "5. Verificar logs de error recientes:"
if [ -f "$SITE_ROOT/wp-content/debug.log" ]; then
    echo "Últimas 20 líneas de debug.log:"
    tail -20 "$SITE_ROOT/wp-content/debug.log"
else
    echo "⚠️ No existe debug.log (WP_DEBUG no activado)"
fi
echo ""

echo "6. Verificar permisos directorio wp-content:"
ls -ld "$SITE_ROOT/wp-content" | awk '{print "Permisos:", $1, "Owner:", $3":"$4}'
echo ""

echo "=== Fin diagnóstico ==="
