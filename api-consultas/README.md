# API REST - Consultas Analíticas DataLake

API REST desplegada en **EC2 Ubuntu 22.04** desarrollada con **FastAPI** que ejecuta consultas SQL sobre **Amazon Athena**, exponiendo 15+ endpoints analíticos para consultar datos del DataLake almacenados en S3 y catalogados con AWS Glue.

## 🎯 Descripción del Componente

Esta API implementa la capa de acceso al DataLake, proporcionando:

### **Funcionalidades Implementadas:**
- ✅ **15+ Endpoints RESTful** para consultas analíticas
- ✅ **Integración con Amazon Athena** vía boto3 SDK
- ✅ **Consultas SQL sobre AWS Glue Data Catalog** (9 tablas catalogadas)
- ✅ **Datos de múltiples fuentes**: MySQL, PostgreSQL y MongoDB unificados
- ✅ **Dashboard general** con métricas agregadas
- ✅ **Queries personalizadas** vía endpoint POST
- ✅ **Documentación interactiva** con Swagger UI
- ✅ **Health checks** y monitoreo
- ✅ **CORS configurado** para acceso desde clientes web
- ✅ **Logging estructurado** con niveles configurables

## 🚀 Despliegue en AWS

### Infraestructura AWS Implementada:

**Amazon Athena:**
- Motor de consultas SQL serverless
- Database: `datalake_db` (AWS Glue Data Catalog)
- 9 tablas catalogadas: `ms1_users`, `ms1_orders`, `ms1_products`, `ms2_customers`, `ms2_invoices`, `ms2_payments`, `ms3_inventory`, `ms3_shipments`, `ms3_suppliers`
- Output location: S3 bucket para resultados de queries

**AWS Glue Data Catalog:**
- 3 Crawlers configurados y ejecutados
- 9 tablas con esquemas inferidos automáticamente
- Particiones por fecha reconocidas
- Tipos de datos correctamente mapeados

**EC2 Ubuntu 22.04:**
- API corriendo en contenedor Docker
- Puerto 8000 expuesto
- IAM Role: `LabRole` con permisos Athena, Glue y S3
- Security Group configurado con puerto 8000 abierto
- Health check endpoint activo

**Contenedor Docker:**
- Imagen: Python 3.11 slim
- Framework: FastAPI 0.104.1
- ASGI Server: Uvicorn
- Dependencies: boto3, python-dotenv
- Variables de entorno configuradas vía `.env`

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

## � Componentes AWS Integrados

Esta API se integra con los siguientes componentes ya desplegados:

- ✅ **Amazon S3**: 3 buckets con datos en JSON Lines (`raw-ms1-data-bgc`, `raw-ms2-data-bgc`, `raw-ms3-data-bgc`)
- ✅ **AWS Glue Data Catalog**: Database `datalake_db` con 9 tablas catalogadas
- ✅ **Amazon Athena**: Motor SQL serverless configurado con workgroup `primary`
- ✅ **EC2 Ubuntu 22.04**: Servidor con Docker, IAM Role `LabRole`, Security Group con puerto 8000 abierto
- ✅ **IAM Role**: `LabRole` con permisos S3, Glue y Athena
- ✅ **Docker Network**: Aislamiento de contenedores en EC2

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

## 🚀 Despliegue Implementado

### Contenedor Docker
El servicio está desplegado como contenedor Docker en EC2:

```bash
# Contenedor construido y desplegado
Container: api-consultas-datalake
Image: Python 3.11 slim + FastAPI
Status: Running
Port Mapping: 8000:8000
Network: Default bridge
Restart Policy: always
```

### Configuración de Red
**Security Group configurado con**:
- Type: Custom TCP
- Port: 8000
- Source: 0.0.0.0/0 (acceso público)
- Description: API DataLake access

### Acceso al Servicio
La API está accesible en:
- **Swagger UI**: `http://<IP-PUBLICA-EC2>:8000/docs`
- **Health Check**: `http://<IP-PUBLICA-EC2>:8000/health`
- **Dashboard**: `http://<IP-PUBLICA-EC2>:8000/api/dashboard`
- **Endpoints**: `http://<IP-PUBLICA-EC2>:8000/api/*`

### Verificación de Estado

```bash
# Ver contenedor corriendo
docker ps | grep api-consultas-datalake

# Ver logs en tiempo real
docker logs api-consultas-datalake -f

# Health check desde el servidor
curl http://localhost:8000/health
# Response: {"status":"healthy","athena_connection":"ok"}
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

## 📈 Performance y Costos

### Tiempos de Respuesta Observados
- Health check: < 100ms
- Queries simples (SELECT * FROM tabla LIMIT 10): 2-5 segundos
- Queries complejas (agregaciones, filtros): 5-15 segundos
- Dashboard general: 8-12 segundos (múltiples queries)

### Optimización Implementada
- ✅ Particionamiento por fecha en S3 reduce datos escaneados
- ✅ Uso de `LIMIT` en queries para resultados acotados
- ✅ Formato JSON Lines optimizado para Athena
- ✅ IAM Role en EC2 elimina overhead de credenciales temporales

### Costos AWS Athena
- Precio: $5 USD por TB de datos escaneados
- Con particionamiento y datos de prueba: costo mínimo (< $0.01 por query)
- Sin particiones: Athena escanea todo el bucket

## 🔍 Estado de Implementación

### ✅ Completado
- 15+ endpoints analíticos funcionando
- Integración con Athena operativa
- Datos de 3 fuentes unificados
- Documentación Swagger UI activa
- Health checks implementados
- CORS configurado
- Logging estructurado
- Colección Postman con 16 requests
- Despliegue en EC2 con Docker
- IAM Role configurado

### 📊 Métricas del Sistema
- **9 tablas** catalogadas en Glue
- **3 fuentes** de datos integradas
- **15+ endpoints** disponibles
- **Puerto 8000** expuesto
- **JSON Lines** como formato de datos

## 📄 Información del Proyecto

Este componente es parte de un proyecto educativo para AWS Academy que implementa una arquitectura completa de DataLake en AWS, utilizando servicios como S3, Glue, Athena y EC2.