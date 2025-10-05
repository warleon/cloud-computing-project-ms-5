# DataLake Ingester - ETL Pipeline

Pipeline ETL implementado con Python que extrae datos desde 3 bases de datos diferentes, los transforma a formato JSON Lines y los carga en **Amazon S3** con particionamiento por fecha, listo para ser catalogado por **AWS Glue** y consultado con **Amazon Athena**.

## 🎯 Descripción del Componente

Este componente implementa el pipeline ETL completo del DataLake:

### **Extract (Extracción)**
- Conexión a MySQL, PostgreSQL y MongoDB
- Extracción de todas las tablas/colecciones de cada base de datos
- Lectura completa de datos sin filtros

### **Transform (Transformación)**
- Conversión automática de tipos incompatibles con JSON:
  - `Decimal` → `float`
  - `datetime`/`date` → `string` (formato ISO 8601)
  - `bytes` → `string` (UTF-8)
- Formato JSON Lines (NDJSON): un objeto JSON por línea
- Validación de datos antes de carga

### **Load (Carga)**
- Subida a Amazon S3 usando boto3
- Particionamiento automático por fecha: `year=YYYY/month=MM/day=DD/`
- 3 buckets S3 diferentes (uno por microservicio)
- Uso de IAM Role para autenticación AWS

## 🚀 Despliegue en AWS

### Infraestructura AWS Implementada:

**Amazon S3 - 3 Buckets Creados:**
- `raw-ms1-data-bgc` → Datos de MySQL (MS1)
- `raw-ms2-data-bgc` → Datos de PostgreSQL (MS2)
- `raw-ms3-data-bgc` → Datos de MongoDB (MS3)

**EC2 Ubuntu 22.04:**
- IAM Role asignado: `LabRole` (permisos S3, Glue, Athena)
- Docker instalado y configurado
- 3 contenedores de ingester ejecutándose:
  - `ingesta01-mysql` → Extrae MySQL → S3
  - `ingesta02-postgresql` → Extrae PostgreSQL → S3
  - `ingesta03-mongodb` → Extrae MongoDB → S3

**Datos Ingestados:**
- 9 tablas/colecciones procesadas
- Datos en formato JSON Lines (NDJSON)
- Estructura de particionamiento implementada
- Datos listos para Glue Crawlers

## 🏗️ Arquitectura

```
Bases de Datos                Ingesters (Docker)           Amazon S3
┌─────────────┐              ┌──────────────────┐         ┌─────────────────────┐
│   MySQL     │─────────────▶│  ingesta01-mysql │────────▶│ raw-ms1-data-bgc/   │
│  (MS1)      │              │  (Python+boto3)  │         │   users/            │
└─────────────┘              └──────────────────┘         │   orders/           │
                                                           │   products/         │
┌─────────────┐              ┌──────────────────┐         │                     │
│ PostgreSQL  │─────────────▶│ingesta02-postgres│────────▶│ raw-ms2-data-bgc/   │
│  (MS2)      │              │  (Python+boto3)  │         │   customers/        │
└─────────────┘              └──────────────────┘         │   invoices/         │
                                                           │   payments/         │
┌─────────────┐              ┌──────────────────┐         │                     │
│  MongoDB    │─────────────▶│ ingesta03-mongodb│────────▶│ raw-ms3-data-bgc/   │
│  (MS3)      │              │  (Python+boto3)  │         │   inventory/        │
└─────────────┘              └──────────────────┘         │   shipments/        │
                                                           │   suppliers/        │
                                                           └─────────────────────┘
```

## ✨ Características Implementadas

- ✅ **Multi-database support**: MySQL, PostgreSQL y MongoDB integrados
- ✅ **Conversión automática de tipos**: Decimal→float, datetime→ISO string, bytes→string
- ✅ **Formato JSON Lines (NDJSON)**: Un objeto JSON por línea, optimizado para Athena
- ✅ **Particionamiento por fecha**: `year=YYYY/month=MM/day=DD/` para queries eficientes
- ✅ **Containerización**: 3 contenedores independientes, uno por fuente de datos
- ✅ **Configuración por environment**: Variables de entorno con `.env` files
- ✅ **IAM Role authentication**: Usa credenciales del EC2 automáticamente (sin hardcoding)
- ✅ **Manejo de errores**: Logging detallado y manejo de excepciones
- ✅ **Ejecución one-shot**: Los contenedores ejecutan y terminan (no quedan corriendo)

## 📊 Resultados de Ingesta

### Datos Procesados y Cargados a S3:

**Bucket: `raw-ms1-data-bgc`** (MySQL)
- `users/` → 10 registros
- `orders/` → 15 registros
- `products/` → 12 registros
- **Total MS1**: 37 registros

**Bucket: `raw-ms2-data-bgc`** (PostgreSQL)
- `customers/` → 5 registros
- `invoices/` → 8 registros
- `payments/` → 6 registros
- **Total MS2**: 19 registros

**Bucket: `raw-ms3-data-bgc`** (MongoDB)
- `inventory/` → 6 documentos
- `shipments/` → 7 documentos
- `suppliers/` → 5 documentos
- **Total MS3**: 18 documentos

