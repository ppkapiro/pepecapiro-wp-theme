# SELF-HOSTED RUNNER PLAN - Guía Técnica de Setup y Mantenimiento

**Proyecto:** pepecapiro-wp-theme  
**Fecha de creación:** 2025-10-28  
**Propósito:** Runbook completo para implementar y mantener un self-hosted runner de GitHub Actions manteniendo el repositorio privado.

---

## Resumen ejecutivo

**¿Qué es un self-hosted runner?**
Un servidor (VPS, PC local, o WSL) que ejecuta workflows de GitHub Actions en tu propia infraestructura en lugar de usar los runners cloud de GitHub.

**Ventajas:**
- ✅ Cero consumo de minutos de GitHub Actions
- ✅ Repositorio permanece privado
- ✅ Control total sobre entorno (software, versiones, recursos)
- ✅ Artifacts y logs almacenados localmente

**Desventajas:**
- ⚠️ Requiere infraestructura 24/7 (VPS recomendado vs PC)
- ⚠️ Mantenimiento operativo (~1 hora/mes)
- ⚠️ Dependencias deben instalarse manualmente
- ⚠️ Menor concurrencia (1 job por runner sin escalar)

---

## Requisitos previos

### Hardware mínimo

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| **CPU** | 2 vCPU | 4 vCPU |
| **RAM** | 2 GB | 4 GB |
| **Disco** | 20 GB SSD | 40 GB SSD |
| **Ancho de banda** | 10 Mbps | 50+ Mbps |
| **Uptime** | 95% | 99.9% (VPS) |

### Software requerido

| Software | Versión | Propósito |
|----------|---------|-----------|
| **OS** | Ubuntu 22.04 LTS | Sistema operativo base |
| **GitHub Runner** | Latest (auto-update) | Ejecutor de workflows |
| **Node.js** | 20.x LTS | Para Lighthouse CLI, npm scripts |
| **Python** | 3.11+ | Para scripts CI (assert_lh_thresholds.py, PSI) |
| **Chrome/Chromium** | Latest stable | Para Lighthouse audits |
| **Git** | 2.40+ | Checkout de código |
| **Docker** (opcional) | 24.x | Para actions que requieren containers |

---

## Fase 1: Provisión de infraestructura (30 minutos)

### Opción A: VPS Cloud (recomendado para uptime 99.9%)

**Proveedores sugeridos:**
- **Hetzner Cloud:** €4.15/mes (2 vCPU, 4GB RAM, 40GB SSD)
- **DigitalOcean:** $6/mes (Basic Droplet)
- **Linode:** $5/mes (Nanode)
- **Oracle Cloud:** FREE tier (2 vCPU, 1GB RAM, 50GB - con limitaciones)

**Provisión en Hetzner (ejemplo):**
```bash
# 1. Crear cuenta en https://console.hetzner.cloud/
# 2. Crear proyecto "pepecapiro-ci"
# 3. Crear servidor:
#    - Location: Falkenstein (DE) o Ashburn (US)
#    - Image: Ubuntu 22.04
#    - Type: CPX11 (2 vCPU, 2GB RAM) o CPX21 (3 vCPU, 4GB RAM)
#    - SSH Key: Subir tu ~/.ssh/id_rsa.pub
#    - Firewall: Permitir solo SSH (22)
# 4. Copiar IP pública asignada

# Conectar por SSH
ssh root@<IP_VPS>
```

### Opción B: PC/WSL Local (solo si uptime no es crítico)

**Requisitos:**
- PC con Windows 10/11 + WSL2 instalado
- O Linux nativo (Ubuntu 22.04)
- PC encendido 24/7 (o aceptar que workflows fallen cuando esté apagado)

**Setup WSL2 (si aplica):**
```bash
# En PowerShell como Admin
wsl --install -d Ubuntu-22.04

# Dentro de WSL
sudo apt update && sudo apt upgrade -y
```

---

## Fase 2: Hardening inicial del servidor (20 minutos)

### Paso 1: Crear usuario dedicado

```bash
# NO ejecutar runner como root (riesgo de seguridad)
sudo adduser github-runner --disabled-password --gecos ""

# Añadir a grupo sudo (solo si se necesita instalar paquetes durante workflows - NO recomendado)
# sudo usermod -aG sudo github-runner

# Cambiar a usuario
sudo su - github-runner
```

