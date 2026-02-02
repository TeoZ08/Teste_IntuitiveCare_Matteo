from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional

app = FastAPI(title="API IntuitiveCare", version="1.0.0")

# habilitar cors para permitir requisicoes do frontend vue.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# configuracao do banco
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
        print(f"erro de conexao: {e}")
        raise HTTPException(status_code=500, detail="erro interno no banco de dados")

@app.get("/")
def read_root():
    return {"status": "online", "docs_url": "/docs"}

# rota 1: listar operadoras (paginada)
@app.get("/api/operadoras")
def listar_operadoras(page: int = 1, limit: int = 10, search: Optional[str] = None):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    offset = (page - 1) * limit
    
    try:
        # constroi query dinamica para busca
        where_clause = ""
        params = []
        
        if search:
            # busca por razao social ou cnpj
            where_clause = "WHERE razao_social ILIKE %s OR cnpj ILIKE %s"
            term = f"%{search}%"
            params = [term, term]
            
        # query de dados
        query = f"""
            SELECT reg_ans, cnpj, razao_social, uf, modalidade 
            FROM operadoras 
            {where_clause}
            ORDER BY razao_social 
            LIMIT %s OFFSET %s
        """
        cur.execute(query, params + [limit, offset])
        results = cur.fetchall()
        
        # query de contagem total (para paginacao)
        count_query = f"SELECT COUNT(*) as total FROM operadoras {where_clause}"
        cur.execute(count_query, params)
        total = cur.fetchone()['total']
        
        return {
            "data": results,
            "meta": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": -(-total // limit) # divisao arredondada pra cima
            }
        }
    finally:
        cur.close()
        conn.close()

# rota 2: detalhes da operadora (busca por reg_ans ou cnpj)
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
            raise HTTPException(status_code=404, detail="operadora nao encontrada")
            
        return operadora
    finally:
        cur.close()
        conn.close()

# rota 3: historico de despesas
@app.get("/api/operadoras/{identificador}/despesas")
def historico_despesas(identificador: str):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # primeiro identifica a operadora
        cur.execute("SELECT reg_ans FROM operadoras WHERE reg_ans = %s OR cnpj = %s", (identificador, identificador))
        op = cur.fetchone()
        
        if not op:
            raise HTTPException(status_code=404, detail="operadora nao encontrada")
            
        # busca despesas agregadas por data
        cur.execute("""
            SELECT 
                data_referencia,
                SUM(vl_saldo_final) as valor_total
            FROM demonstracoes_contabeis
            WHERE reg_ans = %s AND cd_conta_contabil LIKE '4%'
            GROUP BY data_referencia
            ORDER BY data_referencia
        """, (op['reg_ans'],))
        
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

# rota 4: estatisticas gerais
@app.get("/api/estatisticas")
def estatisticas_gerais():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # 1. top 5 operadoras (ultimo periodo)
        cur.execute("""
            SELECT op.razao_social, op.uf, SUM(dc.vl_saldo_final) as total
            FROM demonstracoes_contabeis dc
            JOIN operadoras op ON dc.reg_ans = op.reg_ans
            WHERE dc.cd_conta_contabil LIKE '4%' 
            AND dc.data_referencia = (SELECT MAX(data_referencia) FROM demonstracoes_contabeis)
            GROUP BY op.razao_social, op.uf
            ORDER BY total DESC
            LIMIT 5
        """)
        top5 = cur.fetchall()
        
        # 2. distribuicao por UF
        cur.execute("""
            SELECT op.uf, SUM(dc.vl_saldo_final) as total
            FROM demonstracoes_contabeis dc
            JOIN operadoras op ON dc.reg_ans = op.reg_ans
            WHERE dc.cd_conta_contabil LIKE '4%'
            GROUP BY op.uf
            ORDER BY total DESC
        """)
        ufs = cur.fetchall()

        cur.execute("""
            SELECT SUM(vl_saldo_final) as total 
            FROM demonstracoes_contabeis 
            WHERE cd_conta_contabil LIKE '4%'
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