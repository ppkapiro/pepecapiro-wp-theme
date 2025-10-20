# Dashboard de Estado — Referencia Técnica

## Archivo: `public/status.json`

Este archivo contiene el estado actualizado del sistema WordPress y es generado automáticamente cada 6 horas por el workflow `health-dashboard.yml`.

### Estructura JSON

```json
{
  "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
  "auth": "OK | KO | SKIP",
  "home": "OK | KO | SKIP",
  "menus": "OK | KO | SKIP",
  "media": "OK | KO | SKIP",
  "settings": "OK | DRIFT | KO | SKIP",
  "polylang": "Yes | No",
  "issues": 0
}
```

### Campos

- **timestamp**: Fecha/hora UTC de la última generación.
- **auth**: Estado de autenticación con la API de WordPress.
  - `OK`: credenciales válidas y acceso correcto.
  - `KO`: fallo de autenticación o secrets faltantes.
  - `SKIP`: no se ejecutó la verificación.
- **home**: Estado de la configuración de la página de inicio y fronts ES/EN.
  - `OK`: show_on_front='page', página de inicio configurada, fronts devuelven HTTP 200.
  - `KO`: configuración incorrecta o fronts inaccesibles.
  - `SKIP`: no verificado (auth KO).
- **menus**: Estado de los menús bilingües principales.
  - `OK`: menús existen y cumplen con el manifiesto.
  - `KO`: discrepancia con el manifiesto o menús faltantes.
  - `SKIP`: no verificado.
- **media**: Estado de los medios subidos.
  - `OK`: archivos del manifiesto presentes y asignados.
  - `KO`: archivos faltantes o asignaciones incorrectas.
  - `SKIP`: no verificado.
- **settings**: Estado de ajustes básicos (timezone, permalinks, start_of_week).
  - `OK`: todos los ajustes coinciden con el esperado.
  - `DRIFT`: ajustes divergen del esperado pero el sitio funciona.
  - `KO`: error al obtener ajustes.
  - `SKIP`: no verificado.
- **polylang**: Indica si el sitio tiene Polylang activo.
  - `Yes`: Polylang detectado.
  - `No`: sin Polylang o no detectado.
- **issues**: Número de issues abiertos con la etiqueta `monitoring`.

### Uso

- **Monitoreo externo**: Scripts o dashboards pueden hacer GET a `https://<repo-pages-url>/status.json` para comprobar el estado del sitio sin autenticación.
- **Alertas**: Si `auth`, `home`, `menus`, `media` o `settings` son `KO`, se recomienda revisar logs y ejecutar `run-repair.yml`.
- **Auditoría**: Compara timestamps sucesivos para detectar cambios de estado.

### Actualización

El archivo se actualiza automáticamente:
- Cada 6 horas (cron `0 */6 * * *`).
- Manualmente ejecutando `health-dashboard.yml`.

Generado por: `.github/workflows/health-dashboard.yml`
