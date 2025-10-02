import time
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

DB_USER = 'docker'
DB_PASSWORD = 'docker'
DB_HOST = 'localhost'
DB_PORT = '5439'
DB_NAME = 'pixtur_dw'

SQL_DIR = Path(__file__).parent.parent / 'database'
SCHEMA_FILE = SQL_DIR / 'data_warehouse.sql'
# INSERT_FILE = SQL_DIR / 'insert_data.sql'

def execute_sql_file(engine, filepath):
    print(f"Executando script: {filepath.name}...")
    try:
        with engine.connect() as connection:
            with open(filepath, 'r', encoding='utf-8') as file:
                sql_script = file.read()
                connection.execute(text(sql_script))
        print(f"✅ Script {filepath.name} executado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao executar {filepath.name}: {e}")
        raise

def main():
    print("Iniciando o setup do Data Warehouse...")
    
    db_connection_str = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    retries = 5
    engine = None
    while retries > 0:
        try:
            engine = create_engine(db_connection_str)
            engine.connect()
            print("🚀 Conexão com o banco de dados bem-sucedida!")
            break
        except OperationalError:
            print(f"Aguardando o banco de dados ficar disponível... ({retries} tentativas restantes)")
            retries -= 1
            time.sleep(3)
            
    if not engine:
        print("❌ Não foi possível conectar ao banco de dados. Verifique se o contêiner Docker está no ar.")
        return

    try:
        execute_sql_file(engine, SCHEMA_FILE)
        # execute_sql_file(engine, INSERT_FILE)
        print("\n🎉 Setup do Data Warehouse concluído com sucesso! O banco de dados está pronto.")
    except Exception:
        print("\n🔥 Ocorreu um erro durante o setup. O processo foi interrompido.")

if __name__ == "__main__":
    main()