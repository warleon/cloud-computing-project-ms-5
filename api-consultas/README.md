# API REST - Consultas Analíticas DataLake

API REST desarrollada con **FastAPI** que ejecuta consultas SQL sobre Amazon Athena, exponiendo endpoints analíticos para consultar datos del DataLake almacenados en S3.

## 🎯 Propósito

Esta API actúa como capa de acceso al DataLake, permitiendo:
- ✅ Ejecutar consultas SQL sobre datos catalogados en AWS Glue
- ✅ Exponer endpoints RESTful para análisis de datos
- ✅ Consultar datos de múltiples fuentes (MySQL, PostgreSQL, MongoDB)
- ✅ Generar dashboards y reportes analíticos
- ✅ Ejecutar queries personalizadas vía HTTP

## 🏗️ Arquitectura

```
Cliente (Postman/Browser/App)
    ↓
API REST (FastAPI - Puerto 8000)
    ↓
AthenaClient (boto3)
    ↓
Amazon Athena
    ↓
AWS Glue Data Catalog
    ↓
Amazon S3 (Datos en JSON Lines)
```

## 📋 Pre-requisitos

- EC2 con Docker y Docker Compose instalados
- IAM Role con permisos para Athena, Glue y S3 (ej: LabRole)
- Datos ya ingestados en S3 con formato JSON Lines
- Tablas catalogadas en AWS Glue Data Catalog
- Security Group con puerto 8000 abierto (para acceso externo)

## ⚙️ Configuración

### Variables de Entorno

1. Copia el archivo de ejemplo:
```bash
cp .env.example .env
```

2. Configura las variables en `.env`:
```bash
# AWS Configuration
AWS_DEFAULT_REGION=us-east-1
AWS_ACCESS_KEY_ID=          # Opcional si usas IAM Role
AWS_SECRET_ACCESS_KEY=      # Opcional si usas IAM Role
AWS_SESSION_TOKEN=          # Opcional si usas IAM Role

# Athena Configuration
ATHENA_DATABASE=datalake_raw
ATHENA_OUTPUT_LOCATION=s3://raw-ms1-data-bgc/athena-results/
ATHENA_WORKGROUP=primary

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false

# Logging
LOG_LEVEL=INFO
```

**Nota**: Si tu EC2 tiene un IAM Role asignado (como LabInstanceProfile), no necesitas configurar las credenciales AWS manualmente.

## Endpoints Disponibles

### Health Check
- GET / - Informacion del servicio
- GET /health - Health check con verificacion de Athena

### Ventas (MySQL)
- GET /api/ventas/resumen - Resumen general de ventas
- GET /api/ventas/por-usuario - Ventas agrupadas por usuario
- GET /api/ventas/por-estado - Ventas por estado de orden

### Productos
- GET /api/productos/top?limit=10 - Top productos por valor de inventario

### Clientes B2B (PostgreSQL)
- GET /api/clientes/top?limit=10 - Top clientes por facturacion
- GET /api/facturas/estado - Estado de facturas y pagos

### Inventario y Logistica (MongoDB)
- GET /api/inventario/bajo-stock?threshold=100 - Productos con stock bajo
- GET /api/envios/estado - Resumen de estado de envios

### Dashboard
- GET /api/dashboard - Metricas para dashboard ejecutivo

### Custom Query
- POST /api/query/custom - Ejecutar query SQL personalizada

### Metadata
- GET /api/queries/list - Listar queries predefinidas disponibles

## 📚 Documentación Interactiva

Una vez corriendo la API, accede a:
- **Swagger UI**: `http://<IP-PUBLICA-EC2>:8000/docs` (interfaz interactiva para probar endpoints)
- **ReDoc**: `http://<IP-PUBLICA-EC2>:8000/redoc` (documentación alternativa)
- **Health Check**: `http://<IP-PUBLICA-EC2>:8000/health`

## 🚀 Instalación y Ejecución

### 1. Construir y levantar el contenedor

```bash
cd ~/api-consultas

# Construir imagen y levantar contenedor
docker-compose up -d --build
```

### 2. Verificar estado

```bash
# Ver contenedores corriendo
docker ps

# Ver logs en tiempo real
docker logs api-consultas-datalake -f

# Health check desde el servidor
curl http://localhost:8000/health
```

### 3. Abrir puerto en Security Group

Para acceder desde fuera del EC2:
1. AWS Console → EC2 → Security Groups
2. Seleccionar el Security Group de tu EC2
3. **Edit inbound rules** → **Add rule**:
   - Type: **Custom TCP**
   - Port: **8000**
   - Source: **0.0.0.0/0** (o tu IP)
4. **Save rules**

### 4. Probar desde navegador/Postman

```
http://<IP-PUBLICA-EC2>:8000/docs
http://<IP-PUBLICA-EC2>:8000/health
http://<IP-PUBLICA-EC2>:8000/api/dashboard
```

## 📦 Colección de Postman

Importa la colección lista para usar: [`DataLake_API_Postman_Collection.json`](./DataLake_API_Postman_Collection.json)

**En Postman**:
1. File → Import
2. Seleccionar el archivo JSON
3. La colección aparecerá con 16+ requests preconfiguradas

## 💡 Ejemplos de Uso

### Health Check
```bash
curl http://localhost:8000/health
```
**Respuesta:**
```json
{
  "status": "healthy",
  "athena_connection": "ok",
  "timestamp": "2025-10-05T02:47:10"
}
```

