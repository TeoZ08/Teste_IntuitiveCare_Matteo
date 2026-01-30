import os
import psycopg2
import time
import pandas as pd

DB_CONFIG = {
    "dbname": "intuitive_db",
    "user": "user_teste",
    "password": "password_teste",
    "host": "localhost",
    "port": "5432"
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_DEMONSTRACOES = os.path.join(BASE_DIR, "demonstracoes_contabeis.csv")
FILE_OPERADORAS = os.path.join(BASE_DIR, "operadoras.csv")

def carregar_csv(cursor, file_path, table_name, columns=None):
    if not os.path.exists(file_path):
        print(f"Arquivo nao encontrado: {file_path}")
        return

    print(f"Carregando {table_name}...")
    start = time.time()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        cols_sql = f"({','.join(columns)})" if columns else ""
        sql = f"COPY {table_name} {cols_sql} FROM stdin WITH CSV HEADER DELIMITER ',' NULL ''"
        cursor.copy_expert(sql, f)
        
    print(f"Tabela {table_name} carregada em {time.time() - start:.2f}s")

def carregar_dados():
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("Limpando dados antigos...")
        cur.execute("TRUNCATE TABLE demonstracoes_contabeis, operadoras RESTART IDENTITY;")
        conn.commit()

        # carrega operadoras (lendo colunas do csv para garantir ordem)
        if os.path.exists(FILE_OPERADORAS):
            df_op = pd.read_csv(FILE_OPERADORAS, nrows=0)
            carregar_csv(cur, FILE_OPERADORAS, "operadoras", list(df_op.columns))

        # carrega demonstracoes
        carregar_csv(cur, FILE_DEMONSTRACOES, "demonstracoes_contabeis")

        conn.commit()
        print("Carga finalizada com sucesso.")

    except Exception as e:
        print(f"Erro critico: {e}")
        if conn: conn.rollback()
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    carregar_dados()