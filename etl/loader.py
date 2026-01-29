import os
import psycopg2
import time
import sys

# configurações do Banco
DB_CONFIG = {
    "dbname": "intuitive_db",
    "user": "user_teste",
    "password": "password_teste",
    "host": "localhost",
    "port": "5432"
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "relatorio_final.csv")

def carregar_dados():
    if not os.path.exists(CSV_FILE):
        print(f"ERRO: Arquivo {CSV_FILE} não encontrado.")
        print("Rode o 'main_etl.py' primeiro!")
        sys.exit(1)

    print("Conectando ao PostgreSQL...")
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("Limpando tabela (TRUNCATE)...")
        cur.execute("TRUNCATE TABLE demonstracoes_contabeis;")
        conn.commit()

        print("Iniciando carga via COPY STREAM (Alta Performance)...")
        start_time = time.time()
        
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            # SQLpara lidar com NULLs se necessário
            sql = "COPY demonstracoes_contabeis FROM stdin WITH CSV HEADER DELIMITER ',' NULL ''"
            cur.copy_expert(sql, f)
            
        conn.commit()
        end_time = time.time()
        
        # estatísticas finais
        duration = end_time - start_time
        cur.execute("SELECT COUNT(*) FROM demonstracoes_contabeis;")
        qtd = cur.fetchone()[0]
        
        print(f"CARGA COMPLETA!")
        print(f"Tempo: {duration:.2f} segundos")
        print(f"Registros: {qtd}")
        print(f"Velocidade: {int(qtd/duration)} linhas/segundo")

    except Exception as e:
        print(f"Erro durante a carga: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    carregar_dados()