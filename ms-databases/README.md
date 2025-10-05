# Test Databases - Microservicios

Entorno de bases de datos de prueba desplegado en **EC2 Ubuntu 22.04** que simula 3 microservicios con datos de ejemplo, utilizado como fuente de datos para el flujo completo de ingesta hacia el DataLake en AWS.

## 🎯 Descripción del Componente

Este componente implementa:
- **3 Bases de datos containerizadas**: MySQL 8.0, PostgreSQL 15 y MongoDB 7.0
- **Fuentes de datos realistas**: Esquemas y datos que simulan microservicios de producción
- **Datos de prueba pre-cargados**: 9 tablas/colecciones con datos de ejemplo
- **Aislamiento por microservicio**: Cada servicio tiene su propia base de datos independiente
- **Despliegue en Docker**: Todos los servicios corriendo en contenedores Docker en EC2
- **Red compartida**: Comunicación entre contenedores vía red Docker `datalake-network`
- **Integración con DataLake**: Fuente de datos para los ingesters que extraen hacia S3

## 🚀 Despliegue en AWS

### Infraestructura Implementada:
- **EC2 Ubuntu 22.04** (t2.medium o superior)
- **Docker Engine** instalado y configurado
- **Docker Compose** para orquestación de contenedores
- **3 Contenedores activos**:
  - `mysql-test-db` (puerto 3307)
  - `postgres-test-db` (puerto 5433)
  - `mongo-test-db` (puerto 27018)
- **Volúmenes persistentes** para datos de bases de datos
- **Security Group** configurado con puertos necesarios abiertos

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network                           │
│                  (datalake-network)                         │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   MySQL 8.0  │  │PostgreSQL 15 │  │ MongoDB 7.0  │     │
│  │   Port 3306  │  │  Port 5432   │  │  Port 27017  │     │
│  │              │  │              │  │              │     │
│  │  Database:   │  │  Database:   │  │  Database:   │     │
│  │   testdb     │  │   testdb     │  │   testdb     │     │
│  │              │  │              │  │              │     │
│  │  Tables:     │  │  Tables:     │  │  Collections:│     │
│  │  - users     │  │  - customers │  │  - inventory │     │
│  │  - orders    │  │  - invoices  │  │  - shipments │     │
│  │  - products  │  │  - payments  │  │  - suppliers │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         ↓                  ↓                  ↓
    Ingester MS1      Ingester MS2      Ingester MS3
```

## 🗄️ Servicios Implementados

### 1. MySQL 8.0 (Microservicio 1)
- **Contenedor**: `mysql-test-db`
- **Puerto mapeado**: 3307 → 3306
- **Database**: `testdb`
- **Usuario**: configurado vía `.env`
- **Volumen**: `mysql-data` (persistente)
- **Health Check**: `mysqladmin ping` cada 10s
- **Tablas implementadas**: 
  - `users` - 10 usuarios del sistema
  - `orders` - 15 pedidos/órdenes
  - `products` - 12 productos en catálogo
- **Script de inicialización**: `init-mysql.sql`

### 2. PostgreSQL 15 (Microservicio 2)
- **Contenedor**: `postgres-test-db`
- **Puerto mapeado**: 5433 → 5432
- **Database**: `testdb`
- **Usuario**: configurado vía `.env`
- **Volumen**: `postgres-data` (persistente)
- **Health Check**: `pg_isready` cada 10s
- **Tablas implementadas**:
  - `customers` - 5 clientes B2B
  - `invoices` - 8 facturas con diferentes estados
  - `payments` - 6 pagos procesados
- **Script de inicialización**: `init-postgres.sql`

### 3. MongoDB 7.0 (Microservicio 3)
- **Contenedor**: `mongo-test-db`
- **Puerto mapeado**: 27018 → 27017
- **Database**: `testdb`
- **Usuario**: configurado vía `.env`
- **Volumen**: `mongo-data` (persistente)
- **Health Check**: `mongosh --eval 'db.adminCommand("ping")'` cada 10s
- **Colecciones implementadas**:
  - `inventory` - 6 productos con ubicaciones de almacén
  - `shipments` - 7 envíos en diferentes estados
  - `suppliers` - 5 proveedores activos e inactivos
- **Script de inicialización**: `init-mongo.js`

## 📊 Datos de Prueba

### Resumen de Datos Implementados:
- **MySQL**: 37 registros totales (10 users + 15 orders + 12 products)
- **PostgreSQL**: 19 registros totales (5 customers + 8 invoices + 6 payments)
- **MongoDB**: 18 documentos totales (6 inventory + 7 shipments + 5 suppliers)
- **Total**: 74 registros listos para ingesta

## ⚙️ Configuración Implementada

### Variables de Entorno
Las bases de datos están configuradas con variables de entorno definidas en el archivo `.env`:

```bash
# MySQL Configuration (implementada)
MYSQL_ROOT_PASSWORD=********
MYSQL_DATABASE=testdb
MYSQL_USER=appuser
MYSQL_PASSWORD=********
MYSQL_PORT=3307 (mapeado externamente)

