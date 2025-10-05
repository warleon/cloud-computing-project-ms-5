"""
Cliente para ejecutar queries en Amazon Athena
"""

import boto3
import time
import logging
import os
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class AthenaClient:
    """Cliente para interactuar con Amazon Athena"""
    
    def __init__(self, region_name: str = None):
        """
        Inicializa el cliente de Athena
        
        Args:
            region_name: Región de AWS (opcional, usa variable de entorno)
        """
        region = region_name or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.athena = boto3.client('athena', region_name=region)
        self.s3 = boto3.client('s3', region_name=region)
        self.database = os.getenv("ATHENA_DATABASE", "datalake_raw")
        self.output_location = os.getenv("ATHENA_OUTPUT_LOCATION", "s3://raw-ms1-data-bgc/athena-results/")
        self.workgroup = os.getenv("ATHENA_WORKGROUP", "primary")
        self.last_execution_time_ms = 0
        
        logger.info(f"AthenaClient inicializado - Database: {self.database}, Region: {region}")
    
    def execute_query(self, query: str, database: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Ejecuta una query en Athena y devuelve los resultados
        
        Args:
            query: Query SQL a ejecutar
            database: Base de datos (opcional, usa self.database por defecto)
            
        Returns:
            Lista de diccionarios con los resultados
        """
        start_time = time.time()
        db = database or self.database
        
        try:
            logger.info(f"Ejecutando query en Athena: {query[:100]}...")
            
            # Iniciar ejecución de query
            response = self.athena.start_query_execution(
                QueryString=query,
                QueryExecutionContext={'Database': db},
                ResultConfiguration={'OutputLocation': self.output_location}
            )
            
            query_execution_id = response['QueryExecutionId']
            logger.info(f"Query ID: {query_execution_id}")
            
            # Esperar a que la query termine
            self._wait_for_query_completion(query_execution_id)
            
            # Obtener resultados
            results = self._get_query_results(query_execution_id)
            
            execution_time = int((time.time() - start_time) * 1000)
            self.last_execution_time_ms = execution_time
            
            logger.info(f"Query completada en {execution_time}ms - {len(results)} filas")
            
            return results
            
        except Exception as e:
            logger.error(f"Error ejecutando query: {e}")
            raise
    
    def _wait_for_query_completion(self, query_execution_id: str, max_wait_time: int = 60):
        """
        Espera a que la query termine de ejecutarse
        
        Args:
            query_execution_id: ID de la ejecución de la query
            max_wait_time: Tiempo máximo de espera en segundos
        """
        start_time = time.time()
        
        while True:
            response = self.athena.get_query_execution(QueryExecutionId=query_execution_id)
            status = response['QueryExecution']['Status']['State']
            
            if status in ['SUCCEEDED']:
                logger.info(f"Query {query_execution_id} completada exitosamente")
                return
            
            if status in ['FAILED', 'CANCELLED']:
                reason = response['QueryExecution']['Status'].get('StateChangeReason', 'Unknown')
                raise Exception(f"Query failed: {reason}")
            
            # Verificar timeout
            elapsed_time = time.time() - start_time
            if elapsed_time > max_wait_time:
                raise Exception(f"Query timeout after {max_wait_time} seconds")
            
            # Esperar antes de verificar nuevamente
            time.sleep(0.5)
    
    def _get_query_results(self, query_execution_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene los resultados de una query ejecutada
        
        Args:
            query_execution_id: ID de la ejecución de la query
            
        Returns:
            Lista de diccionarios con los resultados
        """
        results = []
        next_token = None
        
        while True:
            params = {'QueryExecutionId': query_execution_id, 'MaxResults': 1000}
            if next_token:
                params['NextToken'] = next_token
            
            response = self.athena.get_query_results(**params)
            
            # Obtener nombres de columnas (primera fila)
            if not results:
                column_names = [col['Name'] for col in response['ResultSet']['ResultSetMetadata']['ColumnInfo']]
            
            # Procesar filas (saltando la primera que es el header)
            rows = response['ResultSet']['Rows'][1:] if not next_token else response['ResultSet']['Rows']
            
            for row in rows:
                values = [field.get('VarCharValue', None) for field in row['Data']]
                results.append(dict(zip(column_names, values)))
            
            # Verificar si hay más resultados
            next_token = response.get('NextToken')
            if not next_token:
                break
        
        return results