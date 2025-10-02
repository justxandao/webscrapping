import json
import logging
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
DB_USER = 'docker'
DB_PASSWORD = 'docker'
DB_HOST = 'localhost'
DB_PORT = '5439'
DB_NAME = 'pixtur_dw'
JSON_FILE_PATH = Path(__file__).parent.parent / 'hospedagens.json'

def get_db_engine():
    try:
        db_connection_str = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(db_connection_str)
        engine.connect()
        logging.info("Conexão com o Data Warehouse bem-sucedida!")
        return engine
    except Exception as e:
        logging.critical(f"Não foi possível conectar ao Data Warehouse: {e}")
        return None

def get_or_create_dimension(connection, table_name, key_column, query_params, insert_params):
    valid_query_params = {k: v for k, v in query_params.items() if v is not None}
    where_clause = ' AND '.join([f'{k} = :{k}' for k in valid_query_params.keys()])
    if not where_clause:
        return None
    query = text(f"SELECT {key_column} FROM {table_name} WHERE {where_clause}")
    result = connection.execute(query, valid_query_params).fetchone()
    if result:
        return result[0]
    else:
        insert_query = text(f"INSERT INTO {table_name} ({', '.join(insert_params.keys())}) VALUES ({', '.join([':'+k for k in insert_params.keys()])}) RETURNING {key_column}")
        new_id = connection.execute(insert_query, insert_params).fetchone()[0]
        return new_id

def upsert_fact(connection, params):
    valid_params = {k: (v if v is not None else 0) for k, v in params.items()}
    pk_check_query = text("""
        SELECT 1 FROM Fato_Hospedagem 
        WHERE fk_local = :fk_local AND fk_hotel = :fk_hotel AND fk_tempo = :fk_tempo
    """)
    result = connection.execute(pk_check_query, {'fk_local': valid_params['fk_local'], 'fk_hotel': valid_params['fk_hotel'], 'fk_tempo': valid_params['fk_tempo']}).fetchone()
    if result:
        update_query = text("""
            UPDATE Fato_Hospedagem 
            SET preco_diaria = :preco_diaria, qtd_avaliacoes = :qtd_avaliacoes, nota_media = :nota_media
            WHERE fk_local = :fk_local AND fk_hotel = :fk_hotel AND fk_tempo = :fk_tempo
        """)
        connection.execute(update_query, valid_params)
    else:
        insert_query = text("""
            INSERT INTO Fato_Hospedagem (fk_local, fk_hotel, fk_tempo, preco_diaria, qtd_avaliacoes, nota_media)
            VALUES (:fk_local, :fk_hotel, :fk_tempo, :preco_diaria, :qtd_avaliacoes, :nota_media)
        """)
        connection.execute(insert_query, valid_params)

def parse_localizacao(texto_local: str):
    if not texto_local: return None, None
    partes = [p.strip() for p in texto_local.split(',')]
    return partes[0], partes[1] if len(partes) > 1 else None

def inferir_tipo_hospedagem(nome_anuncio: str):
    if not nome_anuncio: return 'Indefinido'
    nome_lower = nome_anuncio.lower()
    if 'hotel' in nome_lower: return 'Hotel'
    if 'resort' in nome_lower: return 'Resort'
    if 'pousada' in nome_lower or 'hostel' in nome_lower: return 'Pousada'
    return 'Aluguel por temporada'

def main():
    logging.info("Iniciando processo de carga de dados do JSON para o Data Warehouse.")
    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            dados_coletados = json.load(f)
        logging.info(f"Arquivo '{JSON_FILE_PATH.name}' lido com sucesso. {len(dados_coletados)} registros encontrados.")
    except FileNotFoundError:
        logging.critical(f"ERRO: O arquivo '{JSON_FILE_PATH.name}' não foi encontrado. Execute o script de scraping primeiro.")
        return
    except json.JSONDecodeError:
        logging.critical(f"ERRO: O arquivo '{JSON_FILE_PATH.name}' está vazio ou mal formatado.")
        return

    engine = get_db_engine()
    if not engine:
        return

    registros_processados = 0
    with engine.connect() as connection:
        for anuncio in dados_coletados:
            with connection.begin():
                try:
                    if not anuncio.get('nome_anuncio') or not anuncio.get('localizacao'):
                        logging.warning(f"Registro sem nome ou localização. Pulando: {anuncio.get('link', 'Link não disponível')}")
                        continue
                    
                    cidade, estado = parse_localizacao(anuncio['localizacao'])
                    tipo = inferir_tipo_hospedagem(anuncio['nome_anuncio'])

                    fk_local = get_or_create_dimension(connection, 'Dim_Localizacao', 'sk_local',
                                                       {'cidade': cidade, 'estado': estado},
                                                       {'cidade': cidade, 'estado': estado, 'pais': 'Brasil'})
                    
                    fk_hotel = get_or_create_dimension(connection, 'Dim_Hotel', 'sk_hotel',
                                                       {'nome': anuncio['nome_anuncio']},
                                                       {'nome': anuncio['nome_anuncio'], 'tipo': tipo})

                    if not anuncio.get('datas_disponiveis'):
                        logging.warning(f"Nenhuma data disponível para '{anuncio['nome_anuncio']}'.")
                        continue

                    for data_str in anuncio['datas_disponiveis']:
                        data_obj = datetime.strptime(data_str, '%d/%m/%Y').date()
                        
                        fk_tempo = get_or_create_dimension(connection, 'Dim_Tempo', 'sk_tempo',
                                                           {'data_completa': data_obj},
                                                           {'data_completa': data_obj, 'dia': data_obj.day, 'mes': data_obj.month, 'ano': data_obj.year, 
                                                            'trimestre': (data_obj.month - 1) // 3 + 1, 'semestre': 1 if data_obj.month <= 6 else 2})
                        
                        fato_params = {
                            'fk_local': fk_local, 'fk_hotel': fk_hotel, 'fk_tempo': fk_tempo,
                            'preco_diaria': anuncio.get('valor_noite'),
                            'qtd_avaliacoes': anuncio.get('total_avaliacoes'),
                            'nota_media': anuncio.get('nota_media')
                        }
                        upsert_fact(connection, fato_params)
                    
                    registros_processados += 1

                except Exception as e:
                    logging.error(f"Erro ao processar o anúncio '{anuncio.get('nome_anuncio')}': {e}. Rollback será executado para este registro.")
        
        logging.info("Processo finalizado. Commit de todas as transações bem-sucedidas.")

    logging.info(f"\n🎉 Carga de dados concluída! {registros_processados}/{len(dados_coletados)} registros foram processados e salvos no banco.")

if __name__ == "__main__":
    main()