### Resumen de Ventas
```bash
curl http://localhost:8000/api/ventas/resumen
```

### Top 5 Clientes
```bash
curl http://localhost:8000/api/clientes/top?limit=5
```

### Dashboard Ejecutivo
```bash
curl http://localhost:8000/api/dashboard
```

### Query Personalizada (POST)
```bash
curl -X POST http://localhost:8000/api/query/custom \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT * FROM mysql_ms1_orders WHERE total_amount > 500 LIMIT 10"
  }'
```

## 🛠️ Estructura del Proyecto

```
api-consultas/
├── main.py                    # Aplicación FastAPI con endpoints
├── athena_client.py           # Cliente para ejecutar queries en Athena
├── queries.py                 # Queries SQL predefinidas
├── requirements.txt           # Dependencias Python
├── Dockerfile                 # Imagen Docker
├── docker-compose.yml         # Orquestación del contenedor
├── .env                       # Variables de entorno (no se sube a Git)
├── .env.example               # Plantilla de variables
└── DataLake_API_Postman_Collection.json  # Colección de Postman
```

## 🔧 Comandos Útiles

### Ver logs
```bash
docker logs api-consultas-datalake -f
```

### Reiniciar contenedor
```bash
docker-compose restart
```

### Detener contenedor
```bash
docker-compose down
```

### Reconstruir después de cambios
```bash
docker-compose up -d --build
```

### Entrar al contenedor
```bash
docker exec -it api-consultas-datalake bash
```

## 🐛 Troubleshooting

### Error: "Connection to Athena failed"
**Causa**: IAM Role sin permisos o región incorrecta
**Solución**:
```bash
# Verificar IAM Role del EC2
aws sts get-caller-identity

# Verificar región en .env
cat .env | grep AWS_DEFAULT_REGION
```

### Error: "Table not found"
**Causa**: Glue Crawlers no han ejecutado o tabla no existe
**Solución**:
```bash
# Listar tablas disponibles
curl http://localhost:8000/api/tablas
```

### Error: "Port 8000 already in use"
**Causa**: Otro servicio usa el puerto 8000
**Solución**:
```bash
# Cambiar puerto en .env
API_PORT=8001

# O detener el servicio que usa el puerto
sudo lsof -i :8000
```

### No puedo acceder desde mi navegador
**Causa**: Puerto 8000 no está abierto en Security Group
**Solución**: Ver paso 3 de "Instalación y Ejecución"

## 📊 Detalles de los Endpoints

### Endpoints de Solo Lectura (GET)

| Endpoint | Descripción | Parámetros |
|----------|-------------|------------|
| `/` | Información del servicio | - |
| `/health` | Health check con verificación Athena | - |
| `/api/dashboard` | Dashboard con métricas generales | - |
| `/api/ventas/resumen` | Resumen total de ventas | - |
| `/api/ventas/por-usuario` | Ventas agrupadas por usuario | - |
| `/api/clientes/top` | Top clientes por facturación | `limit` (default: 10) |
| `/api/productos/mas-vendidos` | Productos más vendidos | `limit` (default: 10) |
| `/api/inventario/estado` | Estado del inventario | - |
| `/api/inventario/bajo-stock` | Productos con stock bajo | `threshold` (default: 50) |
| `/api/pagos/estado` | Resumen de pagos por estado | - |
| `/api/facturas/pendientes` | Facturas con estado pending | - |
| `/api/envios/por-estado` | Envíos agrupados por estado | - |
| `/api/proveedores/activos` | Proveedores activos | - |
| `/api/ordenes/alto-valor` | Órdenes de alto valor | `min_amount` (default: 500) |
| `/api/tablas` | Lista tablas disponibles en Glue | - |

### Endpoints de Escritura (POST)

| Endpoint | Descripción | Body |
|----------|-------------|------|
| `/api/query/custom` | Ejecutar query SQL personalizada | `{"query": "SELECT * FROM ..."}` |

## 🔐 Seguridad

### Variables de Entorno
- ✅ Las credenciales AWS se obtienen del IAM Role (no hardcoded)
- ✅ Archivo `.env` no se sube a Git (protegido por `.gitignore`)
- ✅ `.env.example` es solo una plantilla sin credenciales reales

### CORS
- ⚠️ Actualmente permite todos los orígenes (`allow_origins=["*"]`)
- 📝 En producción, especifica dominios permitidos

### Rate Limiting
- ⚠️ No implementado actualmente
- 📝 Considera agregar rate limiting en producción

## 📈 Performance

### Tiempos de Respuesta Típicos
- Health check: < 100ms
- Queries simples: 2-5 segundos
- Queries complejas (JOINs): 5-15 segundos

### Optimización
- Athena cobra por datos escaneados ($5 por TB)
- Usa particiones para reducir costos
- Limita resultados con `LIMIT` en queries

## 🚀 Próximas Mejoras

- [ ] Implementar caché de resultados (Redis)
- [ ] Agregar autenticación (JWT)
- [ ] Rate limiting por IP
- [ ] Métricas con Prometheus
- [ ] Frontend web para visualización
- [ ] Exportar resultados a CSV/Excel
- [ ] Queries asíncronas para queries largas

## 🤝 Contribución

1. Copia `.env.example` a `.env`
2. Configura tus credenciales
3. Haz tus cambios en `main.py`, `athena_client.py` o `queries.py`
4. Prueba localmente con `docker-compose up -d --build`
5. Verifica que `.env` no se suba a Git

## 📄 Licencia

Este es un proyecto educativo para AWS Academy.