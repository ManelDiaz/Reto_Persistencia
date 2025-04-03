import pandas as pd
import psycopg2
from datetime import datetime
import logging
import os

LOG_DIR = 'logs'
LOG_FILE = os.path.join(LOG_DIR, 'turbine_import.log')
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def conectar_db():
    """Establece conexión con la base de datos PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host="db",  # Nombre del servicio en docker-compose
            database="turbina_db",
            user="postgres",
            password="postgres",
            port="5432"
        )
        logger.info("Conexión establecida con la base de datos")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Error al conectar con la base de datos: {e}")
        raise

def importar_csv_db(conexion, ruta_csv):
    """
    Lee un archivo CSV, actualiza todos los timestamps a la fecha y hora actual,
    y los inserta en la base de datos PostgreSQL.
    
    Args:
        conexion: Conexión a la base de datos PostgreSQL
        ruta_csv: Ruta al archivo CSV a importar
    """
    cursor = None
    try:
        # Verificamos si el archivo existe
        if not os.path.exists(ruta_csv):
            logger.error(f"El archivo {ruta_csv} no existe")
            raise FileNotFoundError(f"El archivo {ruta_csv} no existe")
            
        # Leemos el archivo CSV con pandas
        df = pd.read_csv(ruta_csv)
        
        # Verificamos las columnas requeridas
        required_columns = ['lv_active_power_kw', 'wind_speed_ms', 'theoretical_power_curve_kwh', 'wind_direction_deg']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"El archivo CSV no contiene las columnas: {', '.join(missing_columns)}")
            raise ValueError(f"El archivo CSV debe contener las columnas: {', '.join(required_columns)}")
        
        # Actualizamos todos los timestamps a la fecha y hora actual
        current_time = datetime.now()
        
        # Preparamos la consulta SQL
        cursor = conexion.cursor()
        
        # Insertamos los datos en la tabla
        for index, row in df.iterrows():
            insert_query = """
            INSERT INTO turbinas (timestamp, lv_active_power_kw, wind_speed_ms, theoretical_power_curve_kwh, wind_direction_deg)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(
                insert_query, 
                (
                    current_time,
                    float(row['lv_active_power_kw']),
                    float(row['wind_speed_ms']),
                    float(row['theoretical_power_curve_kwh']),
                    float(row['wind_direction_deg'])
                )
            )
        
        # Confirmamos los cambios y cerramos el cursor
        conexion.commit()
        cursor.close()
        
        logger.info(f"Se importaron {len(df)} registros a la base de datos")
        return True
        
    except Exception as e:
        logger.error(f"Error al importar datos del CSV a la base de datos: {e}")
        if conexion and not conexion.closed:
            conexion.rollback()
        if cursor and not cursor.closed:
            cursor.close()
        raise