import pandas as pd
import requests
import zipfile
import io
import os

URLS_DEMONSTRACOES = [
    "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/2025/3T2025.zip", 
    "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/2025/2T2025.zip",
    "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/2025/1T2025.zip"
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FINAL_FILE = os.path.join(BASE_DIR, "relatorio_final.csv")

def processar_etl():
    print("Iniciando ETL...")
    
    lista_dfs = []

    for url in URLS_DEMONSTRACOES:
        print(f"Baixando: {url}...")
        try:
            r = requests.get(url, timeout=60)
            if r.status_code != 200:
                print(f"Erro HTTP: {r.status_code}")
                continue
                
            # ler CSV direto ou extrair ZIP
            try:
                df = pd.read_csv(io.BytesIO(r.content), sep=';', encoding='latin1', on_bad_lines='warn', dtype=str)
            except:
                z = zipfile.ZipFile(io.BytesIO(r.content))
                csv_name = [n for n in z.namelist() if n.endswith('.csv') or n.endswith('.CSV')][0]
                with z.open(csv_name) as f:
                    df = pd.read_csv(f, sep=';', encoding='latin1', dtype=str)
            
            df['origem'] = url
            lista_dfs.append(df)
            print(f"Sucesso! {len(df)} linhas.")
            
        except Exception as e:
            print(f"Erro: {e}")

    if lista_dfs:
        print("Consolidando e Limpando...")
        df_final = pd.concat(lista_dfs, ignore_index=True)
        
        # limpeza de números (PT-BR para Float)
        cols_num = ['VL_SALDO_INICIAL', 'VL_SALDO_FINAL']
        for col in cols_num:
            if col in df_final.columns:
                df_final[col] = df_final[col].str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        
        df_final.to_csv(FINAL_FILE, index=False, encoding='utf-8')
        print(f"ARQUIVO GERADO: {FINAL_FILE}")
    else:
        print("Nada foi gerado. Verifique os links.")

if __name__ == "__main__":
    processar_etl()