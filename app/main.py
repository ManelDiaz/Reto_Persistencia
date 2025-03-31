
from utils.database import conectar_db, importar_csv_db

def main():
    conexion = conectar_db()
    
    direcion_csv = "../datos_turbina/T1.csv"
    importar_csv_db(conexion, direcion_csv)

if __name__ == "__main__":
    main()