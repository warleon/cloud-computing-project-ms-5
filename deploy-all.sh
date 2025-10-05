#!/bin/bash
# ============================================
# Script Maestro de Despliegue del DataLake
# ============================================
# Este script levanta todos los servicios en el orden correcto
# Uso: ./deploy-all.sh [start|stop|restart|status|logs]
# ============================================

set -e  # Salir si hay error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_color() {
    echo -e "${2}${1}${NC}"
}

# Función para mostrar uso
show_usage() {
    print_color "Uso: $0 [comando]" "$BLUE"
    echo ""
    echo "Comandos disponibles:"
    echo "  start     - Levantar todos los servicios"
    echo "  stop      - Detener todos los servicios"
    echo "  restart   - Reiniciar todos los servicios"
    echo "  status    - Ver estado de todos los contenedores"
    echo "  logs      - Ver logs de todos los servicios"
    echo "  rebuild   - Reconstruir y levantar todos los servicios"
    echo ""
}

# Función para levantar servicios
start_services() {
    print_color "🚀 Iniciando DataLake completo..." "$GREEN"
    echo ""
    
    # 1. Bases de datos primero (tienen que estar listas para los ingesters)
    print_color "📊 [1/3] Levantando bases de datos..." "$BLUE"
    cd ms-databases
    docker-compose up -d
    cd ..
    
    print_color "⏳ Esperando 15 segundos para que las bases de datos inicialicen..." "$YELLOW"
    sleep 15
    
    # 2. Ingesters (necesitan las bases de datos activas)
    print_color "📥 [2/3] Levantando ingesters..." "$BLUE"
    cd datalake-ingester
    docker-compose up -d
    cd ..
    
    # 3. API REST (puede levantarse independientemente)
    print_color "🌐 [3/3] Levantando API REST..." "$BLUE"
    cd api-consultas
    docker-compose up -d
    cd ..
    
    echo ""
    print_color "✅ Todos los servicios iniciados correctamente!" "$GREEN"
    echo ""
    print_color "Ver estado: $0 status" "$BLUE"
    print_color "Ver logs: $0 logs" "$BLUE"
}

# Función para detener servicios
stop_services() {
    print_color "🛑 Deteniendo todos los servicios..." "$RED"
    echo ""
    
    # Detener en orden inverso
    print_color "[1/3] Deteniendo API REST..." "$YELLOW"
    cd api-consultas && docker-compose down && cd ..
    
    print_color "[2/3] Deteniendo ingesters..." "$YELLOW"
    cd datalake-ingester && docker-compose down && cd ..
    
    print_color "[3/3] Deteniendo bases de datos..." "$YELLOW"
    cd ms-databases && docker-compose down && cd ..
    
    echo ""
    print_color "✅ Todos los servicios detenidos!" "$GREEN"
}

# Función para reiniciar servicios
restart_services() {
    print_color "🔄 Reiniciando todos los servicios..." "$YELLOW"
    stop_services
    echo ""
    sleep 2
    start_services
}

# Función para ver estado
show_status() {
    print_color "📊 Estado de todos los contenedores:" "$BLUE"
    echo ""
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "mysql-test-db|postgres-test-db|mongo-test-db|ingesta0|api-consultas"
    echo ""
    
    # Contar contenedores corriendo
    RUNNING=$(docker ps | grep -E "mysql-test-db|postgres-test-db|mongo-test-db|ingesta0|api-consultas" | wc -l)
    print_color "Total de contenedores corriendo: $RUNNING/7" "$GREEN"
}

# Función para ver logs
show_logs() {
    print_color "📋 Logs de todos los servicios (últimas 50 líneas):" "$BLUE"
    echo ""
    
    print_color "=== BASES DE DATOS ===" "$YELLOW"
    docker logs --tail 10 mysql-test-db 2>&1 | head -n 10 || true
    docker logs --tail 10 postgres-test-db 2>&1 | head -n 10 || true
    docker logs --tail 10 mongo-test-db 2>&1 | head -n 10 || true
    
    print_color "=== INGESTERS ===" "$YELLOW"
    docker logs --tail 10 ingesta01-mysql 2>&1 | head -n 10 || true
    docker logs --tail 10 ingesta02-postgresql 2>&1 | head -n 10 || true
    docker logs --tail 10 ingesta03-mongodb 2>&1 | head -n 10 || true
    
    print_color "=== API REST ===" "$YELLOW"
    docker logs --tail 10 api-consultas-datalake 2>&1 | head -n 10 || true
    
    echo ""
    print_color "Para ver logs completos de un servicio: docker logs -f <nombre-contenedor>" "$BLUE"
}

# Función para reconstruir
rebuild_services() {
    print_color "🔨 Reconstruyendo todos los servicios..." "$YELLOW"
    
    stop_services
    echo ""
    
    print_color "📦 Reconstruyendo imágenes..." "$BLUE"
    cd ms-databases && docker-compose build && cd ..
    cd datalake-ingester && docker-compose build && cd ..
    cd api-consultas && docker-compose build && cd ..
    
    echo ""
    start_services
}

# Main script
case "${1:-}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    rebuild)
        rebuild_services
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
