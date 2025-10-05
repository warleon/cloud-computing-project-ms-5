# DataLake Ingester

Scripts Python que extraen datos desde bases de datos (MySQL, PostgreSQL, MongoDB) y los suben a Amazon S3 en formato JSON Lines, listos para ser catalogados por AWS Glue y consultados con Athena.

## 🎯 Propósito

El ingester es el componente ETL (Extract, Transform, Load) del DataLake:
- **Extract**: Conecta a las bases de datos y extrae todas las tablas/colecciones
- **Transform**: Convierte tipos de datos problemáticos (Decimal, datetime) a formatos JSON válidos
- **Load**: Sube los datos a S3 con particionamiento por fecha

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

## ✨ Características

- ✅ **Multi-database**: Soporte para MySQL, PostgreSQL y MongoDB
- ✅ **Type conversion**: Convierte automáticamente Decimal→float, datetime→ISO string
- ✅ **JSON Lines format**: Datos en NDJSON, formato óptimo para Athena
- ✅ **Date partitioning**: Estructura `year=YYYY/month=MM/day=DD/` para queries eficientes
- ✅ **Containerized**: Cada ingester corre en su propio contenedor Docker
- ✅ **Environment-based**: Configuración mediante variables de entorno (.env)
- ✅ **IAM Role support**: Usa credenciales del EC2 automáticamente

## 📋 Pre-requisitos

- EC2 con Docker y Docker Compose instalados
- IAM Role con permisos S3 PutObject (ej: LabRole)
- 3 buckets S3 ya creados
- Bases de datos corriendo y accesibles (ver `ms-databases/`)

## Configuración

### Variables de Entorno

1. Copia el archivo de ejemplo:
```bash
cp .env.example .env
```

2. Configura las variables en `.env`:

```bash
# AWS Configuration
AWS_DEFAULT_REGION=us-east-1

# S3 Buckets Configuration
S3_BUCKET_MS1=raw-ms1-data-bgc
S3_BUCKET_MS2=raw-ms2-data-bgc
S3_BUCKET_MS3=raw-ms3-data-bgc

# MySQL Database (MS1)
MYSQL_HOST=mysql-test-db
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=rootpassword
MYSQL_DATABASE=testdb

# PostgreSQL Database (MS2)
POSTGRES_HOST=postgres-test-db
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgrespassword
POSTGRES_DATABASE=testdb

# MongoDB Database (MS3)
MONGO_HOST=mongo-test-db
MONGO_PORT=27017
MONGO_USER=admin
MONGO_PASSWORD=adminpassword
MONGO_DATABASE=testdb
MONGO_AUTH_SOURCE=admin

# Ingestion Configuration
INGESTION_INTERVAL=3600
ENABLE_PARTITIONING=true
LOG_LEVEL=INFO
```

## Uso

### Con Docker Compose (recomendado)

Ejecutar todos los ingesters:
```bash
docker-compose up -d
```

Ver logs:
```bash
docker logs ingesta01-mysql -f
docker logs ingesta02-postgresql -f
docker logs ingesta03-mongodb -f
```

Detener ingesters:
```bash
docker-compose down
```

### Ejecución Manual

Ejecutar un ingester específico:
```bash
# MySQL
export DB_TYPE=mysql
export DB_HOST=mysql-test-db
export DB_PORT=3306
export DB_USER=root
export DB_PASSWORD=rootpassword
export DB_NAME=testdb
export S3_BUCKET=raw-ms1-data-bgc
export TABLES=users,orders,products

python ingester.py
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
