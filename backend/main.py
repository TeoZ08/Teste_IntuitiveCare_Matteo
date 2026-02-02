from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional
from datetime import date

app = FastAPI(title="API IntuitiveCare", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuracao do banco
DB_CONFIG = {
    "dbname": "intuitive_db",
    "user": "user_teste",
    "password": "password_teste",
    "host": "localhost",
    "port": "5432"
}

def get_db_connection():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Erro de conexao DB: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no banco de dados")

@app.get("/")
def read_root():
    return {"status": "online", "docs_url": "/docs"}

# Rota 1: Listar Operadoras
@app.get("/api/operadoras")
def listar_operadoras(page: int = 1, limit: int = 10, search: Optional[str] = None):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    offset = (page - 1) * limit
    
    try:
        where_clause = ""
        params = []
        
        if search:
            where_clause = "WHERE razao_social ILIKE %s OR cnpj ILIKE %s"
            term = f"%{search}%"
            params = [term, term]
            
        # Busca dados
        query = f"""
            SELECT reg_ans, cnpj, razao_social, uf, modalidade 
            FROM operadoras 
            {where_clause}
            ORDER BY razao_social 
            LIMIT %s OFFSET %s
        """
        cur.execute(query, params + [limit, offset])
        results = cur.fetchall()
        
        # Busca total
        count_query = f"SELECT COUNT(*) as total FROM operadoras {where_clause}"
        cur.execute(count_query, params)
        total_row = cur.fetchone()
        total = total_row['total'] if total_row else 0
        
        return {
            "data": results,
            "meta": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": -(-total // limit)
            }
        }
    finally:
        cur.close()
        conn.close()

# Rota 2: Detalhes da Operadora
@app.get("/api/operadoras/{identificador}")
def detalhes_operadora(identificador: str):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT * FROM operadoras 
            WHERE reg_ans = %s OR cnpj = %s
        """, (identificador, identificador))
        
        operadora = cur.fetchone()
        if not operadora:
            raise HTTPException(status_code=404, detail="Operadora nao encontrada")
            
        return operadora
    finally:
        cur.close()
        conn.close()

# Rota 3: Histórico de Despesas
@app.get("/api/operadoras/{identificador}/despesas")
def historico_despesas(identificador: str):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # 1. Identifica a operadora
        cur.execute("SELECT reg_ans FROM operadoras WHERE reg_ans = %s OR cnpj = %s", (identificador, identificador))
        op = cur.fetchone()
        
        if not op:
            raise HTTPException(status_code=404, detail="Operadora nao encontrada")
            
        # 2. Busca despesas
        cur.execute("""
            SELECT 
                data_referencia,
                SUM(vl_saldo_final) as valor_total
            FROM demonstracoes_contabeis
            WHERE reg_ans = %s AND cd_conta_contabil LIKE '4%%'
            GROUP BY data_referencia
            ORDER BY data_referencia
        """, (op['reg_ans'],))
        
        resultados = cur.fetchall()
        
        # 3. Tratamento manual dos dados (Decimal -> float, Date -> str)
        dados_formatados = []
        for row in resultados:
            dados_formatados.append({
                "data_referencia": str(row['data_referencia']),
                "valor_total": float(row['valor_total']) if row['valor_total'] else 0.0
            })
            
        return dados_formatados
        
    except Exception as e:
        print(f"Erro na Rota Despesas: {e}") # Log no terminal
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

# Rota 4: Estatísticas Gerais
@app.get("/api/estatisticas")
def estatisticas_gerais():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Top 5
        cur.execute("""
            SELECT op.razao_social, op.uf, SUM(dc.vl_saldo_final) as total
            FROM demonstracoes_contabeis dc
            JOIN operadoras op ON dc.reg_ans = op.reg_ans
            WHERE dc.cd_conta_contabil LIKE '4%%' 
            AND dc.data_referencia = (SELECT MAX(data_referencia) FROM demonstracoes_contabeis)
            GROUP BY op.razao_social, op.uf
            ORDER BY total DESC
            LIMIT 5
        """)
        top5 = cur.fetchall()
        
        # Por UF
        cur.execute("""
            SELECT op.uf, SUM(dc.vl_saldo_final) as total
            FROM demonstracoes_contabeis dc
            JOIN operadoras op ON dc.reg_ans = op.reg_ans
            WHERE dc.cd_conta_contabil LIKE '4%%'
            GROUP BY op.uf
            ORDER BY total DESC
        """)
        ufs = cur.fetchall()

        # Total Geral
        cur.execute("""
            SELECT SUM(vl_saldo_final) as total 
            FROM demonstracoes_contabeis 
            WHERE cd_conta_contabil LIKE '4%%'
        """)
        row = cur.fetchone()
        total_geral = row['total'] if row and row['total'] else 0

        return {
            "top_5": top5,
            "por_uf": ufs,
            "total_despesas_periodo": total_geral
        }
    finally:
        cur.close()
        conn.close()