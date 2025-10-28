# 🔴 ERROR SMTP - Configuración Incorrecta Detectada

**Fecha:** 2025-10-28  
**Diagnóstico:** Run 18879948146 (smtp-diagnostico.yml)

---

## Problemas Detectados

### ❌ **Puerto incorrecto**
- **Actual:** `456`
- **Correcto:** `465` (SSL) o `587` (TLS)

### ❌ **Encryption desactivado**
- **Actual:** `"encryption":"none"`
- **Correcto:** `"encryption":"ssl"` (puerto 465) o `"encryption":"tls"` (puerto 587)

### ⚠️ **Email usuario dudoso**
- **Actual:** `"user":"contact@ppcapiro.com"`
- **Verificar:** ¿Existe este email en Hostinger? El dominio es `ppcapiro.com` (sin `e` en pepe)
- **Recomendado:** Usar email del dominio `pepecapiro.com` (con `e`)

### ⚠️ **From Email**
- **Actual:** `"from_email":"musicmanagercuba@gmail.com"`
- **Problema:** Email de Gmail no coincide con SMTP Hostinger
- **Recomendado:** Usar `noreply@pepecapiro.com` o `contact@pepecapiro.com`

---

## Resultado Test

```
Resultado wp_mail(): FALSE (fallo)
PHPMailer ErrorInfo: SMTP Error: Could not connect to SMTP host.
```

**Causa:** Puerto 456 no existe (typo), y encryption "none" sin SSL/TLS impide conexión.

---

## Corrección Requerida (URGENTE)

**Login:** https://pepecapiro.com/wp-admin  
**Navegar:** WP Mail SMTP > Settings

### Configuración CORRECTA:

1. **Mailer:** Other SMTP ✅ (ya está)

2. **From Email:** 
   - Cambiar de: `musicmanagercuba@gmail.com`
   - A: `noreply@pepecapiro.com` o `contact@pepecapiro.com`
   - ✅ **Force From Email** (activado correctamente)

3. **From Name:** `Pepe Capiro` ✅ (ya está)

4. **SMTP Host:** `smtp.hostinger.com` ✅ (ya está)

5. **Encryption:** 
   - Cambiar de: `None`
   - A: **`SSL`** (recomendado)

6. **SMTP Port:**
   - Cambiar de: `456` ❌
   - A: **`465`** (si usas SSL)
   - O: `587` (si usas TLS)

7. **Auto TLS:** ✅ Activar (ON)

8. **Authentication:** ✅ Activar (ON) (ya está)

9. **SMTP Username:**
   - Verificar email: ¿`contact@ppcapiro.com` existe?
   - Si NO existe: Cambiar a email válido de Hostinger
   - Debe coincidir con "From Email"

10. **SMTP Password:**
    - Verificar que es el password correcto del email
    - Si cambias username, actualizar password también

---

## Checklist Re-Configuración

- [ ] From Email cambiado a email de pepecapiro.com
- [ ] Encryption cambiado a **SSL**
- [ ] Port cambiado a **465**
- [ ] Username verificado (email existe en Hostinger)
- [ ] Password verificado (correcto para el email)
- [ ] **Save Settings** clickeado
- [ ] Email de prueba enviado desde tab "Email Test"
- [ ] Email de prueba recibido en inbox

---

## Próximo Paso

**Después de re-configurar:**

```bash
# Test via workflow
cd /home/pepe/work/pepecapiro-wp-theme
gh workflow run smtp-config.yml --field action=test
```

O **probar formulario de contacto directamente:**
- https://pepecapiro.com/contacto/ (ES)
- https://pepecapiro.com/en/contact/ (EN)

---

## Configuración Actual (JSON)

```json
{
  "mail": {
    "from_email": "musicmanagercuba@gmail.com",
    "from_name": "Pepe Capiro",
    "mailer": "smtp",
    "return_path": false,
    "from_email_force": true,
    "from_name_force": false
  },
  "smtp": {
    "autotls": true,
    "auth": true,
    "host": "smtp.hostinger.com",
    "encryption": "none",
    "port": 456,
    "user": "contact@ppcapiro.com",
    "pass": "[OCULTO - 64 caracteres]"
  }
}
```

**Errores críticos:**
- ❌ `"port": 456` → debe ser `465`
- ❌ `"encryption": "none"` → debe ser `"ssl"`
- ⚠️ `"from_email": "musicmanagercuba@gmail.com"` → debe ser email de pepecapiro.com
- ⚠️ `"user": "contact@ppcapiro.com"` → verificar dominio correcto

---

**Estado:** ❌ SMTP NO FUNCIONAL (requiere re-configuración inmediata)