# PostgreSQL Configuration (implementada)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=********
POSTGRES_DB=testdb
POSTGRES_APP_USER=appuser
POSTGRES_APP_PASSWORD=********
POSTGRES_PORT=5433 (mapeado externamente)

# MongoDB Configuration (implementada)
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=********
MONGO_INITDB_DATABASE=testdb
MONGO_APP_USER=appuser
MONGO_APP_PASSWORD=********
MONGO_PORT=27018 (mapeado externamente)

# Docker Network
NETWORK_NAME=datalake-network
```

**Nota de Seguridad**: El archivo `.env` con credenciales reales está protegido por `.gitignore` y no se sube a Git.

## 🔌 Conectividad

### Desde Otros Contenedores Docker (Ingesters)
Los ingesters se conectan usando nombres de servicio:
- MySQL: `mysql-db:3306`
- PostgreSQL: `postgres-db:5432`
- MongoDB: `mongo-db:27017`

### Desde Host EC2 (para debugging)
```bash
# MySQL
mysql -h 127.0.0.1 -P 3307 -u appuser -p

# PostgreSQL
psql -h 127.0.0.1 -p 5433 -U appuser -d testdb

# MongoDB
mongosh --host 127.0.0.1 --port 27018 -u appuser -p
```

### Verificar estado

```bash
docker-compose ps
```

### Ver logs

```bash
docker logs mysql-test-db
docker logs postgres-test-db
docker logs mongo-test-db
```

### Detener servicios

```bash
docker-compose down
```

### Detener y eliminar volúmenes (⚠️ Elimina todos los datos)

```bash
docker-compose down -v
```

## Conectarse a las bases de datos

### MySQL

```bash
# Desde el host
docker exec -it mysql-test-db mysql -u root -p

# Con cliente externo
mysql -h localhost -P 3306 -u appuser -p
```

### PostgreSQL

```bash
# Desde el host
docker exec -it postgres-test-db psql -U postgres -d testdb

# Con cliente externo
psql -h localhost -p 5432 -U postgres -d testdb
```

### MongoDB

```bash
# Desde el host
docker exec -it mongo-test-db mongosh -u admin -p

# Con cliente externo
mongosh mongodb://admin:adminpassword@localhost:27017/testdb
```

## Scripts de Inicialización

Los siguientes scripts se ejecutan automáticamente al crear los contenedores:

1. **init-mysql.sql** - Crea tablas e inserta datos de prueba en MySQL
2. **init-postgres.sql** - Crea tablas e inserta datos de prueba en PostgreSQL
3. **init-mongo.js** - Crea colecciones e inserta datos de prueba en MongoDB

## Datos de Prueba

### MySQL - Users
```sql
SELECT * FROM users;
-- 5 usuarios de ejemplo
```

### MySQL - Orders
```sql
SELECT * FROM orders;
-- 8 órdenes con diferentes estados
```

### MySQL - Products
```sql
SELECT * FROM products;
-- 6 productos con precios y stock
```

### PostgreSQL - Customers
```sql
SELECT * FROM customers;
-- 5 clientes B2B
```

### PostgreSQL - Invoices
```sql
SELECT * FROM invoices;
-- 8 facturas con diferentes estados
```

### PostgreSQL - Payments
```sql
SELECT * FROM payments;
-- 6 pagos procesados
```

### MongoDB - Inventory
```javascript
db.inventory.find()
// 6 productos con ubicaciones
```

### MongoDB - Shipments
```javascript
db.shipments.find()
// 7 envíos en diferentes estados
```

### MongoDB - Suppliers
```javascript
db.suppliers.find()
// 5 proveedores activos e inactivos
```

## Red Docker

Todas las bases de datos se ejecutan en la red `datalake-network`, lo que permite:
- Comunicación entre contenedores usando nombres de servicio
- Aislamiento de otros servicios Docker
- Fácil conexión desde otros contenedores (como los ingesters)

## Health Checks

Cada contenedor tiene un health check configurado:
- **MySQL**: `mysqladmin ping`
- **PostgreSQL**: `pg_isready`
- **MongoDB**: `mongosh ping`

Esto asegura que los servicios estén completamente listos antes de que otros contenedores intenten conectarse.

## Troubleshooting

### Error: "Port already in use"
- Verifica que no haya otros servicios usando los puertos 3306, 5432 o 27017
- Cambia los puertos en el archivo `.env` si es necesario

### Error: "Authentication failed"
- Verifica las credenciales en `.env`
- Si cambiaste las credenciales, elimina los volúmenes y recrea los contenedores:
  ```bash
  docker-compose down -v
  docker-compose up -d
  ```

### Los scripts de inicialización no se ejecutan
- Los scripts solo se ejecutan si la base de datos se crea por primera vez
- Para forzar la re-ejecución, elimina los volúmenes: `docker-compose down -v`
