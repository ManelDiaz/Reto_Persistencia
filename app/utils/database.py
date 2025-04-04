import pandas as pd
import psycopg2
from datetime import datetime, timedelta
import logging
import os
import sys
import time
from pathlib import Path

# Añadimos el directorio principal a sys.path para importar correctamente
sys.path.append(str(Path(__file__).parent.parent))
from models.turbina import Turbina

# Configuración de logs
LOG_DIR = 'logs'
LOG_FILE = os.path.join(LOG_DIR, 'turbine_import.log')
os.makedirs(LOG_DIR, exist_ok=True)

# Configurar el manejador de archivo
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.INFO)

# Configurar el manejador de consola
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)

# Formateo de logs
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Configurar el logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def conectar_db(max_intentos=5, espera_segundos=3):
    """
    Establece conexión con la base de datos PostgreSQL con reintentos.
    
    Args:
        max_intentos: Número máximo de intentos de conexión
        espera_segundos: Tiempo de espera entre intentos
        
    Returns:
        Conexión a la base de datos PostgreSQL
    """
    intento = 1
    ultima_excepcion = None
    
    while intento <= max_intentos:
        try:
            logger.info(f"Intento de conexión a la base de datos {intento}/{max_intentos}")
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
            ultima_excepcion = e
            logger.warning(f"Error al conectar con la base de datos (intento {intento}): {e}")
            if intento < max_intentos:
                logger.info(f"Reintentando en {espera_segundos} segundos...")
                time.sleep(espera_segundos)
            intento += 1
    
    # Si llegamos aquí, todos los intentos fallaron
    logger.error(f"Error al conectar con la base de datos después de {max_intentos} intentos: {ultima_excepcion}")
    raise ultima_excepcion

def importar_csv_db(conexion, ruta_csv, batch_size=100):
    """
    Lee un archivo CSV y lo inserta en la base de datos usando transacciones por lotes.
    
    Args:
        conexion: Conexión a la base de datos PostgreSQL
        ruta_csv: Ruta al archivo CSV a importar
        batch_size: Tamaño de cada lote para transacciones (por defecto 100)
        
    Returns:
        dict: Resumen de la operación con contadores de registros
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
        required_columns = ['Date/Time', 'LV ActivePower (kW)', 'Wind Speed (m/s)', 'Theoretical_Power_Curve (KWh)', 'Wind Direction (°)']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"El archivo CSV no contiene las columnas: {', '.join(missing_columns)}")
            raise ValueError(f"El archivo CSV debe contener las columnas: {', '.join(required_columns)}")
        
        # Mapeo de columnas del CSV a nombres usados en el modelo
        column_mapping = {
            'Date/Time': 'timestamp',
            'LV ActivePower (kW)': 'lv_active_power_kw',
            'Wind Speed (m/s)': 'wind_speed_ms',
            'Theoretical_Power_Curve (KWh)': 'theoretical_power_curve_kwh',
            'Wind Direction (°)': 'wind_direction_deg'
        }
        
        # Renombrar columnas para facilitar el procesamiento
        df = df.rename(columns=column_mapping)
        
        # Contadores para el resumen
        total_records = len(df)
        valid_records = 0
        invalid_records = 0
        
        # Actualizamos todos los timestamps a la fecha y hora actual
        current_time = datetime.now()
        
        # Procesar por lotes para manejar mejor las transacciones
        for batch_start in range(0, len(df), batch_size):
            batch_end = min(batch_start + batch_size, len(df))
            batch_df = df.iloc[batch_start:batch_end]
            
            # Crear un cursor nuevo para cada lote
            cursor = conexion.cursor()
            
            try:
                # Insertamos los datos del lote actual
                for index, row in batch_df.iterrows():
                    try:
                        # Crear un timestamp único para cada fila
                        unique_timestamp = current_time + timedelta(microseconds=index)
                        
                        # Insertar registro
                        insert_query = """
                        INSERT INTO turbina (timestamp, lv_active_power_kw, wind_speed_ms, theoretical_power_curve_kwh, wind_direction_deg)
                        VALUES (%s, %s, %s, %s, %s)
                        """
                        cursor.execute(
                            insert_query, 
                            (
                                unique_timestamp,
                                float(row['lv_active_power_kw']),
                                float(row['wind_speed_ms']),
                                float(row['theoretical_power_curve_kwh']),
                                float(row['wind_direction_deg'])
                            )
                        )
                        valid_records += 1
                    except Exception as row_error:
                        # Registrar error pero continuar con el siguiente registro
                        invalid_records += 1
                        logger.error(f"Error al insertar registro {index}: {row_error}")
                
                # Confirmar la transacción del lote actual
                conexion.commit()
                logger.info(f"Lote {batch_start//batch_size + 1}: {valid_records - invalid_records} registros insertados")
                
            except Exception as batch_error:
                # Si hay error en el lote, hacer rollback y registrar
                conexion.rollback()
                logger.error(f"Error en lote {batch_start//batch_size + 1}: {batch_error}")
                invalid_records += len(batch_df)
            finally:
                # Cerrar el cursor del lote
                cursor.close()
        
        logger.info(f"Se importaron {valid_records} registros a la base de datos")
        
        # Devuelve un diccionario con el resumen
        return {
            "total": total_records,
            "valid": valid_records,
            "invalid": invalid_records
        }
        
    except Exception as e:
        logger.error(f"Error al importar datos del CSV a la base de datos: {e}")
        if cursor and not cursor.closed:
            cursor.close()
        # Devuelve un diccionario con error para evitar que falle el main
        return {
            "total": total_records if 'total_records' in locals() else 0,
            "valid": valid_records if 'valid_records' in locals() else 0,
            "invalid": invalid_records if 'invalid_records' in locals() else 0,
            "error": str(e)
        }

def consultar_datos(conexion, limite=100):
    """
    Consulta los datos más recientes de la tabla turbinas.
    
    Args:
        conexion: Conexión a la base de datos PostgreSQL
        limite: Número máximo de registros a devolver
        
    Returns:
        list: Lista de diccionarios con los datos consultados
    """
    cursor = None
    try:
        cursor = conexion.cursor()
        query = """
        SELECT timestamp, lv_active_power_kw, wind_speed_ms, 
               theoretical_power_curve_kwh, wind_direction_deg
        FROM turbina
        ORDER BY timestamp DESC
        LIMIT %s
        """
        cursor.execute(query, (limite,))
        
        # Obtener nombres de columnas
        column_names = [desc[0] for desc in cursor.description]
        
        # Convertir resultados a lista de diccionarios
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(column_names, row)))
            
        return results
        
    except Exception as e:
        logger.error(f"Error al consultar datos: {e}")
        raise
    finally:
        if cursor and not cursor.closed:
            cursor.close()