### Paso 2: Configurar firewall (solo VPS)

```bash
# Habilitar UFW (Uncomplicated Firewall)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp  # SSH
sudo ufw enable

# Verificar
sudo ufw status
```

### Paso 3: Hardening SSH (opcional pero recomendado)

```bash
# Editar configuración SSH
sudo nano /etc/ssh/sshd_config

# Cambios recomendados:
# PermitRootLogin no
# PasswordAuthentication no
# PubkeyAuthentication yes

# Reiniciar SSH
sudo systemctl restart sshd
```

### Paso 4: Actualizaciones automáticas

```bash
# Instalar unattended-upgrades
sudo apt install unattended-upgrades -y

# Configurar
sudo dpkg-reconfigure --priority=low unattended-upgrades
# Seleccionar "Yes" para actualizaciones automáticas de seguridad
```

---

## Fase 3: Instalación del GitHub Runner (30 minutos)

### Paso 1: Obtener token de registro

**Desde tu máquina local (con gh CLI configurado):**
```bash
# Generar token de registro (válido por 1 hora)
gh api -X POST /repos/ppkapiro/pepecapiro-wp-theme/actions/runners/registration-token --jq '.token'

# Copiar el token (empieza con "AAAAA...")
```

### Paso 2: Descargar e instalar runner

**En el servidor (como usuario `github-runner`):**
```bash
# Cambiar a home del usuario
cd ~

# Crear directorio para el runner
mkdir actions-runner && cd actions-runner

# Descargar la última versión (Linux x64)
RUNNER_VERSION="2.311.0"  # Verificar última en https://github.com/actions/runner/releases
curl -o actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz -L \
  https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

# Extraer
tar xzf ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

# Verificar integridad (opcional)
echo "$(cat actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz.sha256) actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz" | shasum -a 256 -c
```

### Paso 3: Configurar runner

```bash
# Configurar con el token obtenido en Paso 1
./config.sh --url https://github.com/ppkapiro/pepecapiro-wp-theme \
            --token <TOKEN_AQUI> \
            --name pepecapiro-runner-01 \
            --labels self-hosted,linux,x64,pepecapiro \
            --work _work \
            --unattended

# Output esperado:
# --------------------------------------------------------------------------------
# |        ____ _ _   _   _       _          _        _   _                      |
# |       / ___(_) |_| | | |_   _| |__      / \   ___| |_(_) ___  _ __  ___     |
# |      | |  _| | __| |_| | | | | '_ \    / _ \ / __| __| |/ _ \| '_ \/ __|    |
# |      | |_| | | |_|  _  | |_| | |_) |  / ___ \ (__| |_| | (_) | | | \__ \    |
# |       \____|_|\__|_| |_|\__,_|_.__/  /_/   \_\___|\__|_|\___/|_| |_|___/    |
# |                                                                              |
# |                       Self-hosted runner registration                        |
# |                                                                              |
# --------------------------------------------------------------------------------
# √ Runner successfully added
# √ Runner connection is good
```

**Parámetros explicados:**
- `--url`: URL del repositorio
- `--token`: Token de registro (caduca en 1 hora; solo se usa una vez)
- `--name`: Nombre visible del runner en GitHub UI
- `--labels`: Etiquetas para seleccionar runner en workflows (`runs-on: [self-hosted, pepecapiro]`)
- `--work`: Directorio de trabajo para checkouts (se crea automáticamente)
- `--unattended`: Configuración no interactiva (para scripts)

### Paso 4: Instalar como servicio systemd

```bash
# Instalar servicio (requiere sudo)
sudo ./svc.sh install github-runner

# Iniciar servicio
sudo ./svc.sh start

# Verificar estado
sudo ./svc.sh status

# Output esperado:
# ● actions.runner.ppkapiro-pepecapiro-wp-theme.pepecapiro-runner-01.service - GitHub Actions Runner
#      Loaded: loaded (/etc/systemd/system/actions.runner.ppkapiro-pepecapiro-wp-theme.pepecapiro-runner-01.service; enabled; vendor preset: enabled)
#      Active: active (running) since Mon 2025-10-28 00:00:00 UTC; 5s ago
```

