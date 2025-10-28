# Configuración Manual de WP Mail SMTP

**Plugin:** WP Mail SMTP by WPForms (v4.6.0)  
**Estado:** ✅ Instalado y activado (2025-10-28)  
**Sitio:** pepecapiro.com

---

## ⚠️ Acción Manual Requerida

La configuración de SMTP **requiere credenciales de email** que NO deben almacenarse en código o GitHub Secrets. La configuración se hace directamente en el admin de WordPress y se guarda en la base de datos.

---

## Pasos de Configuración

### 1. Acceder al plugin

1. Login en: https://pepecapiro.com/wp-admin
2. Ir a: **WP Mail SMTP > Settings** (en sidebar izquierdo)

---

### 2. Configurar Mailer

**Opción recomendada:** `Other SMTP`

- **From Email:** `noreply@pepecapiro.com` (o email válido de Hostinger)
  - **Importante:** Debe ser email del dominio pepecapiro.com
  - Verificar que email existe en Hostinger Email Accounts
  
- **From Name:** `Pepe Capiro`
  
- **Return Path:** ✅ **Checked** (Force From Email)

---

### 3. Configurar SMTP (Hostinger)

**SMTP Host:** `smtp.hostinger.com`

**Encryption:**
- Opción 1 (recomendada): `SSL`
- Opción 2: `TLS`

**SMTP Port:**
- Si SSL: `465`
- Si TLS: `587`

**Auto TLS:** ✅ **On** (activar)

**Authentication:** ✅ **On** (activar)

**SMTP Username:** Email completo
- Ejemplo: `noreply@pepecapiro.com`
- **Importante:** Usar el mismo email que "From Email"

**SMTP Password:** Password del email
- Obtener de: Hostinger hPanel > Email Accounts > pepecapiro.com > Manage
- Si no conoces password: Reset password en hPanel

---

### 4. Configuración Avanzada (Opcional)

**Backup Connection:**
- Si disponible: Configurar PHP Mail como backup
- Útil si SMTP falla temporalmente

**Email Log:**
- ✅ **Enable** (recomendado)
- Permite ver historial de emails enviados
- Útil para debugging de formularios

---

## 5. Guardar y Probar

### Guardar configuración

1. Click en **Save Settings** (botón azul abajo)
2. Verificar que aparece mensaje: "Settings were successfully saved."

### Enviar email de prueba

1. Ir a: **WP Mail SMTP > Email Test** (tab superior)
2. **Send To:** Ingresar tu email personal (para verificar recepción)
3. Click en **Send Email**
4. Verificar resultado:
   - ✅ **Success:** "Test email was sent successfully!"
   - ❌ **Error:** Revisar mensaje de error

### Verificar recepción

1. Revisar bandeja de entrada del email ingresado
2. Si no aparece: Revisar carpeta SPAM
3. Email de prueba debe tener:
   - From: noreply@pepecapiro.com (o email configurado)
   - Subject: "WP Mail SMTP: Test Email"
   - Body: Mensaje simple de prueba

---

## 6. Probar Formulario de Contacto

### Desde sitio público

1. Ir a: https://pepecapiro.com/contacto/ (o /en/contact/)
2. Llenar formulario:
   - Nombre: Test
   - Email: tu_email@example.com
   - Mensaje: "Prueba de SMTP configurado"
3. Enviar formulario
4. Verificar que aparece mensaje de éxito (WPForms)

### Verificar recepción

- Email debe llegar a: (verificar en WPForms > Settings > Notifications)
- Default: Admin email de WordPress
- Si configuraste email personalizado: Verificar ese inbox

---

## 7. Validación via Workflow (Post-Configuración)

Una vez configurado manualmente en WP admin, puedes validar con workflow:

```bash
cd /home/pepe/work/pepecapiro-wp-theme
gh workflow run smtp-config.yml --field action=test
```

