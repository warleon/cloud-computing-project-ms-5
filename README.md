# DataLake Architecture - AWS Cloud Project

Arquitectura completa de DataLake en AWS con ingesta de datos desde múltiples fuentes, catalogación con Glue y consultas analíticas vía API REST.

## 🏗️ Arquitectura

```
Bases de Datos (MySQL, PostgreSQL, MongoDB)
    ↓
Ingesters (Python + boto3)
    ↓
Amazon S3 (Raw Data - Particionado por fecha)
    ↓
AWS Glue Crawlers (Data Catalog)
    ↓
Amazon Athena (SQL Queries)
    ↓
API REST (FastAPI)
    ↓
Usuarios/Aplicaciones
```

## 📁 Estructura del Proyecto

```
cloud-m5/
│
├── ms-databases/          # Bases de datos de prueba (MySQL, PostgreSQL, MongoDB)
├── datalake-ingester/     # Scripts de ingesta de datos hacia S3
└── api-consultas/         # API REST para consultas analíticas
```

## 🚀 Inicio Rápido

### 1. Configuración de Variables de Entorno

Cada carpeta necesita su archivo `.env`:

```bash
# En cada carpeta (ms-databases, datalake-ingester, api-consultas)
cp .env.example .env
```

**⚠️ IMPORTANTE**: Edita cada `.env` con tus credenciales reales. Los archivos `.env.example` son solo plantillas.

### 2. Despliegue en AWS

#### Pre-requisitos:
- EC2 con Ubuntu 22.04
- IAM Role con permisos S3, Glue y Athena (ej: LabRole)
- Docker y Docker Compose instalados
- 3 buckets S3 creados

#### Pasos:

```bash
# 1. Levantar bases de datos de prueba
cd ms-databases
docker-compose up -d

# 2. Ejecutar ingesters (extracción de datos a S3)
cd ../datalake-ingester
docker-compose up -d

# 3. Configurar Glue Crawlers (desde AWS Console)
# - Crear Glue Database
# - Crear Crawlers para cada bucket
# - Ejecutar Crawlers

# 4. Levantar API REST
cd ../api-consultas
docker-compose up -d
```

### 3. Verificar Despliegue

```bash
# Ver estado de contenedores
docker ps

# Ver logs
docker logs mysql-test-db
docker logs ingesta01-mysql
docker logs api-consultas-datalake

# Probar API
curl http://localhost:8000/health
```

## 📚 Documentación por Componente

### 🗄️ [ms-databases](./ms-databases/README.md)
Bases de datos de prueba con datos de ejemplo para simular 3 microservicios.

### 📥 [datalake-ingester](./datalake-ingester/README.md)
Scripts Python que extraen datos de las bases de datos y los suben a S3 en formato JSON Lines.

### 🌐 [api-consultas](./api-consultas/README.md)
API REST desarrollada con FastAPI que ejecuta queries en Athena y expone endpoints analíticos.

## 🔐 Seguridad

### Archivos que NO se suben a Git:
- ✅ `.env` (contiene credenciales reales)
- ✅ `*.pem` y `*.ppk` (llaves SSH)
- ✅ `notes.txt` (puede contener info sensible)
- ✅ Datos de bases de datos (`mysql-data/`, etc.)

### Archivos que SÍ se suben a Git:
- ✅ `.env.example` (plantillas sin credenciales reales)
- ✅ Código fuente (`.py`, `.js`, `.sql`)
- ✅ Dockerfiles y docker-compose.yml
- ✅ README.md y documentación

## 🛠️ Tecnologías Utilizadas

### AWS Services:
- **S3** - Almacenamiento de datos raw
- **EC2** - Servidor para contenedores Docker
- **IAM** - Gestión de permisos (LabRole)
- **Glue** - Data Catalog y Crawlers
- **Athena** - Motor de consultas SQL

### Stack Tecnológico:
- **Python 3.11** - Lenguaje principal
- **FastAPI** - Framework para API REST
- **boto3** - SDK de AWS para Python
- **Docker & Docker Compose** - Containerización
- **MySQL 8.0** - Base de datos relacional
- **PostgreSQL 15** - Base de datos relacional
- **MongoDB 7.0** - Base de datos NoSQL

## 📊 Endpoints de la API

Una vez desplegada la API, accede a:
- **Swagger UI**: `http://<EC2-IP>:8000/docs`
- **Health Check**: `http://<EC2-IP>:8000/health`
- **Dashboard**: `http://<EC2-IP>:8000/api/dashboard`

Ver [Colección de Postman](./api-consultas/DataLake_API_Postman_Collection.json) para probar todos los endpoints.

## 🔧 Comandos Útiles

```bash
# Ver todos los contenedores corriendo
docker ps

# Ver logs en tiempo real
docker logs -f <container-name>

# Reiniciar un servicio
docker-compose restart <service-name>

# Detener todo
docker-compose down

# Detener y eliminar volúmenes (⚠️ elimina datos)
docker-compose down -v

# Reconstruir después de cambios
docker-compose up -d --build
```

## 🐛 Troubleshooting

### Error: "network not found"
```bash
# Crear la red manualmente
docker network create datalake-network
```

### Error: "Port already in use"
```bash
# Cambiar puertos en .env
# O detener el servicio que usa el puerto
```

### Error: "Permission denied" en S3
- Verifica que el IAM Role tenga permisos S3
- Revisa que los buckets existan en la región correcta

### Athena devuelve errores de tipo
- Verifica que los Crawlers hayan ejecutado correctamente
- Asegúrate de que los datos estén en formato JSON Lines (no JSON pretty-printed)

## 📝 Notas Adicionales

### AWS Academy Limitations:
- No puedes crear IAM Roles nuevos (usa LabRole/LabInstanceProfile)
- Las sesiones expiran después de 4 horas
- Algunos servicios pueden estar restringidos

### Recomendaciones:
- Usa contraseñas seguras en producción
- Configura backups de las bases de datos
- Implementa monitoreo y alertas
- Considera usar AWS Secrets Manager para credenciales

## 🤝 Contribución

1. Copia `.env.example` a `.env` en cada carpeta
2. Configura tus credenciales
3. Haz tus cambios
4. Asegúrate de que `.env` esté en `.gitignore`
5. Prueba localmente antes de subir

## 📄 Licencia

Este es un proyecto educativo para AWS Academy.

---

**Desarrollado con ❤️ para aprender arquitecturas de DataLake en AWS**