### Paso 5: Habilitar auto-start en boot

```bash
# Ya está habilitado automáticamente por svc.sh install
# Verificar:
sudo systemctl is-enabled actions.runner.ppkapiro-pepecapiro-wp-theme.pepecapiro-runner-01.service

# Output: enabled
```

### Paso 6: Verificar runner en GitHub

**Desde tu máquina local:**
```bash
gh api /repos/ppkapiro/pepecapiro-wp-theme/actions/runners --jq '.runners[] | {name, status, os}'
```

Output esperado:
```json
{
  "name": "pepecapiro-runner-01",
  "status": "online",
  "os": "linux"
}
```

**O en GitHub UI:**
1. Abrir: https://github.com/ppkapiro/pepecapiro-wp-theme/settings/actions/runners
2. Debe aparecer: **pepecapiro-runner-01** con estado **Idle** (verde)

---

## Fase 4: Instalación de dependencias (40 minutos)

### 1. Actualizar sistema base

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git build-essential
```

### 2. Instalar Node.js 20 LTS

```bash
# Añadir repositorio NodeSource
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

# Instalar Node.js y npm
sudo apt install -y nodejs

# Verificar
node --version  # v20.x.x
npm --version   # 10.x.x
```

### 3. Instalar Python 3.11+

```bash
# Ubuntu 22.04 incluye Python 3.10; actualizar a 3.11
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip

# Configurar python3 por defecto
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Verificar
python3 --version  # Python 3.11.x
```

### 4. Instalar Chrome/Chromium (para Lighthouse)

```bash
# Opción A: Chromium (open-source, ligero)
sudo apt install -y chromium-browser

# Opción B: Google Chrome (oficial, más compatible)
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt --fix-broken install -y

# Verificar
chromium-browser --version  # Chromium 120.x.x
# O
google-chrome --version     # Google Chrome 120.x.x
```

### 5. Instalar Lighthouse CLI

```bash
sudo npm install -g lighthouse

# Verificar
lighthouse --version  # 11.x.x

# Test rápido
lighthouse --help
```

### 6. Instalar Python libraries

```bash
# Bibliotecas requeridas por scripts CI
pip3 install --user requests beautifulsoup4 lxml pyyaml

# Verificar
python3 -c "import requests, bs4, lxml, yaml; print('OK')"
# Output: OK
```

### 7. Instalar Docker (opcional - solo si workflows usan containers)

```bash
# Añadir repositorio Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Añadir usuario github-runner al grupo docker (sin sudo)
sudo usermod -aG docker github-runner

# ⚠️ CERRAR SESIÓN Y VOLVER A CONECTAR para aplicar cambio de grupo
exit
sudo su - github-runner

# Verificar
docker --version  # Docker version 24.x.x
docker run hello-world  # Debe descargar y ejecutar contenedor de prueba
```

### 8. Instalar herramientas adicionales (según workflows)

```bash
# jq (para parseo JSON en workflows)
sudo apt install -y jq

# WP-CLI (si workflows gestionan WordPress directamente)
curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
chmod +x wp-cli.phar
sudo mv wp-cli.phar /usr/local/bin/wp

# Verificar
wp --info
```

---

## Fase 5: Migrar workflows a self-hosted (30 minutos)

### Paso 1: Crear branch de trabajo

```bash
# En tu máquina local
cd /home/pepe/work/pepecapiro-wp-theme
git checkout -b feat/self-hosted-runner
```

### Paso 2: Script de migración masiva

```bash
# Reemplazar runs-on en todos los workflows
find .github/workflows -name "*.yml" -type f -exec sed -i 's/runs-on: ubuntu-latest/runs-on: [self-hosted, linux, x64]/g' {} \;

# Verificar cambios
git diff .github/workflows/
```

**Antes:**
```yaml
jobs:
  lighthouse:
    runs-on: ubuntu-latest
```

**Después:**
```yaml
jobs:
  lighthouse:
    runs-on: [self-hosted, linux, x64]
