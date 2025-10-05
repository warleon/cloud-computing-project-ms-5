# DataLake Architecture - AWS Cloud Project

Arquitectura completa de DataLake desplegada en **EC2 Ubuntu 22.04** con ingesta de datos desde múltiples fuentes, catalogación con Glue y consultas analíticas vía API REST.

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                      EC2 Ubuntu 22.04                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Docker Containers (7 servicios)                     │   │
│  │  ├─ MySQL 8.0         (puerto 3307)                  │   │
│  │  ├─ PostgreSQL 15     (puerto 5433)                  │   │
│  │  ├─ MongoDB 7.0       (puerto 27018)                 │   │
│  │  ├─ Ingester MySQL    (ingesta01-mysql)              │   │
│  │  ├─ Ingester PostgreSQL (ingesta02-postgresql)       │   │
│  │  ├─ Ingester MongoDB  (ingesta03-mongodb)            │   │
│  │  └─ API REST FastAPI  (puerto 8000)                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                  │
└───────────────────────────┼──────────────────────────────────┘
                            │
                            ↓ boto3 (JSON Lines)
        ┌──────────────────────────────────────┐
        │         Amazon S3 (3 Buckets)        │
        │  ├─ raw-ms1-data-bgc (MySQL)         │
        │  ├─ raw-ms2-data-bgc (PostgreSQL)    │
        │  └─ raw-ms3-data-bgc (MongoDB)       │
        └──────────────┬───────────────────────┘
                       │
                       ↓ AWS Glue Crawlers
        ┌──────────────────────────────────────┐
        │   AWS Glue Data Catalog (9 tablas)   │
        └──────────────┬───────────────────────┘
                       │
                       ↓ Athena SQL Queries
        ┌──────────────────────────────────────┐
        │      Amazon Athena (Query Engine)    │
        └──────────────┬───────────────────────┘
                       │
                       ↓ API REST (15+ endpoints)
        ┌──────────────────────────────────────┐
        │      Usuarios/Aplicaciones           │
        └──────────────────────────────────────┘
```

## 📁 Estructura del Proyecto

```
cloud-m5/
│
├── docker-compose.yml         # Orquestador maestro (usa 'include')
├── deploy-all.sh              # Script de despliegue para Ubuntu/Linux
├── .gitignore                 # Protege .env y archivos sensibles
│
├── ms-databases/              # 3 bases de datos de prueba
│   ├── docker-compose.yml     # MySQL, PostgreSQL, MongoDB
│   ├── .env                   # Credenciales de BD (gitignored)
│   ├── .env.example           # Plantilla para configurar
│   ├── init-mysql.sql         # Datos de prueba MS1
│   ├── init-postgres.sql      # Datos de prueba MS2
│   ├── init-mongo.js          # Datos de prueba MS3
│   └── README.md              # Documentación detallada
│
├── datalake-ingester/         # ETL: Extrae y sube a S3
│   ├── docker-compose.yml     # 3 ingesters (uno por DB)
│   ├── ingester.py            # Lógica de ingesta (boto3)
│   ├── .env                   # AWS credentials + S3 buckets
│   ├── .env.example           # Plantilla
│   ├── requirements.txt       # boto3, pymysql, psycopg2, pymongo
│   └── README.md              # Documentación ETL
│
└── api-consultas/             # API REST con FastAPI
    ├── docker-compose.yml     # Servicio API (puerto 8000)
    ├── main.py                # Endpoints de FastAPI
    ├── athena_client.py       # Cliente para consultas Athena
    ├── queries.py             # Queries SQL predefinidas
    ├── .env                   # AWS credentials + config Athena
    ├── .env.example           # Plantilla
    ├── requirements.txt       # fastapi, boto3, uvicorn
    ├── DataLake_API_Postman_Collection.json  # 16 requests
    └── README.md              # Documentación API con endpoints