**Gran Total**: 74 registros ingestados exitosamente a S3

### Estructura de Archivos en S3:
```
s3://raw-ms1-data-bgc/
  └── users/
      └── year=2025/
          └── month=10/
              └── day=05/
                  └── data.json (JSON Lines format)
```

## ⚙️ Configuración Implementada

### Variables de Entorno
Los ingesters están configurados con las siguientes variables en el archivo `.env`:

```bash
# AWS Configuration (implementada)
AWS_DEFAULT_REGION=us-east-1
AWS_ACCESS_KEY_ID=        # Vacío (usa IAM Role de EC2)
AWS_SECRET_ACCESS_KEY=    # Vacío (usa IAM Role de EC2)
AWS_SESSION_TOKEN=        # Vacío (usa IAM Role de EC2)

# S3 Buckets Configuration (3 buckets creados)
S3_BUCKET_MS1=raw-ms1-data-bgc    # Para datos MySQL
S3_BUCKET_MS2=raw-ms2-data-bgc    # Para datos PostgreSQL
S3_BUCKET_MS3=raw-ms3-data-bgc    # Para datos MongoDB

# MySQL Database Connection (MS1)
MYSQL_HOST=mysql-db              # Nombre del contenedor
MYSQL_PORT=3306                  # Puerto interno
MYSQL_USER=root
MYSQL_PASSWORD=********
MYSQL_DATABASE=testdb

# PostgreSQL Database Connection (MS2)
POSTGRES_HOST=postgres-db        # Nombre del contenedor
POSTGRES_PORT=5432               # Puerto interno
POSTGRES_USER=postgres
POSTGRES_PASSWORD=********
POSTGRES_DATABASE=testdb

# MongoDB Database Connection (MS3)
MONGO_HOST=mongo-db              # Nombre del contenedor
MONGO_PORT=27017                 # Puerto interno
MONGO_USER=admin
MONGO_PASSWORD=********
MONGO_DATABASE=testdb
MONGO_AUTH_SOURCE=admin

# Ingestion Configuration
INGESTION_INTERVAL=3600
ENABLE_PARTITIONING=true
LOG_LEVEL=INFO
```

## 🔄 Ejecución de Ingesters

### Modo de Ejecución Implementado

Los 3 ingesters se ejecutan como **contenedores one-shot** (ejecutan y terminan):

```bash
# Estado de ejecución
Container: ingesta01-mysql        → Ejecuta extracción MySQL → Sube a S3 → Termina (Exit 0)
Container: ingesta02-postgresql   → Ejecuta extracción PostgreSQL → Sube a S3 → Termina (Exit 0)
Container: ingesta03-mongodb      → Ejecuta extracción MongoDB → Sube a S3 → Termina (Exit 0)
```

### Logs de Ejecución

```bash
# Ver logs de ingesta exitosa
docker logs ingesta01-mysql
# Output: "Extracción completada: 3 tablas procesadas → raw-ms1-data-bgc"

docker logs ingesta02-postgresql
# Output: "Extracción completada: 3 tablas procesadas → raw-ms2-data-bgc"

docker logs ingesta03-mongodb
# Output: "Extracción completada: 3 colecciones procesadas → raw-ms3-data-bgc"
```

### Verificación en S3

```bash
# Verificar datos en buckets S3
aws s3 ls s3://raw-ms1-data-bgc/ --recursive
aws s3 ls s3://raw-ms2-data-bgc/ --recursive
aws s3 ls s3://raw-ms3-data-bgc/ --recursive

# Ejemplo de salida:
# 2025-10-05 users/year=2025/month=10/day=05/data.json
# 2025-10-05 orders/year=2025/month=10/day=05/data.json
# 2025-10-05 products/year=2025/month=10/day=05/data.json
```

## Estructura de datos en S3

Los datos se almacenan con la siguiente estructura:
```
s3://bucket-name/
  └── table_name/
      └── year=2025/
          └── month=10/
              └── day=04/
                  └── data.json
```

Cada archivo `data.json` contiene datos en formato JSON Lines (un objeto JSON por línea):
```json
{"id": 1, "name": "John", "email": "john@example.com"}
{"id": 2, "name": "Jane", "email": "jane@example.com"}
```

## Conversión de Tipos

El ingester convierte automáticamente:
- `Decimal` → `float`
- `datetime`/`date` → `string` (ISO 8601)
- `bytes` → `string` (UTF-8)

Esto asegura que AWS Glue Crawler infiera correctamente los tipos de datos.

## Troubleshooting

### Error: "DB_TYPE y S3_BUCKET son requeridos"
- Verifica que el archivo `.env` exista y tenga las variables correctas
- Revisa que `docker-compose.yml` esté cargando el archivo `.env`

### Error de conexión a la base de datos
- Verifica que el host sea correcto (nombre del contenedor en Docker)
- Asegúrate de que las bases de datos estén corriendo
- Revisa las credenciales en `.env`

### Error de permisos en S3
- Verifica que el EC2 tenga un IAM Role con permisos S3
- Revisa que los buckets existan y estén en la misma región