```

### Paso 3: Ajustes específicos por workflow (si aplica)

**Lighthouse.yml - Configurar Chrome path:**
```yaml
- name: Run Lighthouse (mobile)
  env:
    CHROME_PATH: /usr/bin/chromium-browser  # O /usr/bin/google-chrome
  run: |
    lighthouse https://pepecapiro.com \
      --chrome-flags="--headless=new --no-sandbox" \
      ${CHROME_PATH:+--chrome-path="$CHROME_PATH"}
```

**Workflows con Docker - Asegurar que Docker está disponible:**
```yaml
- name: Verificar Docker
  run: docker --version
```

### Paso 4: Commit y push

```bash
git add .github/workflows/
git commit -m "ci: migrate all workflows to self-hosted runner"
git push origin feat/self-hosted-runner
```

### Paso 5: Merge a main (tras testing)

```bash
# Tras verificar que workflows funcionan (ver Fase 6)
git checkout main
git merge feat/self-hosted-runner
git push origin main
```

---

## Fase 6: Testing y validación (30 minutos)

### Paso 1: Test workflow simple

**Crear workflow de prueba:**
```bash
# En tu máquina local
cat > .github/workflows/test-runner.yml << 'EOF'
name: Test Self-Hosted Runner

on:
  workflow_dispatch:

jobs:
  test:
    runs-on: [self-hosted, linux, x64]
    steps:
      - name: Check OS
        run: uname -a
      
      - name: Check Node
        run: node --version
      
      - name: Check Python
        run: python3 --version
      
      - name: Check Chrome
        run: chromium-browser --version || google-chrome --version
      
      - name: Check Lighthouse
        run: lighthouse --version
      
      - name: Echo success
        run: echo "✅ Runner configured correctly!"
EOF

git add .github/workflows/test-runner.yml
git commit -m "ci: add test workflow for self-hosted runner"
git push origin main
```

**Ejecutar test:**
```bash
gh workflow run test-runner.yml

# Monitorear
sleep 5
RUN_ID=$(gh run list --workflow=test-runner.yml --limit=1 --json databaseId --jq '.[0].databaseId')
gh run watch $RUN_ID
```

**Verificar logs en el servidor:**
```bash
# SSH al VPS
ssh github-runner@<IP_VPS>

# Ver logs del runner
sudo journalctl -u actions.runner.ppkapiro-pepecapiro-wp-theme.pepecapiro-runner-01.service -f
```

### Paso 2: Test workflow crítico (Lighthouse)

```bash
# Ejecutar Lighthouse workflow
gh workflow run lighthouse.yml

# Monitorear (puede tardar 5-8 minutos)
sleep 5
LH_RUN=$(gh run list --workflow=lighthouse.yml --limit=1 --json databaseId --jq '.[0].databaseId')
gh run watch $LH_RUN
```

**Si falla, diagnosticar:**
```bash
# Revisar logs del job específico
gh run view $LH_RUN --log | grep -i "error\|fail"

# Errores comunes y soluciones:
# "chromium-browser: command not found" → Instalar Chrome/Chromium
# "ECONNREFUSED" → Firewall bloqueando salida HTTPS (puerto 443)
# "Permission denied" → Usuario github-runner necesita permisos (raro)
```

### Paso 3: Test workflows adicionales

```bash
# Smoke tests
gh workflow run smoke-tests.yml
sleep 3
gh run watch $(gh run list --workflow=smoke-tests.yml --limit=1 --json databaseId --jq '.[0].databaseId')

# SEO Audit
gh workflow run seo_audit.yml
sleep 3
gh run watch $(gh run list --workflow=seo_audit.yml --limit=1 --json databaseId --jq '.[0].databaseId')
```

**Criterio de éxito:**
- [ ] test-runner.yml: ✅ Success
- [ ] lighthouse.yml: ✅ Success (todos los URLs auditados)
- [ ] smoke-tests.yml: ✅ Success
- [ ] seo_audit.yml: ✅ Success

---

## Fase 7: Mantenimiento y monitorización

### Cron jobs para mantenimiento automatizado

**Editar crontab del usuario github-runner:**
```bash
crontab -e
```

**Añadir entradas:**
```cron
# Actualizar runner (verifica versión cada domingo a las 2 AM)
0 2 * * 0 cd /home/github-runner/actions-runner && ./run.sh --check-version >> /home/github-runner/runner-update.log 2>&1

