import pandas as pd
import requests
import zipfile
import io
import os

# URLs atualizadas
URLS_DEMONSTRACOES = [
    "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/2025/3T2025.zip", #2025-12-11
    "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/2025/2T2025.zip", #2025-09-02
    "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/2025/1T2025.zip"  #2025-06-03
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FINAL_FILE = os.path.join(BASE_DIR, "relatorio_final.csv")

def processar_etl():
    print("Iniciando ETL...")
    lista_dfs = []

    for url in URLS_DEMONSTRACOES:
        print(f"Baixando: {url}...")
        try:
            r = requests.get(url, timeout=120)
            if r.status_code != 200:
                print(f"Erro HTTP {r.status_code} ao acessar {url}. Pulando...")
                continue
                
            file_content = io.BytesIO(r.content)
            df = None
            
            # tenta abrir como ZIP primeiro (padrão ANS)
            try:
                with zipfile.ZipFile(file_content) as z:
                    # procura qualquer arquivo que termine com .csv ou .CSV dentro do zip
                    csv_files = [n for n in z.namelist() if n.lower().endswith('.csv')]
                    
                    if not csv_files:
                        print(f"Nenhum CSV encontrado dentro do ZIP de {url}")
                        continue

                    # pega o primeiro CSV encontrado
                    print(f"Extraindo {csv_files[0]} do ZIP...")
                    with z.open(csv_files[0]) as f:
                        df = pd.read_csv(f, sep=';', encoding='latin1', dtype=str, on_bad_lines='skip')
            
            except zipfile.BadZipFile:
                # se falhar como ZIP, tenta ler direto como CSV
                print("Arquivo não é ZIP, tentando ler como CSV direto...")
                file_content.seek(0)
                df = pd.read_csv(file_content, sep=';', encoding='latin1', dtype=str, on_bad_lines='skip')

            if df is not None:
                df['origem'] = url
                df.columns = [c.strip().upper() for c in df.columns]
                lista_dfs.append(df)
                print(f"Sucesso! {len(df)} linhas processadas.")
            
        except Exception as e:
            print(f"Erro crítico ao processar {url}: {e}")

    if lista_dfs:
        print("Consolidando dados...")
        df_final = pd.concat(lista_dfs, ignore_index=True)
        
        # limpeza numérica
        cols_num = ['VL_SALDO_INICIAL', 'VL_SALDO_FINAL']
        for col in cols_num:
            if col in df_final.columns:
                # remover pontos de milhar e troca vírgula por ponto
                df_final[col] = df_final[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                # forçar conversão para numérico, erros viram NaN
                df_final[col] = pd.to_numeric(df_final[col], errors='coerce').fillna(0)
        
        df_final.to_csv(FINAL_FILE, index=False, encoding='utf-8')
        print(f"ETL FINALIZADO COM SUCESSO! Arquivo gerado: {FINAL_FILE}")
    else:
        print("Nenhum dado foi gerado. Verifique sua conexão ou as URLs da ANS.")

if __name__ == "__main__":
    processar_etl()