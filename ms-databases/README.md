# Test Databases - Microservicios

Entorno de bases de datos de prueba que simula 3 microservicios con datos de ejemplo, diseñado para probar el flujo completo de ingesta hacia el DataLake.

## 🎯 Propósito

Este componente proporciona:
- **Fuentes de datos realistas**: 3 bases de datos con esquemas diferentes
- **Datos de prueba**: Tablas/colecciones pre-pobladas con datos de ejemplo
- **Aislamiento**: Cada microservicio tiene su propia base de datos
- **Facilidad de setup**: Todo containerizado con Docker Compose
- **Compatibilidad**: Diseñado para trabajar con el ingester del DataLake

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

## 🗄️ Servicios

### 1. MySQL (Microservicio 1)
- **Puerto**: 3306
- **Database**: testdb
- **Tablas**: 
  - `users` - Usuarios del sistema
  - `orders` - Pedidos/órdenes
  - `products` - Catálogo de productos

### 2. PostgreSQL (Microservicio 2)
- **Puerto**: 5432
- **Database**: testdb
- **Tablas**:
  - `customers` - Clientes B2B
  - `invoices` - Facturas
  - `payments` - Pagos

### 3. MongoDB (Microservicio 3)
- **Puerto**: 27017
- **Database**: testdb
- **Colecciones**:
  - `inventory` - Inventario de productos
  - `shipments` - Envíos/entregas
  - `suppliers` - Proveedores

## Configuración

### Variables de Entorno

1. Copia el archivo de ejemplo:
```bash
cp .env.example .env
```

2. Configura las variables en `.env`:

```bash
# MySQL Configuration
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=testdb
MYSQL_USER=appuser
MYSQL_PASSWORD=apppass123
MYSQL_PORT=3306

# PostgreSQL Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgrespassword
POSTGRES_DB=testdb
POSTGRES_APP_USER=appuser
POSTGRES_APP_PASSWORD=apppass123
POSTGRES_PORT=5432

# MongoDB Configuration
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=adminpassword
MONGO_INITDB_DATABASE=testdb
MONGO_APP_USER=appuser
MONGO_APP_PASSWORD=apppass123
MONGO_PORT=27017

# Docker Network
NETWORK_NAME=datalake-network
```

**Nota**: Estas son credenciales de prueba. En producción, usa contraseñas seguras.

## Uso

### Levantar todas las bases de datos

```bash
docker-compose up -d
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
