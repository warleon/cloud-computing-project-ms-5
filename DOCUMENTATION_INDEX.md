# 📚 Índice de Documentación del Proyecto

Este proyecto cuenta con documentación completa en cada carpeta. A continuación, un índice de todos los README disponibles:

## 📄 Documentación Principal

### [README.md (Raíz)](./README.md)
- **Ubicación**: `/`
- **Contenido**: 
  - Visión general de la arquitectura completa
  - Estructura del proyecto
  - Guía de inicio rápido
  - Tecnologías utilizadas
  - Troubleshooting general

---

## 📁 Documentación por Componente

### 1. [API REST - Consultas Analíticas](./api-consultas/README.md)
- **Ubicación**: `/api-consultas/`
- **Contenido**:
  - ✅ Propósito y arquitectura del componente
  - ✅ Pre-requisitos y configuración
  - ✅ Variables de entorno explicadas
  - ✅ Lista completa de 15+ endpoints
  - ✅ Ejemplos de uso con curl
  - ✅ Instrucciones de despliegue paso a paso
  - ✅ Troubleshooting específico
  - ✅ Comandos útiles de Docker
  - ✅ Detalles de performance y optimización
  - ✅ Roadmap de mejoras futuras

**Temas clave**:
- Cómo ejecutar queries en Athena vía API REST
- Configuración de permisos IAM
- Apertura de puertos en Security Group
- Uso de Postman Collection
- Swagger UI interactivo

---

### 2. [DataLake Ingester](./datalake-ingester/README.md)
- **Ubicación**: `/datalake-ingester/`
- **Contenido**:
  - ✅ Propósito y arquitectura ETL
  - ✅ Diagrama de flujo de datos
  - ✅ Pre-requisitos y configuración
  - ✅ Variables de entorno explicadas
  - ✅ Estructura de datos en S3
  - ✅ Conversión de tipos automática
  - ✅ Ejecución con Docker Compose
  - ✅ Ejecución manual (sin Docker)
  - ✅ Troubleshooting específico
  - ✅ Formato JSON Lines explicado

**Temas clave**:
- Cómo conectar a MySQL, PostgreSQL, MongoDB
- Conversión de Decimal y datetime
- Particionamiento por fecha en S3
- Permisos IAM necesarios
- Debugging de conexiones a bases de datos

---

### 3. [Test Databases - Microservicios](./ms-databases/README.md)
- **Ubicación**: `/ms-databases/`
- **Contenido**:
  - ✅ Propósito y arquitectura de las bases de datos
  - ✅ Diagrama de red Docker
  - ✅ Pre-requisitos y configuración
  - ✅ Variables de entorno explicadas
  - ✅ Descripción de cada base de datos
  - ✅ Datos de prueba incluidos
  - ✅ Comandos para conectarse a cada DB
  - ✅ Scripts de inicialización explicados
  - ✅ Health checks configurados
  - ✅ Troubleshooting específico

**Temas clave**:
- Cómo levantar las 3 bases de datos
- Datos de prueba pre-cargados
- Conexión desde contenedores y desde host
- Red Docker compartida
- Resetear bases de datos

---

## 🗂️ Documentación Adicional

### [Colección de Postman](./api-consultas/DataLake_API_Postman_Collection.json)
- **Ubicación**: `/api-consultas/`
- **Contenido**: 16+ requests HTTP preconfiguradas
- **Uso**: Importar en Postman para probar todos los endpoints

### [Archivos .env.example](./README.md#configuración)
- **Ubicaciones**: 
  - `/api-consultas/.env.example`
  - `/datalake-ingester/.env.example`
  - `/ms-databases/.env.example`
- **Propósito**: Plantillas de configuración sin datos sensibles
- **Uso**: Copiar a `.env` y rellenar con credenciales reales

---

## 📖 Cómo Navegar la Documentación

### Para Principiantes
1. Leer [README principal](./README.md) - Entender la arquitectura completa
2. Leer [ms-databases/README.md](./ms-databases/README.md) - Levantar bases de datos
3. Leer [datalake-ingester/README.md](./datalake-ingester/README.md) - Ingestar datos
4. Leer [api-consultas/README.md](./api-consultas/README.md) - Consultar datos

### Para Deployment
1. [README principal](./README.md) → Sección "Inicio Rápido"
2. Cada componente tiene sección "Instalación y Ejecución"
3. Revisar sección "Troubleshooting" si hay errores

### Para Desarrollo
1. Revisar estructura de proyecto en cada README
2. Variables de entorno en `.env.example`
3. Sección "Comandos Útiles" en cada README
4. Sección "Contribución" en cada README

---

## 🎯 Mapa de Contenido por Tema

### Configuración de Variables de Entorno
- [API REST - Configuración](./api-consultas/README.md#configuración)
- [Ingester - Variables de Entorno](./datalake-ingester/README.md#variables-de-entorno)
- [Databases - Configuración](./ms-databases/README.md#variables-de-entorno)

### Docker y Contenedores
- [API REST - Comandos Útiles](./api-consultas/README.md#comandos-útiles)
- [Ingester - Uso con Docker](./datalake-ingester/README.md#uso)
- [Databases - Uso](./ms-databases/README.md#uso)

### Troubleshooting
- [API REST - Troubleshooting](./api-consultas/README.md#troubleshooting)
- [Ingester - Troubleshooting](./datalake-ingester/README.md#troubleshooting)
- [Databases - Troubleshooting](./ms-databases/README.md#troubleshooting)

### AWS Services
- [README Principal - AWS Services](./README.md#tecnologías-utilizadas)
- [API REST - IAM y Athena](./api-consultas/README.md#pre-requisitos)
- [Ingester - S3 y Particiones](./datalake-ingester/README.md#estructura-de-datos-en-s3)

### Seguridad
- [README Principal - Seguridad](./README.md#seguridad)
- [API REST - Seguridad](./api-consultas/README.md#seguridad)

---

## ✅ Checklist de Documentación

- [x] README principal con arquitectura completa
- [x] README de API REST con endpoints y ejemplos
- [x] README de Ingester con ETL explicado
- [x] README de Databases con datos de prueba
- [x] .env.example en cada carpeta
- [x] .gitignore en raíz y subcarpetas
- [x] Colección de Postman lista para usar
- [x] Diagramas ASCII de arquitectura
- [x] Secciones de troubleshooting en cada README
- [x] Comandos útiles de Docker en cada README
- [x] Ejemplos prácticos con curl/código

---

## 🤝 Cómo Contribuir a la Documentación

Si encuentras algo confuso o quieres mejorar la documentación:

1. Lee el README actual
2. Identifica qué falta o qué mejorar
3. Crea una copia de `.env.example` si vas a documentar nuevas variables
4. Agrega ejemplos prácticos cuando sea posible
5. Mantén el formato consistente (emojis, títulos, code blocks)
6. No incluyas credenciales reales en los README

---

**Última actualización**: Octubre 5, 2025  
**Versión**: 1.0.0
