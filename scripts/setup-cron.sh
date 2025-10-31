#!/bin/bash

# Script de configuración automática de cron para health checks
# Autor: Sistema de Monitoreo
# Fecha: $(date +%Y-%m-%d)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRON_FILE="/tmp/health-checks-crontab.tmp"

echo "=== CONFIGURACIÓN AUTOMÁTICA DE CRON PARA HEALTH CHECKS ==="
echo "Directorio de scripts: $SCRIPT_DIR"
echo ""

# Verificar si el directorio existe
if [ ! -d "$SCRIPT_DIR" ]; then
    echo "ERROR: El directorio $SCRIPT_DIR no existe"
    exit 1
fi

# Crear archivo de crontab temporal
cat > "$CRON_FILE" << 'EOF'
# Health Checks Automáticos - Configuración generada automáticamente
# NO EDITAR MANUALMENTE - Usar setup-cron.sh para modificar

# Configuración de variables de entorno para los scripts
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Health Check General - Cada 5 minutos
*/5 * * * * SCRIPT_DIR=SCRIPT_DIR_HERE /bin/bash SCRIPT_DIR_HERE/health-check.sh >> /var/log/health-check-cron.log 2>&1

# Verificación de Bases de Datos - Cada 15 minutos
*/15 * * * * SCRIPT_DIR=SCRIPT_DIR_HERE /bin/bash SCRIPT_DIR_HERE/check-db-connections.sh >> /var/log/db-check-cron.log 2>&1

# Verificación de RabbitMQ - Cada 10 minutos
*/10 * * * * SCRIPT_DIR=SCRIPT_DIR_HERE /bin/bash SCRIPT_DIR_HERE/check-rabbitmq.sh >> /var/log/rabbitmq-check-cron.log 2>&1

# Verificación de Redis - Cada 10 minutos
*/10 * * * * SCRIPT_DIR=SCRIPT_DIR_HERE /bin/bash SCRIPT_DIR_HERE/check-redis.sh >> /var/log/redis-check-cron.log 2>&1

# Reporte Completo - Cada hora
0 * * * * SCRIPT_DIR=SCRIPT_DIR_HERE /bin/bash SCRIPT_DIR_HERE/generate-health-report.sh >> /var/log/health-report-cron.log 2>&1

# Reporte Diario Completo - A las 6:00 AM
0 6 * * * SCRIPT_DIR=SCRIPT_DIR_HERE /bin/bash SCRIPT_DIR_HERE/generate-health-report.sh >> /var/log/daily-health-report.log 2>&1

# Limpieza de logs antiguos - Domingos a las 2:00 AM
0 2 * * 0 find SCRIPT_DIR_HERE/logs/ -name "*.log" -mtime +30 -delete
0 2 * * 0 find SCRIPT_DIR_HERE/reports/ -name "*.html" -mtime +30 -delete
0 2 * * 0 find SCRIPT_DIR_HERE/reports/ -name "*.json" -mtime +30 -delete

EOF

# Reemplazar placeholder con directorio real
sed -i "s|SCRIPT_DIR_HERE|$SCRIPT_DIR|g" "$CRON_FILE"

echo "Configuración de cron generada:"
echo "================================"
cat "$CRON_FILE"
echo "================================"
echo ""

# Preguntar si instalar
read -p "¿Deseas instalar esta configuración de cron? (y/n): " install_cron

if [ "$install_cron" = "y" ] || [ "$install_cron" = "Y" ]; then
    echo ""
    echo "Instalando configuración de cron..."
    
    # Crear backup del crontab actual
    if crontab -l > /tmp/crontab-backup-$(date +%Y%m%d-%H%M%S).txt 2>/dev/null; then
        echo "Backup del crontab actual creado"
    fi
    
    # Instalar nuevo crontab
    if crontab "$CRON_FILE"; then
        echo "✓ Configuración de cron instalada exitosamente"
        
        # Crear directorios de log si no existen
        sudo mkdir -p /var/log
        sudo touch /var/log/health-check-cron.log
        sudo touch /var/log/db-check-cron.log
        sudo touch /var/log/rabbitmq-check-cron.log
        sudo touch /var/log/redis-check-cron.log
        sudo touch /var/log/health-report-cron.log
        sudo touch /var/log/daily-health-report.log
        
        # Configurar rotación de logs
        if [ -d "/etc/logrotate.d" ]; then
            cat > /tmp/health-checks-logrotate << 'EOF'
/var/log/health-check-cron.log
/var/log/db-check-cron.log
/var/log/rabbitmq-check-cron.log
/var/log/redis-check-cron.log
/var/log/health-report-cron.log
/var/log/daily-health-report.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 root root
}
EOF
            sudo mv /tmp/health-checks-logrotate /etc/logrotate.d/health-checks
            echo "✓ Configuración de rotación de logs creada"
        fi
        
        echo ""
        echo "Instalación completada. Los health checks se ejecutarán automáticamente:"
        echo "- Health check general: cada 5 minutos"
        echo "- Bases de datos: cada 15 minutos"
        echo "- RabbitMQ y Redis: cada 10 minutos"
        echo "- Reporte completo: cada hora"
        echo "- Reporte diario: diariamente a las 6:00 AM"
        echo ""
        echo "Logs disponibles en:"
        echo "- /var/log/health-check-cron.log"
        echo "- /var/log/db-check-cron.log"
        echo "- /var/log/rabbitmq-check-cron.log"
        echo "- /var/log/redis-check-cron.log"
        echo "- /var/log/health-report-cron.log"
        echo "- /var/log/daily-health-report.log"
        echo ""
        echo "Reportes en: $SCRIPT_DIR/reports/"
        
    else
        echo "ERROR: No se pudo instalar el crontab"
        exit 1
    fi
else
    echo ""
    echo "Instalación cancelada."
    echo "Para instalar manualmente, ejecuta:"
    echo "crontab $CRON_FILE"
fi

# Limpiar archivo temporal
rm -f "$CRON_FILE"

echo ""
echo "Configuración completada."