# Limpiar workspace antiguo (archivos > 7 días, cada día a las 3 AM)
0 3 * * * find /home/github-runner/actions-runner/_work/ -type d -mtime +7 -exec rm -rf {} + >> /home/github-runner/cleanup.log 2>&1

# Limpiar logs del runner (archivos > 30 días, cada semana)
0 4 * * 0 find /home/github-runner/actions-runner/_diag/ -type f -mtime +30 -delete

# Monitoreo de disco (alerta si > 80%, cada hora)
0 * * * * df -h /home/github-runner | awk 'NR==2 {if (substr($5,1,length($5)-1) > 80) print "⚠️ Disco al "$5" - Limpiar workspace"}' | logger -t runner-disk-monitor
```

### Script de health check

**Crear script de monitoreo:**
```bash
cat > /home/github-runner/health-check.sh << 'EOF'
#!/bin/bash

# Health check del runner
echo "=== Runner Health Check $(date) ===" >> /home/github-runner/health.log

# 1. Verificar servicio activo
if ! sudo systemctl is-active --quiet actions.runner.*.service; then
    echo "❌ Runner service DOWN - Reiniciando..." >> /home/github-runner/health.log
    sudo systemctl restart actions.runner.*.service
else
    echo "✅ Runner service UP" >> /home/github-runner/health.log
fi

# 2. Verificar espacio en disco
DISK_USAGE=$(df /home/github-runner | awk 'NR==2 {print substr($5,1,length($5)-1)}')
if [ "$DISK_USAGE" -gt 85 ]; then
    echo "⚠️ Disco al ${DISK_USAGE}% - Limpiando workspace..." >> /home/github-runner/health.log
    find /home/github-runner/actions-runner/_work/ -type d -mtime +3 -exec rm -rf {} + 2>/dev/null
fi

# 3. Verificar conectividad a GitHub
if ! curl -s -o /dev/null -w "%{http_code}" https://api.github.com | grep -q "200"; then
    echo "❌ No hay conectividad a GitHub API" >> /home/github-runner/health.log
else
    echo "✅ Conectividad a GitHub OK" >> /home/github-runner/health.log
fi

echo "" >> /home/github-runner/health.log
EOF

chmod +x /home/github-runner/health-check.sh

# Añadir a crontab (cada 15 minutos)
echo "*/15 * * * * /home/github-runner/health-check.sh" >> /tmp/cron_temp
crontab -l >> /tmp/cron_temp
crontab /tmp/cron_temp
rm /tmp/cron_temp
```

### Dashboard de monitoreo (opcional - Prometheus + Grafana)

**Si se requiere monitoreo avanzado:**
```bash
# Instalar node_exporter para métricas del servidor
wget https://github.com/prometheus/node_exporter/releases/download/v1.7.0/node_exporter-1.7.0.linux-amd64.tar.gz
tar xzf node_exporter-1.7.0.linux-amd64.tar.gz
sudo mv node_exporter-1.7.0.linux-amd64/node_exporter /usr/local/bin/
sudo useradd -rs /bin/false node_exporter

# Crear servicio systemd
sudo cat > /etc/systemd/system/node_exporter.service << EOF
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start node_exporter
sudo systemctl enable node_exporter

# Accesible en http://<IP_VPS>:9100/metrics
```

---

## Troubleshooting común

### Problema 1: Runner aparece "Offline" en GitHub

**Diagnóstico:**
```bash
sudo systemctl status actions.runner.*.service

# Si está stopped:
sudo systemctl start actions.runner.*.service

# Ver logs para más contexto
sudo journalctl -u actions.runner.*.service -n 100
```

**Causas comunes:**
- Servicio no iniciado tras reboot
- Token de registro expirado (regenerar con `./config.sh`)
- Firewall bloqueando salida a GitHub (puerto 443)

### Problema 2: Workflow falla con "command not found"

**Ejemplo:** `chromium-browser: command not found`

**Solución:**
```bash
# Verificar PATH del usuario github-runner
sudo su - github-runner
echo $PATH