Este comando:
- Ejecuta `wp_mail()` vía WP-CLI
- Envía email de prueba a `test@example.com` (cambiar en workflow si necesario)
- Verifica que SMTP está funcionando desde línea de comandos

**Nota:** El email de prueba del workflow es diferente al test manual - ambos deben funcionar.

---

## Troubleshooting

### Error: "Could not authenticate"

**Causa:** Username o password incorrectos

**Solución:**
1. Verificar que SMTP Username es el email completo (con @pepecapiro.com)
2. Reset password del email en Hostinger hPanel
3. Re-ingresar password en WP Mail SMTP settings
4. Guardar y probar nuevamente

---

### Error: "Could not connect to SMTP host"

**Causa:** Host, puerto o encryption incorrectos

**Solución:**
1. Verificar host: `smtp.hostinger.com` (sin http://)
2. Verificar puerto: 465 (SSL) o 587 (TLS)
3. Verificar encryption coincide con puerto (SSL=465, TLS=587)
4. Si persiste: Cambiar de SSL a TLS (o viceversa)

---

### Error: "From address is not allowed"

**Causa:** Email "From" no coincide con cuenta SMTP

**Solución:**
1. Asegurar que "From Email" = "SMTP Username"
2. Ambos deben usar mismo email (ej: noreply@pepecapiro.com)
3. Email debe existir en Hostinger Email Accounts

---

### Emails no llegan (sin error)

**Causas posibles:**
1. Email bloqueado por SPAM filter del destinatario
2. SPF/DKIM records no configurados en DNS

**Solución:**
1. Revisar carpeta SPAM
2. Enviar a otro email (Gmail, Outlook) para comparar
3. Verificar SPF record en Hostinger DNS:
   - Ir a: hPanel > DNS/Name Servers > pepecapiro.com
   - Buscar record TXT con `v=spf1`
   - Debe incluir: `include:hostinger.com` o similar
4. Si no existe SPF: Agregar record TXT:
   ```
   v=spf1 include:smtp.hostinger.com ~all
   ```

---

## Credenciales de Referencia

**Host SMTP Hostinger:**
- Incoming (IMAP): `imap.hostinger.com:993` (SSL)
- Outgoing (SMTP): `smtp.hostinger.com:465` (SSL) o `:587` (TLS)

**Documentación oficial:**
- Hostinger: https://support.hostinger.com/en/articles/1583229-how-to-configure-smtp-settings
- WP Mail SMTP: https://wpmailsmtp.com/docs/

---

## Checklist Post-Configuración

- [ ] SMTP configurado en WP Mail SMTP settings
- [ ] Email de prueba enviado desde WP admin (tab Email Test)
- [ ] Email de prueba recibido correctamente
- [ ] Formulario de contacto ES enviado y recibido
- [ ] Formulario de contacto EN enviado y recibido
- [ ] Email Log habilitado (para debugging futuro)
- [ ] SPF record verificado en DNS (opcional pero recomendado)
- [ ] Workflow test ejecutado: `gh workflow run smtp-config.yml --field action=test`

---

## Próximos Pasos

Una vez completada configuración y checklist:

1. Actualizar `docs/DOCUMENTO_DE_TRABAJO_CONTINUO_Pepecapiro.md`:
   - Marcar Fase 5 (SMTP) como completada
   - Agregar entrada al historial con fecha de configuración
   
2. Generar `reports/smtp_estado.md`:
   - Resumen de configuración (sin credentials)
   - Resultados de tests (manual + workflow)
   - Checklist completado

3. Proceder a Fase 6 (Cierre v0.3.0):
   - CIERRE_v0_3_0.md
   - public/status.json
   - FINAL_DEPLOY_READY.flag

---

**Fecha de documento:** 2025-10-28  
**Autor:** Copilot (agente autónomo)  
**Requiere acción manual:** ✅ SÍ - configuración de credenciales SMTP en WP admin
