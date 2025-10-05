# 📝 Actualización de docker-compose.yml - env_file + environment

## ✅ Cambios Aplicados

Se han actualizado los 3 archivos `docker-compose.yml` para usar **AMBOS** `env_file` y `environment`, siguiendo las mejores prácticas de Docker Compose.

---

## 🔄 ¿Qué cambió?

### **Antes (solo `env_file`):**
```yaml
services:
  api-consultas-datalake:
    env_file:
      - .env
    # Las variables se cargan pero no son visibles en el YAML
```

### **Ahora (env_file + environment):**
```yaml
services:
  api-consultas-datalake:
    env_file:
      - .env                              # Carga TODAS las variables del .env
    environment:                           # Declara explícitamente las que usa
      - AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-1}
      - ATHENA_DATABASE=${ATHENA_DATABASE:-datalake_raw}
      - API_PORT=${API_PORT:-8000}
```

---

## 🎯 Beneficios de esta Configuración

### 1. **Auto-documentación** 📚
Ahora el `docker-compose.yml` documenta qué variables necesita cada servicio:
```yaml
environment:
  # AWS Configuration        ← Comentarios descriptivos
  - AWS_DEFAULT_REGION=...
  # Athena Configuration
  - ATHENA_DATABASE=...
```

### 2. **Valores por Defecto** ⚙️
Usando `${VARIABLE:-default}` se definen fallbacks:
```yaml
- AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-1}
# Si no existe en .env, usa "us-east-1"
```

### 3. **Validación Clara** ✅
Si una variable obligatoria falta en `.env`, Docker Compose mostrará un warning claro sobre cuál falta.

### 4. **Mejor Debugging** 🐛
Puedes ver rápidamente qué variables usa cada contenedor sin abrir código Python.

### 5. **Flexibilidad** 🔧
Puedes sobrescribir valores sin tocar el `.env`:
```bash
# Sobrescribir solo LOG_LEVEL sin tocar .env
LOG_LEVEL=DEBUG docker-compose up
```

---

## 📊 Resumen de Archivos Actualizados

| Archivo | Servicios | Variables Declaradas |
|---------|-----------|---------------------|
| **api-consultas/docker-compose.yml** | 1 servicio | 11 variables (AWS, Athena, API) |
| **datalake-ingester/docker-compose.yml** | 3 servicios | ~10 variables cada uno (DB, S3, AWS) |
| **ms-databases/docker-compose.yml** | 3 servicios | 3-4 variables cada uno (DB config) |

---

## 🔍 Detalles por Archivo

### 1. `/api-consultas/docker-compose.yml`

**Variables declaradas:**
```yaml
environment:
  # AWS Configuration
  - AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-1}
  - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
  - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
  - AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN}
  
  # Athena Configuration
  - ATHENA_DATABASE=${ATHENA_DATABASE:-datalake_raw}
  - ATHENA_OUTPUT_LOCATION=${ATHENA_OUTPUT_LOCATION}
  - ATHENA_WORKGROUP=${ATHENA_WORKGROUP:-primary}
  
  # API Configuration
  - API_HOST=${API_HOST:-0.0.0.0}
  - API_PORT=${API_PORT:-8000}
  - API_RELOAD=${API_RELOAD:-false}
  
  # Logging
  - LOG_LEVEL=${LOG_LEVEL:-INFO}
```

**Valores por defecto agregados:**
- `AWS_DEFAULT_REGION` → `us-east-1`
- `ATHENA_DATABASE` → `datalake_raw`
- `ATHENA_WORKGROUP` → `primary`
- `API_HOST` → `0.0.0.0`
- `API_PORT` → `8000`
- `API_RELOAD` → `false`
- `LOG_LEVEL` → `INFO`

---

### 2. `/datalake-ingester/docker-compose.yml`

Actualizado para **3 servicios** (ingesta01, ingesta02, ingesta03):

**Variables declaradas en cada servicio:**
```yaml
environment:
  # Ingester Type
  - DB_TYPE=mysql  # Valor fijo según el servicio
  
  # Database Connection (específico por DB)
  - DB_HOST=${MYSQL_HOST:-mysql-test-db}
  - DB_PORT=${MYSQL_PORT:-3306}
  - DB_USER=${MYSQL_USER:-root}
  - DB_PASSWORD=${MYSQL_PASSWORD}
  - DB_NAME=${MYSQL_DATABASE:-testdb}
  
  # S3 Configuration
  - S3_BUCKET=${S3_BUCKET_MS1}
  - TABLES=users,orders,products  # Lista específica por MS
  
  # AWS Configuration
  - AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-1}
  
  # Logging
  - LOG_LEVEL=${LOG_LEVEL:-INFO}
```

**Valores por defecto por servicio:**

| Servicio | DB_HOST | DB_PORT | DB_USER | DB_NAME |
|----------|---------|---------|---------|---------|
| **ingesta01-mysql** | mysql-test-db | 3306 | root | testdb |
| **ingesta02-postgresql** | postgres-test-db | 5432 | postgres | testdb |
| **ingesta03-mongodb** | mongo-test-db | 27017 | admin | testdb |

