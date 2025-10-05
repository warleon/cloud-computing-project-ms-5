"""
Data Ingester - Extrae datos de bases de datos y los sube a S3
Soporta: MySQL, PostgreSQL, MongoDB
"""

import os
import sys
import json
import logging
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Any
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataIngester:
    """Clase para ingestar datos desde bases de datos hacia S3"""

    def __init__(self, db_type: str, bucket_name: str):
        """
        Inicializa el ingester

        Args:
            db_type: Tipo de base de datos (mysql, postgresql, mongodb)
            bucket_name: Nombre del bucket S3 de destino
        """
        self.db_type = db_type.lower()
        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3')

        # Configuración desde variables de entorno
        self.db_host = os.getenv('DB_HOST')
        self.db_port = os.getenv('DB_PORT')
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')
        self.db_name = os.getenv('DB_NAME')

        logger.info(f"Ingester inicializado - Tipo: {self.db_type}, Bucket: {self.bucket_name}")

    def _convert_types(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convierte tipos de datos problemáticos a tipos JSON válidos
        Esto asegura que Glue Crawler infiera los tipos correctamente

        Args:
            data: Lista de registros

        Returns:
            Lista de registros con tipos convertidos
        """
        for row in data:
            for key, value in list(row.items()):
                # Convertir Decimal a float (para números con decimales)
                if isinstance(value, Decimal):
                    row[key] = float(value)
                # Convertir datetime/date a string ISO
                elif isinstance(value, (datetime, date)):
                    row[key] = value.isoformat()
                # Convertir bytes a string
                elif isinstance(value, bytes):
                    try:
                        row[key] = value.decode('utf-8')
                    except:
                        row[key] = str(value)
                # Convertir otros tipos no serializables
                elif hasattr(value, '__dict__') and not isinstance(value, (str, int, float, bool, list, dict)):
                    row[key] = str(value)

        return data

    def connect_database(self):
        """Establece conexión con la base de datos según el tipo"""
        try:
            if self.db_type == 'mysql':
                import pymysql
                self.connection = pymysql.connect(
                    host=self.db_host,
                    port=int(self.db_port or 3306),
                    user=self.db_user,
                    password=self.db_password,
                    database=self.db_name,
                    cursorclass=pymysql.cursors.DictCursor
                )
                logger.info("Conectado a MySQL exitosamente")

            elif self.db_type == 'postgresql':
                import psycopg2
                import psycopg2.extras
                self.connection = psycopg2.connect(
                    host=self.db_host,
                    port=int(self.db_port or 5432),
                    user=self.db_user,
                    password=self.db_password,
                    database=self.db_name
                )
                logger.info("Conectado a PostgreSQL exitosamente")

            elif self.db_type == 'mongodb':
                from pymongo import MongoClient
                connection_string = f"mongodb://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port or 27017}"
                self.connection = MongoClient(connection_string)
                self.db = self.connection[self.db_name]
                logger.info("Conectado a MongoDB exitosamente")

            else:
                raise ValueError(f"Tipo de base de datos no soportado: {self.db_type}")

        except Exception as e:
            logger.error(f"Error al conectar a la base de datos: {e}")
            raise

    def extract_data(self, table_name: str, query: str = None) -> List[Dict[str, Any]]:
        """
        Extrae datos de una tabla o colección

        Args:
            table_name: Nombre de la tabla/colección
            query: Query personalizado (opcional)

        Returns:
            Lista de registros
        """
        try:
            if self.db_type in ['mysql', 'postgresql']:
                with self.connection.cursor() as cursor:
                    if query:
                        cursor.execute(query)
                    else:
                        cursor.execute(f"SELECT * FROM {table_name}")

                    if self.db_type == 'mysql':
                        data = cursor.fetchall()
                    else:  # PostgreSQL
                        import psycopg2.extras
                        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                        if query:
                            cursor.execute(query)
                        else:
                            cursor.execute(f"SELECT * FROM {table_name}")
                        data = cursor.fetchall()
                        data = [dict(row) for row in data]

                    # Convertir tipos problemáticos a tipos JSON válidos
                    data = self._convert_types(data)

                logger.info(f"Extraídos {len(data)} registros de {table_name}")
                return data

            elif self.db_type == 'mongodb':
                collection = self.db[table_name]
                data = list(collection.find())

                # Convertir ObjectId a string
                for record in data:
                    if '_id' in record:
                        record['_id'] = str(record['_id'])

                # Convertir tipos problemáticos
                data = self._convert_types(data)

                logger.info(f"Extraídos {len(data)} documentos de {table_name}")
                return data

        except Exception as e:
            logger.error(f"Error al extraer datos de {table_name}: {e}")
            raise

    def upload_to_s3(self, data: List[Dict[str, Any]], table_name: str):
        """
        Sube los datos a S3 en formato JSON Lines con particionamiento por fecha

        Args:
            data: Datos a subir
            table_name: Nombre de la tabla/colección (para el path en S3)
        """
        try:
            # Crear estructura de particionamiento
            now = datetime.now()
            year = now.strftime('%Y')
            month = now.strftime('%m')
            day = now.strftime('%d')
            timestamp = now.strftime('%Y%m%d_%H%M%S')

            # Construir la ruta en S3
            s3_key = f"{table_name}/year={year}/month={month}/day={day}/{table_name}_{timestamp}.json"

            # Convertir datos a JSON Lines (un objeto por línea)
            json_lines = '\n'.join([json.dumps(record, default=str) for record in data])

            # Subir a S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json_lines,
                ContentType='application/x-ndjson'
            )

            logger.info(f"Datos subidos exitosamente a s3://{self.bucket_name}/{s3_key}")
            logger.info(f"Total de registros: {len(data)}")

        except ClientError as e:
            logger.error(f"Error al subir datos a S3: {e}")
            raise

    def ingest_table(self, table_name: str, query: str = None):
        """
        Proceso completo de ingesta: extrae y sube a S3

        Args:
            table_name: Nombre de la tabla/colección
            query: Query personalizado (opcional)
        """
        logger.info(f"Iniciando ingesta de {table_name}")

        # Extraer datos
        data = self.extract_data(table_name, query)

        if not data:
            logger.warning(f"No se encontraron datos en {table_name}")
            return

        # Subir a S3
        self.upload_to_s3(data, table_name)

        logger.info(f"Ingesta completada para {table_name}")

    def close(self):
        """Cierra la conexión a la base de datos"""
        try:
            if self.connection:
                self.connection.close()
                logger.info("Conexión a la base de datos cerrada")
        except Exception as e:
            logger.error(f"Error al cerrar conexión: {e}")


def main():
    """Función principal"""
    # Leer configuración desde variables de entorno
    db_type = os.getenv('DB_TYPE')  # mysql, postgresql, mongodb
    bucket_name = os.getenv('S3_BUCKET')
    tables = os.getenv('TABLES', '').split(',')  # Lista de tablas separadas por coma

    if not db_type or not bucket_name:
        logger.error("DB_TYPE y S3_BUCKET son requeridos")
        sys.exit(1)

    if not tables or tables == ['']:
        logger.error("TABLES es requerido (separadas por coma)")
        sys.exit(1)

    # Crear ingester
    ingester = DataIngester(db_type, bucket_name)

    try:
        # Conectar a la base de datos
        ingester.connect_database()

        # Ingestar cada tabla
        for table in tables:
            table = table.strip()
            if table:
                ingester.ingest_table(table)

        logger.info("Proceso de ingesta completado exitosamente")

    except Exception as e:
        logger.error(f"Error en el proceso de ingesta: {e}")
        sys.exit(1)

    finally:
        ingester.close()


if __name__ == "__main__":
    main()