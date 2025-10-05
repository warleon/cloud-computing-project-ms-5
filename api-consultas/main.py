"""
API REST para Consultas Analíticas del DataLake
Ejecuta queries en Athena y devuelve resultados en JSON
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

from athena_client import AthenaClient
from queries import PREDEFINED_QUERIES

# Cargar variables de entorno
load_dotenv()

# Configurar logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="DataLake Analytics API",
    description="API REST para consultas analíticas sobre el DataLake",
    version="1.0.0"
)

# Configurar CORS (para permitir acceso desde navegadores)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cliente de Athena
athena_client = AthenaClient()


# Modelos Pydantic
class CustomQueryRequest(BaseModel):
    query: str
    database: str = "datalake_raw"


class QueryResponse(BaseModel):
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    rows_count: Optional[int] = None
    execution_time_ms: Optional[int] = None
    error: Optional[str] = None


# ========== ENDPOINTS ==========

@app.get("/", tags=["Health"])
async def root():
    """Endpoint raíz - Health check"""
    return {
        "service": "DataLake Analytics API",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check del servicio"""
    try:
        # Verificar conexión con Athena
        test_query = "SELECT 1 as test"
        result = athena_client.execute_query(test_query)
        
        return {
            "status": "healthy",
            "athena_connection": "ok" if result else "error",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


# ========== VENTAS (MySQL) ==========

@app.get("/api/ventas/resumen", tags=["Ventas"], response_model=QueryResponse)
async def get_ventas_resumen():
    """Obtener resumen general de ventas"""
    try:
        query = PREDEFINED_QUERIES["ventas_resumen"]
        results = athena_client.execute_query(query)
        
        return QueryResponse(
            success=True,
            data=results,
            rows_count=len(results) if results else 0,
            execution_time_ms=athena_client.last_execution_time_ms
        )
    except Exception as e:
        logger.error(f"Error en ventas_resumen: {e}")
        return QueryResponse(success=False, error=str(e))


@app.get("/api/ventas/por-usuario", tags=["Ventas"], response_model=QueryResponse)
async def get_ventas_por_usuario():
    """Obtener ventas agrupadas por usuario"""
    try:
        query = PREDEFINED_QUERIES["ventas_por_usuario"]
        results = athena_client.execute_query(query)
        
        return QueryResponse(
            success=True,
            data=results,
            rows_count=len(results) if results else 0,
            execution_time_ms=athena_client.last_execution_time_ms
        )
    except Exception as e:
        logger.error(f"Error en ventas_por_usuario: {e}")
        return QueryResponse(success=False, error=str(e))


@app.get("/api/ventas/por-estado", tags=["Ventas"], response_model=QueryResponse)
async def get_ventas_por_estado():
    """Obtener ventas agrupadas por estado de orden"""
    try:
        query = PREDEFINED_QUERIES["ordenes_por_estado"]
        results = athena_client.execute_query(query)
        
        return QueryResponse(
            success=True,
            data=results,
            rows_count=len(results) if results else 0,
            execution_time_ms=athena_client.last_execution_time_ms
        )
    except Exception as e:
        logger.error(f"Error en ventas_por_estado: {e}")
        return QueryResponse(success=False, error=str(e))


@app.get("/api/productos/top", tags=["Productos"], response_model=QueryResponse)
async def get_top_productos(limit: int = Query(10, ge=1, le=100)):
    """Obtener productos más valiosos por inventario"""
    try:
        query = PREDEFINED_QUERIES["productos_top"].format(limit=limit)
        results = athena_client.execute_query(query)
        
        return QueryResponse(
            success=True,
            data=results,
            rows_count=len(results) if results else 0,
            execution_time_ms=athena_client.last_execution_time_ms
        )
    except Exception as e:
        logger.error(f"Error en productos_top: {e}")
        return QueryResponse(success=False, error=str(e))


# ========== CLIENTES B2B (PostgreSQL) ==========

@app.get("/api/clientes/top", tags=["Clientes B2B"], response_model=QueryResponse)
async def get_top_clientes(limit: int = Query(10, ge=1, le=100)):
    """Obtener top clientes por facturación"""
    try:
        query = PREDEFINED_QUERIES["clientes_top"].format(limit=limit)
        results = athena_client.execute_query(query)
        
        return QueryResponse(
            success=True,
            data=results,
            rows_count=len(results) if results else 0,
            execution_time_ms=athena_client.last_execution_time_ms
        )
    except Exception as e:
        logger.error(f"Error en clientes_top: {e}")
        return QueryResponse(success=False, error=str(e))


@app.get("/api/facturas/estado", tags=["Clientes B2B"], response_model=QueryResponse)
async def get_estado_facturas():
    """Obtener estado de facturas y pagos"""
    try:
        query = PREDEFINED_QUERIES["facturas_estado"]
        results = athena_client.execute_query(query)
        
        return QueryResponse(
            success=True,
            data=results,
            rows_count=len(results) if results else 0,
            execution_time_ms=athena_client.last_execution_time_ms
        )
    except Exception as e:
        logger.error(f"Error en facturas_estado: {e}")
        return QueryResponse(success=False, error=str(e))


# ========== INVENTARIO (MongoDB) ==========

@app.get("/api/inventario/bajo-stock", tags=["Inventario"], response_model=QueryResponse)
async def get_inventario_bajo_stock(threshold: int = Query(100, ge=1)):
    """Obtener productos con stock bajo el umbral especificado"""
    try:
        query = PREDEFINED_QUERIES["inventario_bajo_stock"].format(threshold=threshold)
        results = athena_client.execute_query(query)
        
        return QueryResponse(
            success=True,
            data=results,
            rows_count=len(results) if results else 0,
            execution_time_ms=athena_client.last_execution_time_ms
        )
    except Exception as e:
        logger.error(f"Error en inventario_bajo_stock: {e}")
        return QueryResponse(success=False, error=str(e))


@app.get("/api/envios/estado", tags=["Logística"], response_model=QueryResponse)
async def get_estado_envios():
    """Obtener resumen de estado de envíos"""
    try:
        query = PREDEFINED_QUERIES["envios_estado"]
        results = athena_client.execute_query(query)
        
        return QueryResponse(
            success=True,
            data=results,
            rows_count=len(results) if results else 0,
            execution_time_ms=athena_client.last_execution_time_ms
        )
    except Exception as e:
        logger.error(f"Error en envios_estado: {e}")
        return QueryResponse(success=False, error=str(e))


# ========== DASHBOARD EJECUTIVO ==========

@app.get("/api/dashboard", tags=["Dashboard"], response_model=QueryResponse)
async def get_dashboard():
    """Obtener métricas para dashboard ejecutivo"""
    try:
        query = PREDEFINED_QUERIES["dashboard_ejecutivo"]
        results = athena_client.execute_query(query)
        
        return QueryResponse(
            success=True,
            data=results,
            rows_count=len(results) if results else 0,
            execution_time_ms=athena_client.last_execution_time_ms
        )
    except Exception as e:
        logger.error(f"Error en dashboard: {e}")
        return QueryResponse(success=False, error=str(e))


# ========== QUERY PERSONALIZADA ==========

@app.post("/api/query/custom", tags=["Custom"], response_model=QueryResponse)
async def execute_custom_query(request: CustomQueryRequest):
    """Ejecutar una query SQL personalizada en Athena"""
    try:
        # Validación básica de seguridad
        forbidden_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE", "INSERT", "UPDATE"]
        query_upper = request.query.upper()
        
        for keyword in forbidden_keywords:
            if keyword in query_upper:
                raise HTTPException(
                    status_code=400,
                    detail=f"Keyword '{keyword}' no permitido. Solo queries de lectura (SELECT)"
                )
        
        results = athena_client.execute_query(request.query, request.database)
        
        return QueryResponse(
            success=True,
            data=results,
            rows_count=len(results) if results else 0,
            execution_time_ms=athena_client.last_execution_time_ms
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en custom query: {e}")
        return QueryResponse(success=False, error=str(e))


# ========== LISTAR QUERIES DISPONIBLES ==========

@app.get("/api/queries/list", tags=["Metadata"])
async def list_available_queries():
    """Listar todas las queries predefinidas disponibles"""
    return {
        "total_queries": len(PREDEFINED_QUERIES),
        "queries": list(PREDEFINED_QUERIES.keys())
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)