---

### 3. `/ms-databases/docker-compose.yml`

Actualizado para **3 servicios** (mysql-db, postgres-db, mongo-db):

**MySQL:**
```yaml
environment:
  - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
  - MYSQL_DATABASE=${MYSQL_DATABASE:-testdb}
  - MYSQL_USER=${MYSQL_USER:-appuser}
  - MYSQL_PASSWORD=${MYSQL_PASSWORD}
```

**PostgreSQL:**
```yaml
environment:
  - POSTGRES_USER=${POSTGRES_USER:-postgres}
  - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
  - POSTGRES_DB=${POSTGRES_DB:-testdb}
```

**MongoDB:**
```yaml
environment:
  - MONGO_INITDB_ROOT_USERNAME=${MONGO_INITDB_ROOT_USERNAME:-admin}
  - MONGO_INITDB_ROOT_PASSWORD=${MONGO_INITDB_ROOT_PASSWORD}
  - MONGO_INITDB_DATABASE=${MONGO_INITDB_DATABASE:-testdb}
```

---

## 🔐 Flujo de Variables

```
┌─────────────┐
│   .env      │  ← Archivo con credenciales reales (no se sube a Git)
└──────┬──────┘
       │
       ▼
┌──────────────────────┐
│  docker-compose.yml  │  ← Lee del .env con ${VAR:-default}
│  env_file: .env      │
│  environment:        │
│    - VAR=${VAR}      │
└──────┬───────────────┘
       │
       ▼
┌─────────────────┐
│   Contenedor    │  ← Variables disponibles como variables de entorno
│   (Python app)  │  ← os.getenv("VAR")
└─────────────────┘
```

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Usar valores por defecto
Si tu `.env` está vacío o no existe, los valores por defecto se usan automáticamente:
```yaml
- API_PORT=${API_PORT:-8000}  # Usará 8000 si API_PORT no existe en .env
```

### Ejemplo 2: Sobrescribir desde línea de comandos
```bash
# Cambiar LOG_LEVEL sin tocar .env
LOG_LEVEL=DEBUG docker-compose up

# Cambiar múltiples variables
API_PORT=9000 LOG_LEVEL=DEBUG docker-compose up
```

### Ejemplo 3: Ver qué variables usa un servicio
```bash
# Ver configuración final del servicio
docker-compose config

# Ver solo las variables de entorno
docker inspect api-consultas-datalake | jq '.[0].Config.Env'
```

---

## 🚀 Cómo Aplicar los Cambios en el EC2

```bash
# 1. Conectar al EC2
ssh -i labsuser.pem ubuntu@50.16.35.196

# 2. Detener contenedores actuales
cd ~/api-consultas && docker-compose down
cd ~/datalake-ingester && docker-compose down
cd ~/ms-databases && docker-compose down

# 3. Actualizar los archivos docker-compose.yml
# (Copiar desde tu Windows o editar con nano)

# 4. Verificar que .env existan
ls ~/api-consultas/.env
ls ~/datalake-ingester/.env
ls ~/ms-databases/.env

# 5. Reconstruir y levantar
cd ~/ms-databases && docker-compose up -d
cd ~/datalake-ingester && docker-compose up -d
cd ~/api-consultas && docker-compose up -d

# 6. Verificar logs
docker logs api-consultas-datalake
docker logs ingesta01-mysql
docker logs mysql-test-db
```

---

## ✅ Checklist de Verificación

Después de aplicar los cambios, verifica:

- [ ] Los 3 archivos `docker-compose.yml` tienen sección `environment`
- [ ] Cada variable tiene formato `${VAR:-default}` o `${VAR}`
- [ ] Los comentarios documentan grupos de variables
- [ ] Los archivos `.env` existen y tienen las variables necesarias
- [ ] `docker-compose config` no muestra errores
- [ ] Los contenedores arrancan correctamente
- [ ] Las variables se leen correctamente (revisar logs)

---

## 🎓 Mejores Prácticas Aplicadas

✅ **Usar ambos `env_file` y `environment`**
- `env_file` carga masivamente del .env
- `environment` documenta y define defaults

✅ **Valores por defecto con `:-`**
- `${VAR:-default}` proporciona fallback
- Hace el sistema más robusto

✅ **Comentarios descriptivos**
- Agrupa variables por categoría
- Facilita mantenimiento

✅ **Consistencia en formato**
- Todas las variables usan sintaxis `-`
- Orden alfabético por categoría

✅ **Documentación inline**
- El YAML se auto-documenta
- No necesitas leer código Python para saber qué variables usa

---

## 📚 Referencias

- [Docker Compose Environment Variables](https://docs.docker.com/compose/environment-variables/)
- [Docker Compose File Reference](https://docs.docker.com/compose/compose-file/)
- [12-Factor App - Config](https://12factor.net/config)

---

**Fecha de actualización**: Octubre 5, 2025  
**Versión**: 2.0.0 (env_file + environment)