```

## � Arquitectura de Redes Docker

### Conectividad Entre Componentes

```
┌─────────────────────────────────────────────────┐
│          Red: datalake-network                  │
│          (Comunicación interna)                 │
│                                                 │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐    │
│  │ MySQL    │  │PostgreSQL │  │ MongoDB  │    │
│  │ :3306    │  │  :5432    │  │ :27017   │    │
│  └──────────┘  └───────────┘  └──────────┘    │
│       ↑              ↑              ↑          │
│       │   Conexión directa via    │          │
│       │   nombres de contenedores  │          │
│       └──────────────┴──────────────┘          │
│                      │                         │
│           ┌──────────────────────┐             │
│           │  Ingester Containers │             │
│           │  - ingesta01-mysql   │             │
│           │  - ingesta02-postgres│             │
│           │  - ingesta03-mongodb │             │
│           └──────────────────────┘             │
│                                                 │
└─────────────────────────────────────────────────┘

        ┌─────────────────┐
        │  API-Consultas  │  ← NO necesita red Docker
        │    :8000        │     (solo se comunica con AWS)
        └─────────────────┘
                │
                ↓ HTTPS (boto3)
        ┌─────────────────┐
        │  Amazon Athena  │
        │  (AWS Cloud)    │
        └─────────────────┘
                │
                ↓ Query S3
        ┌─────────────────┐
        │   Amazon S3     │
        └─────────────────┘
```

### ¿Quién necesita estar en la red Docker?

| Componente | Red Docker | Razón |
|------------|------------|-------|
| **ms-databases** | ✅ `datalake-network` | Crea la red para que otros componentes se conecten |
| **datalake-ingester** | ✅ `datalake-network` | Necesita conectarse directamente a las 3 bases de datos usando nombres de contenedores (`mysql-db`, `postgres-db`, `mongo-db`) |
| **api-consultas** | ❌ **NO necesita red** | Solo se comunica con Amazon Athena (servicio AWS en la nube). No accede directamente a las bases de datos |

### Flujo de Conexiones

1. **Ingesters → Bases de Datos**: Conexión directa dentro de `datalake-network`
   - Host: `mysql-db`, `postgres-db`, `mongo-db` (nombres de contenedores)
   - Comunicación: TCP interno de Docker

2. **Ingesters → S3**: Conexión HTTPS vía boto3 SDK
   - Usa IAM Role del EC2 para autenticación
   - No requiere credenciales hardcoded

3. **API → Athena/S3**: Conexión HTTPS vía boto3 SDK
   - Usa IAM Role del EC2 para autenticación
   - Lee datos desde S3 vía queries Athena
   - **Nunca accede directamente a las bases de datos**

### Configuración de Red con `include`

Cuando se usa `include` en Docker Compose (como en este proyecto):

1. **El archivo raíz** (`docker-compose.yml`) define la red:
   ```yaml
   networks:
     datalake-network:
       driver: bridge
   ```

2. **Los archivos individuales** referencian la red pero **NO la definen**:
   ```yaml
   services:
     mysql-db:
       networks:
         - datalake-network
   
   # ❌ NO incluir sección "networks:" al final del archivo
   ```

3. **La red se crea automáticamente** al ejecutar:
   ```bash
   docker-compose up -d
   ```

**Importante**: Los archivos `ms-databases/docker-compose.yml` y `datalake-ingester/docker-compose.yml` solo **referencian** la red en los servicios, pero no la definen al final. Esto evita conflictos con el `include`.

## �🚀 Inicio Rápido en EC2 Ubuntu

### Pre-requisitos

1. **EC2 Ubuntu 22.04** (t2.medium o superior recomendado)
2. **IAM Role** con permisos S3, Glue y Athena (ej: `LabRole` para AWS Academy)
3. **3 Buckets S3** creados:
   - `raw-ms1-data-bgc` (para MySQL)
   - `raw-ms2-data-bgc` (para PostgreSQL)
   - `raw-ms3-data-bgc` (para MongoDB)
4. **Docker y Docker Compose instalados** en EC2

### Instalación de Docker en Ubuntu

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Agregar usuario al grupo docker (evita usar sudo)
sudo usermod -aG docker $USER
newgrp docker

# Verificar instalación
docker --version
docker compose version
```

### 1. Clonar el Proyecto y Configurar Variables