# Instalar dependencia faltante
sudo apt install chromium-browser

# O añadir al PATH en ~/.bashrc
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
```

### Problema 3: Disco lleno (100%)

**Limpieza de emergencia:**
```bash
# Limpiar todo el workspace (CUIDADO: borra artifacts)
rm -rf /home/github-runner/actions-runner/_work/*

# Limpiar logs antiguos
find /home/github-runner/actions-runner/_diag/ -type f -mtime +7 -delete

# Verificar espacio recuperado
df -h /home/github-runner
```

### Problema 4: Runner no ejecuta workflows (queda en "Queued")

**Diagnóstico:**
```bash
# Verificar que el runner está "Idle" en GitHub
gh api /repos/ppkapiro/pepecapiro-wp-theme/actions/runners --jq '.runners[] | {name, status, busy}'

# Si busy: false y status: online → OK
# Si busy: true → Hay un job ejecutándose (esperar)
# Si status: offline → Ver Problema 1
```

---

## Plan de rollback (volver a GitHub-hosted runners)

### Paso 1: Revertir workflows

```bash
cd /home/pepe/work/pepecapiro-wp-theme
git checkout main

# Revertir commit de migración
git revert <commit_hash_self_hosted>

# O rehacer cambio manualmente
find .github/workflows -name "*.yml" -exec sed -i 's/runs-on: \[self-hosted, linux, x64\]/runs-on: ubuntu-latest/g' {} \;

git add .github/workflows/
git commit -m "ci: revert to GitHub-hosted runners"
git push origin main
```

### Paso 2: Desconectar runner

```bash
# SSH al VPS
ssh github-runner@<IP_VPS>

# Detener servicio
cd /home/github-runner/actions-runner
sudo ./svc.sh stop
sudo ./svc.sh uninstall

# Remover runner de GitHub
./config.sh remove --token <REMOVAL_TOKEN>
```

**Obtener removal token:**
```bash
# Desde tu máquina local
gh api -X POST /repos/ppkapiro/pepecapiro-wp-theme/actions/runners/remove-token --jq '.token'
```

### Paso 3: Limpiar en GitHub UI

1. Abrir: https://github.com/ppkapiro/pepecapiro-wp-theme/settings/actions/runners
2. Click en **pepecapiro-runner-01**
3. Click **Remove runner**

### Paso 4: Destruir infraestructura (si VPS)

```bash
# Si usaste Hetzner/DigitalOcean/etc:
# 1. Ir al panel de control
# 2. Seleccionar servidor
# 3. Delete/Destroy
# 4. Confirmar (se detiene billing)
```

---

## Checklist final de éxito

**Tras completar todas las fases:**
- [ ] ✅ Runner aparece "Idle" en GitHub Settings > Actions > Runners
- [ ] ✅ test-runner.yml ejecuta correctamente
- [ ] ✅ lighthouse.yml genera reportes completos
- [ ] ✅ Workflows críticos (smoke-tests, seo_audit) funcionan
- [ ] ✅ Servicio systemd habilitado (auto-start en boot)
- [ ] ✅ Cron jobs configurados (actualización, limpieza, monitoring)
- [ ] ✅ Health check ejecuta cada 15 minutos
- [ ] ✅ Disco tiene >20% libre
- [ ] ✅ Conectividad a GitHub API confirmada

**Estado:** 🎉 **SELF-HOSTED RUNNER OPERATIVO**

---

## Costos estimados

| Concepto | One-time | Recurrente (mensual) |
|----------|----------|---------------------|
| **VPS Hetzner CPX11** | €0 (prorrateado) | €4.15 |
| **Setup time (2.5h @ $0)** | Gratis (self-service) | - |
| **Mantenimiento (1h/mes @ $0)** | - | Gratis (self-service) |
| **TOTAL** | €0 | €4.15/mes (~$4.50 USD) |

**Costo anual:** €49.80 (~$54 USD)  
**vs GitHub Actions (repo privado):** $4/usuario/mes + minutos = $48+/año mínimo

---

**Última actualización:** 2025-10-28  
**Responsable de mantenimiento:** [Asignar persona]  
**Próxima revisión:** Mensual (actualizar versiones de dependencias)
