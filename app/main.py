import logging
from utils.database import conectar_db, importar_csv_db

def configurar_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

def main():
    logger = configurar_logging()
    logger.info("Iniciando proceso de importación")
    
    conexion = conectar_db()
    logger.info("Conexión a la base de datos establecida")
    
    direcion_csv = "/data/T1.csv"
    logger.info(f"Importando archivo CSV desde: {direcion_csv}")
    
    resultado = importar_csv_db(conexion, direcion_csv)
    
    logger.info("=== Resumen de importación ===")
    logger.info(f"Total de registros procesados: {resultado['total']}")
    logger.info(f"Registros válidos insertados: {resultado['valid']}")
    logger.info(f"Registros con errores: {resultado['invalid']}")
    logger.info("==============================")
    
    conexion.close()
    logger.info("Conexión a la base de datos cerrada")

if __name__ == "__main__":
    main()