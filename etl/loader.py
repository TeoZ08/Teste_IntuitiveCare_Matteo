import os
import psycopg2
import time

# Configurações do Banco (iguais ao docker-compose)
DB_CONFIG = {
    "dbname": "intuitive_db",
    "user": "user_teste",
    "password": "password_teste",
    "host": "localhost",
    "port": "5432"
}

# Define o caminho do arquivo CSV (mesma pasta do script)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "relatorio_final.csv")

def carregar_dados():
    print("Conectando ao PostgreSQL...")
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 1. Limpar a tabela antes de carregar (Idempotência)
        print("Limpando dados antigos (TRUNCATE)...")
        cur.execute("TRUNCATE TABLE demonstracoes_contabeis;")
        conn.commit()

        # 2. Carregar os dados usando COPY (Alta performance)
        print("Iniciando cópia rápida (COPY)...")
        start_time = time.time()
        
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            # COPY ... FROM stdin informa que vamos mandar o arquivo direto pelo stream
            # HEADER: Pula a primeira linha (cabeçalho)
            # DELIMITER: Avisa que o separador é vírgula
            sql = "COPY demonstracoes_contabeis FROM stdin WITH CSV HEADER DELIMITER ','"
            cur.copy_expert(sql, f)
            
        conn.commit()
        end_time = time.time()
        
        print(f"Sucesso! Dados carregados em {end_time - start_time:.2f} segundos.")
        
        # 3. Verificação final
        cur.execute("SELECT COUNT(*) FROM demonstracoes_contabeis;")
        qtd = cur.fetchone()[0]
        print(f"Total de linhas no banco: {qtd}")

    except Exception as e:
        print(f"Erro crítico ao carregar dados: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    carregar_dados()
