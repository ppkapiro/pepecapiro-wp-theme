# 🟡 SMTP - Error de Autenticación (Password)

**Fecha:** 2025-10-28 15:36 UTC  
**Diagnóstico:** Run 18880363918  
**Estado:** Configuración correcta, pero password incorrecto

---

## ✅ Configuración AHORA CORRECTA

```json
{
  "mail": {
    "from_email": "contact@pepecapiro.com",  ✅
    "from_name": "Pepe Capiro"  ✅
  },
  "smtp": {
    "host": "smtp.hostinger.com",  ✅
    "encryption": "ssl",  ✅
    "port": 465,  ✅
    "auth": true,  ✅
    "user": "contact@pepecapiro.com",  ✅
    "pass": "[80 caracteres - OCULTO]"  ❓
  }
}
```

**Todos los campos correctos EXCEPTO password.**

---

## ❌ Error Actual

```
Resultado wp_mail(): FALSE (fallo)
PHPMailer ErrorInfo: SMTP Error: Could not authenticate.
```

**Causa:** Una de estas dos:

1. **El email `contact@pepecapiro.com` NO existe en Hostinger**
2. **El password ingresado en WP Mail SMTP es incorrecto**

---

## 🔍 Verificación Requerida

### PASO 1: Verificar si email existe en Hostinger

1. Login en: **Hostinger hPanel**
2. Ir a: **Email** > **Email Accounts**
3. Buscar: **contact@pepecapiro.com**

**Resultado A:** Email EXISTE
- ✅ Anotar el password actual (o hacer reset)
- ✅ Ir a PASO 2

**Resultado B:** Email NO EXISTE
- ✅ Click **Create Email Account**
- ✅ Email: `contact@pepecapiro.com`
- ✅ Password: Crear uno fuerte (anotar)
- ✅ Ir a PASO 2

---

### PASO 2: Actualizar password en WordPress

1. Login: https://pepecapiro.com/wp-admin
2. Navegar: **WP Mail SMTP > Settings**
3. Scroll a: **SMTP Password**
4. **Ingresar el password CORRECTO** del email (del PASO 1)
5. Click: **Save Settings**
6. Tab: **Email Test**
7. Enviar test a tu email personal
8. Verificar recepción

---

## 🧪 Test Manual Alternativo

Si prefieres probar directamente el formulario de contacto (sin workflow):

1. **Formulario ES:** https://pepecapiro.com/contacto/
2. **Formulario EN:** https://pepecapiro.com/en/contact/
3. Llenar y enviar mensaje
4. Verificar si llega email a tu inbox

(WPForms enviará email usando la configuración SMTP de WP Mail SMTP)

---

## 📊 Historial de Correcciones

| Intento | Error | Corrección |
|---------|-------|------------|
| 1 | Port `456`, encryption `none` | ✅ Corregido: port `465`, encryption `ssl` |
| 2 | From Email `contac@` (typo) | ✅ Corregido: `contact@` |
| 3 | User `contact@ppcapiro.com` (dominio sin e) | ✅ Corregido: `contact@pepecapiro.com` |
| 4 | **Password incorrecto** | ⏳ PENDIENTE verificación |

---

## ✅ Próximos Pasos

**Una vez verificado password correcto:**

```bash
# Test via workflow
cd /home/pepe/work/pepecapiro-wp-theme
gh workflow run smtp-config.yml --field action=test
```

**O probar formulario directamente:**
- https://pepecapiro.com/contacto/ (ES)
- https://pepecapiro.com/en/contact/ (EN)

---

**Estado:** 🟡 Casi listo - Solo falta verificar password del email en Hostinger
