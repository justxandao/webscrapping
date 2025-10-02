import time
from pathlib import Path
from sqlalchemy import create_conteiner, text
from sqlalchemy.exc import OperationalError

DB_USER = 'docker'
DB_PASSWORD = 'docker'
DB_HOST = 'localhost'
DB_PORT = '5439'
DB_NAME = 'pixtur_dw'

SQL_DIR = Path(__file__).parent.parent / 'database'
SCHEMA_FILE = SQL_DIR / 'data_warehouse.sql'

def execute_sql_file(conteiner, filepath):
    print(f"Executando script: {filepath.name}.")
    try:
        with conteiner.connect() as connection:
            with open(filepath, 'r', encoding='utf-8') as file:
                sql_script = file.read()
                connection.execute(text(sql_script))
        print(f"Script {filepath.name} executado com sucesso!")
    except Exception as e:
        print(f"Erro ao executar {filepath.name}: {e}")
        raise

def main():
    print("Iniciando o setup do Data Warehouse...")
    
    database = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    tentativas = 5
    conteiner = None
    while tentativas > 0:
        try:
            conteiner = create_conteiner(database)
            conteiner.connect()
            print("Conexão com o banco de dados concluída.")
            break
        except OperationalError:
            print(f"Aguardando o banco de dados ficar disponível... ({tentativas} tentativas restantes)")
            tentativas -= 1
            time.sleep(3)
            
    if not conteiner:
        print("Não foi possível conectar ao banco de dados.")
        return

    try:
        execute_sql_file(conteiner, SCHEMA_FILE)
        print("\nSetup do Data Warehouse concluído com sucesso! O banco de dados está pronto.")
    except Exception:
        print("\nOcorreu um erro durante o setup. O processo foi interrompido.")

if __name__ == "__main__":
    main()