```bash
# Clonar repositorio
git clone <tu-repositorio-url>
cd cloud-m5

# Configurar variables de entorno en cada componente
cd ms-databases
cp .env.example .env
nano .env  # Editar credenciales

cd ../datalake-ingester
cp .env.example .env
nano .env  # Configurar AWS credentials y buckets S3

cd ../api-consultas
cp .env.example .env
nano .env  # Configurar AWS credentials y Athena

cd ..  # Volver a raíz
```

**⚠️ IMPORTANTE**: Los archivos `.env` contienen credenciales reales y NO se suben a Git.

### 2. Desplegar Todos los Servicios

#### Verificar versión de Docker Compose

```bash
# Docker Compose V2 (más reciente - integrado con Docker)
docker compose version

# Docker Compose V1 (versión antigua - comando separado)
docker-compose --version
```

**Nota**: Los comandos cambian según la versión:
- **V2**: `docker compose` (con espacio)
- **V1**: `docker-compose` (con guión)

En los ejemplos siguientes usaremos **V1** (`docker-compose`), si tienes V2 usa `docker compose`.

#### Opción A: Docker Compose desde la Raíz (Más Simple)

```bash
# Levanta TODOS los servicios (7 contenedores)
docker compose up -d

# Ver estado
docker compose ps

# Ver logs en tiempo real
docker compose logs -f

# Detener todo
docker compose down
```

#### Opción B: Script Bash con Comandos Útiles

```bash
# Dar permisos de ejecución
chmod +x deploy-all.sh

# Levantar todos los servicios (con espera de 15s para DBs)
./deploy-all.sh start

# Ver estado de todos los contenedores
./deploy-all.sh status

# Ver logs de todos los servicios
./deploy-all.sh logs

# Detener todos los servicios
./deploy-all.sh stop

# Reiniciar todos los servicios
./deploy-all.sh restart

# Reconstruir contenedores después de cambios
./deploy-all.sh rebuild
```

### 3. Configurar AWS Glue (Desde AWS Console)

```bash
# 1. Crear base de datos en Glue
aws glue create-database --database-input '{"Name": "datalake_db"}'

# 2. Crear y ejecutar 3 crawlers (uno por bucket S3)
# Configurar desde AWS Console:
#   - Crawler 1: raw-ms1-data-bgc → tabla: ms1_*
#   - Crawler 2: raw-ms2-data-bgc → tabla: ms2_*
#   - Crawler 3: raw-ms3-data-bgc → tabla: ms3_*

# 3. Ejecutar crawlers para catalogar datos
# Resultado esperado: 9 tablas en Glue Data Catalog
```

### 4. Verificar Despliegue

```bash
# Ver contenedores corriendo (deberías ver 7)
docker ps

# Probar bases de datos
docker logs mysql-test-db
docker logs postgres-test-db
docker logs mongo-test-db

# Probar ingesters (deben ejecutarse y terminar)
docker logs ingesta01-mysql
docker logs ingesta02-postgresql
docker logs ingesta03-mongodb

# Probar API REST
curl http://localhost:8000/health
# Respuesta esperada: {"status":"healthy"}

# Ver Swagger UI en navegador
# http://<IP-PUBLICA-EC2>:8000/docs
```

## � Servicios Desplegados

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| **mysql-test-db** | 3307 | MySQL 8.0 con datos de MS1 (usuarios, pedidos, productos) |
| **postgres-test-db** | 5433 | PostgreSQL 15 con datos de MS2 (clientes, facturas, pagos) |
| **mongo-test-db** | 27018 | MongoDB 7.0 con datos de MS3 (logs, sesiones, eventos) |
| **ingesta01-mysql** | - | Extrae MySQL → S3 (formato JSON Lines) |
| **ingesta02-postgresql** | - | Extrae PostgreSQL → S3 (formato JSON Lines) |
| **ingesta03-mongodb** | - | Extrae MongoDB → S3 (formato JSON Lines) |
| **api-consultas-datalake** | 8000 | API REST con 15+ endpoints (Athena queries) |

## 🌐 API REST - Endpoints Principales

Accede a la documentación interactiva: **`http://<EC2-IP>:8000/docs`**

### Endpoints Disponibles:

- `GET /health` - Health check
- `GET /api/dashboard` - Dashboard general con métricas
- `GET /api/usuarios` - Listar usuarios (MS1)
- `GET /api/pedidos` - Listar pedidos (MS1)
- `GET /api/productos` - Listar productos (MS1)
- `GET /api/clientes` - Listar clientes (MS2)
- `GET /api/facturas` - Listar facturas (MS2)
- `GET /api/pagos` - Listar pagos (MS2)
- `GET /api/logs` - Listar logs (MS3)
- `GET /api/sesiones` - Listar sesiones (MS3)
- `GET /api/eventos` - Listar eventos (MS3)
- `GET /api/pedidos/{pedido_id}` - Pedido por ID
- `GET /api/productos-por-categoria/{categoria}` - Productos filtrados
- `GET /api/facturas-por-cliente/{cliente_id}` - Facturas de cliente
- `POST /api/query-custom` - Ejecutar query SQL personalizada

**📥 Importar Postman Collection**: `api-consultas/DataLake_API_Postman_Collection.json` (16 requests listos)

## 📚 Documentación Detallada por Componente

- **[ms-databases/README.md](./ms-databases/README.md)** - Bases de datos, esquemas, datos de prueba
- **[datalake-ingester/README.md](./datalake-ingester/README.md)** - Ingesters, formato JSON Lines, particiones S3
- **[api-consultas/README.md](./api-consultas/README.md)** - API REST, endpoints, Athena queries, ejemplos

## 🛠️ Tecnologías Utilizadas

| Categoría | Tecnología | Versión |
|-----------|------------|---------|
| **Cloud** | AWS S3, Glue, Athena, EC2, IAM | - |
| **Lenguaje** | Python | 3.11 |
| **Framework API** | FastAPI | 0.104.1 |
| **SDK AWS** | boto3 | 1.34.0 |
| **Bases de Datos** | MySQL | 8.0 |
| | PostgreSQL | 15 |
| | MongoDB | 7.0 |
| **Containerización** | Docker | 24.x |
| | Docker Compose | v3.8 |
| **Formato de Datos** | JSON Lines (NDJSON) | - |

## 🔐 Seguridad y Buenas Prácticas

### Archivos Protegidos (`.gitignore`):
- ✅ `.env` - Credenciales reales
- ✅ `*.pem`, `*.ppk` - Llaves SSH
- ✅ `notes.txt` - Notas personales
- ✅ `mysql-data/`, `postgres-data/`, `mongo-data/` - Volúmenes de datos

### Credenciales AWS:
- Usa **IAM Roles** en EC2 (no hardcodear access keys)
- Para AWS Academy usa `LabRole` / `LabInstanceProfile`
- Rota credenciales regularmente

## 🔧 Comandos Útiles

```bash
# Ver logs de un servicio específico
docker logs -f <nombre-contenedor>

# Reiniciar un servicio
docker compose restart <nombre-servicio>

# Reconstruir después de cambios en código
docker compose up -d --build

# Detener y eliminar volúmenes (⚠️ elimina datos de BD)
docker compose down -v

# Ver uso de recursos
docker stats

# Limpiar contenedores detenidos
docker system prune -a

# Ver redes Docker
docker network ls

# Inspeccionar un contenedor
docker inspect <nombre-contenedor>
```

## 🐛 Troubleshooting

### Error: "networks.datalake-network conflicts with imported resource"

Este error ocurre cuando múltiples archivos docker-compose intentan definir la misma red.

**Solución**: La red debe definirse **solo en el archivo raíz** (`docker-compose.yml`):

```yaml
# docker-compose.yml (raíz)
networks:
  datalake-network:
    driver: bridge
```

Los archivos individuales (`ms-databases/`, `datalake-ingester/`) **NO** deben tener sección `networks:` al final, solo referencian la red en los servicios.

```bash
# Si persiste el error, limpiar y reiniciar:
docker-compose down
docker network prune -f
docker-compose up -d
```

**Nota importante**: Solo los **ingesters** y **bases de datos** necesitan estar en la red `datalake-network`. La **API** no necesita esta red porque solo se comunica con Athena (AWS).

### Error: "Cannot connect to Docker daemon"
```bash
# Verificar que Docker esté corriendo
sudo systemctl status docker

# Iniciar Docker
sudo systemctl start docker

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
newgrp docker
```

