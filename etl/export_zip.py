import pandas as pd
import zipfile
import os
from sqlalchemy import create_engine, text

# MUDANÇA 1: Adicionei '+psycopg2' para garantir que ele use o driver correto
DB_URI = "postgresql+psycopg2://user_teste:password_teste@localhost:5432/intuitive_db"

def exportar_consolidado():
    print("Conectando ao banco para exportar dados...")
    
    engine = create_engine(DB_URI)
    
    query = """
        SELECT 
            op.cnpj as "CNPJ",
            op.razao_social as "RazaoSocial",
            EXTRACT(QUARTER FROM dc.data_referencia) as "Trimestre",
            EXTRACT(YEAR FROM dc.data_referencia) as "Ano",
            dc.vl_saldo_final as "Valor Despesas"
        FROM demonstracoes_contabeis dc
        JOIN operadoras op ON dc.reg_ans = op.reg_ans
        WHERE dc.cd_conta_contabil LIKE '4%%'
    """
    # Note: Usei %% duplo no LIKE acima para o Python não confundir
    
    try:
        # MUDANÇA 2: Usar 'connection' dentro de um contexto (with)
        # Isso resolve o erro "immutabledict is not a sequence"
        with engine.connect() as connection:
            # O Pandas lê usando a conexão aberta
            df = pd.read_sql(text(query), connection)
            
        print(f"Dados recuperados: {len(df)} linhas.")
        
        # Salva em CSV
        csv_filename = "consolidado_despesas.csv"
        df.to_csv(csv_filename, index=False, sep=';', encoding='utf-8-sig')
        
        # Compacta em ZIP
        zip_filename = "consolidado_despesas.zip"
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(csv_filename)
            
        print(f"Arquivo gerado com sucesso: {zip_filename}")
        
        # Limpa o CSV temporário
        if os.path.exists(csv_filename):
            os.remove(csv_filename)
        
    except Exception as e:
        print(f"Erro ao exportar: {e}")

if __name__ == "__main__":
    exportar_consolidado()