### Error: "The container name is already in use"

Este error ocurre cuando hay contenedores de intentos anteriores que no se eliminaron.

```bash
# Detener todos los servicios
docker-compose down

# Eliminar contenedores específicos que quedaron
docker rm -f $(docker ps -aq --filter "name=ingesta") 2>/dev/null || true
docker rm -f $(docker ps -aq --filter "name=mysql-test") 2>/dev/null || true
docker rm -f $(docker ps -aq --filter "name=postgres-test") 2>/dev/null || true
docker rm -f $(docker ps -aq --filter "name=mongo-test") 2>/dev/null || true
docker rm -f $(docker ps -aq --filter "name=api-consultas") 2>/dev/null || true

# Limpiar redes huérfanas
docker network prune -f

# Levantar servicios limpios
docker-compose up -d
```

### Error: "Port already in use"
```bash
# Ver qué proceso usa el puerto
sudo lsof -i :8000

# O cambiar puerto en .env del servicio
```

### Error: "Permission denied" en S3
- Verifica que el IAM Role en EC2 tenga políticas: `AmazonS3FullAccess`, `AWSGlueConsoleFullAccess`, `AmazonAthenaFullAccess`
- Revisa que los buckets existan en la región correcta (us-east-1)
- Verifica credenciales en archivos `.env`

### Athena devuelve errores de tipos de datos
- Verifica que los datos en S3 estén en **JSON Lines** (no JSON pretty-printed)
- Ejecuta los Glue Crawlers para actualizar el esquema
- Los ingesters ya convierten `Decimal` → `float` y `datetime` → `ISO string`

### Ingesters no suben datos a S3
```bash
# Ver logs de ingesters
docker logs ingesta01-mysql
docker logs ingesta02-postgresql
docker logs ingesta03-mongodb

# Verificar conectividad con AWS
aws s3 ls s3://raw-ms1-data-bgc/

# Revisar .env en datalake-ingester/
```

### Warnings: "AWS_ACCESS_KEY_ID variable is not set"
Estos warnings son **normales y esperados** si usas IAM Role en EC2:
```
WARN[0000] The "AWS_ACCESS_KEY_ID" variable is not set. Defaulting to a blank string.
WARN[0000] The "AWS_SECRET_ACCESS_KEY" variable is not set. Defaulting to a blank string.
WARN[0000] The "AWS_SESSION_TOKEN" variable is not set. Defaulting to a blank string.
```

**Puedes ignorarlos** porque:
- El EC2 usa IAM Role (`LabRole`) para autenticación automática
- No necesitas credenciales hardcoded en los `.env`
- Los servicios obtienen credenciales temporales del EC2 metadata service

Si prefieres eliminar los warnings, deja las variables vacías en los `.env`:
```bash
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_SESSION_TOKEN=
```

### API devuelve 500 Internal Server Error
```bash
# Ver logs de la API
docker logs api-consultas-datalake

# Verificar que Glue Data Catalog tenga tablas
aws glue get-tables --database-name datalake_db

# Verificar .env en api-consultas/
```

## 📝 Limitaciones de AWS Academy

- ⚠️ **No puedes crear IAM Roles nuevos** → Usa `LabRole` existente
- ⚠️ **Sesiones expiran después de 4 horas** → Re-inicia la lab
- ⚠️ **Algunos servicios están restringidos** (Lambda, RDS managed, etc.)
- ✅ **S3, Glue, Athena y EC2 funcionan perfectamente**

## 🤝 Contribución

```bash
# 1. Copiar plantillas de variables
cp ms-databases/.env.example ms-databases/.env
cp datalake-ingester/.env.example datalake-ingester/.env
cp api-consultas/.env.example api-consultas/.env

# 2. Configurar credenciales reales (NO subir a Git)

# 3. Hacer cambios en código

# 4. Probar localmente
docker compose up -d --build

# 5. Asegurarse que .env esté en .gitignore

# 6. Commit y push (sin .env)
git add .
git commit -m "descripción"
git push
```

## 📄 Licencia

Proyecto educativo para AWS Academy - Cloud Computing.

---

**Desarrollado con ☁️ para aprender arquitecturas DataLake en AWS**
