import pandas as pd
import requests
import zipfile
import io
import os
import sys

# URLs
URLS_DEMONSTRACOES = [
    "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/2025/3T2025.zip", 
    "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/2025/2T2025.zip",
    "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/2025/1T2025.zip"
]

URL_CADASTRO = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_DEMONSTRACOES = os.path.join(BASE_DIR, "demonstracoes_contabeis.csv")
FILE_OPERADORAS = os.path.join(BASE_DIR, "operadoras.csv")

def limpar_nome_coluna(col):
    return col.replace('"', '').replace("'", "").strip().upper().replace('\uFEFF', '')

def processar_etl():
    print("Iniciando ETL Blindado...")
    
    # --- Parte 1: Demonstracoes ---
    lista_dfs = []
    for url in URLS_DEMONSTRACOES:
        print(f"Baixando: {url}...")
        try:
            r = requests.get(url, timeout=120)
            if r.status_code != 200: continue
            
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                arquivos = z.namelist()
                csv_alvo = next((a for a in arquivos if 'despesa' in a.lower() or 'evento' in a.lower()), None)
                if not csv_alvo: 
                    csvs = [n for n in arquivos if n.lower().endswith('.csv')]
                    if csvs: csv_alvo = csvs[0]

                if csv_alvo:
                    print(f"Extraindo {csv_alvo}...")
                    with z.open(csv_alvo) as f:
                        df = pd.read_csv(f, sep=';', encoding='latin1', dtype=str, on_bad_lines='skip')
                        df['origem'] = url
                        df.columns = [c.strip().upper() for c in df.columns]
                        lista_dfs.append(df)
        except Exception as e:
            print(f"Erro em {url}: {e}")

    if lista_dfs:
        print("Consolidando demonstracoes...")
        df_final = pd.concat(lista_dfs, ignore_index=True)
        cols_num = ['VL_SALDO_INICIAL', 'VL_SALDO_FINAL']
        for col in cols_num:
            if col in df_final.columns:
                df_final[col] = df_final[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                df_final[col] = pd.to_numeric(df_final[col], errors='coerce').fillna(0)
        df_final.to_csv(FILE_DEMONSTRACOES, index=False, encoding='utf-8')
        print(f"Demonstracoes OK: {FILE_DEMONSTRACOES}")

    # --- Parte 2: Cadastro ---
    print("Baixando cadastro de operadoras...")
    try:
        r = requests.get(URL_CADASTRO, timeout=60)
        if r.status_code == 200:
            df = pd.read_csv(io.BytesIO(r.content), sep=';', encoding='latin1', dtype=str, on_bad_lines='skip')
            df.columns = [limpar_nome_coluna(c) for c in df.columns]
            
            # MAPA CORRIGIDO AQUI! 
            # Trocamos REGISTRO_ANS por REGISTRO_OPERADORA
            col_map = {
                'REGISTRO_OPERADORA': 'reg_ans',  # <--- CORREÇÃO
                'CNPJ': 'cnpj', 
                'RAZAO_SOCIAL': 'razao_social',
                'NOME_FANTASIA': 'nome_fantasia', 
                'MODALIDADE': 'modalidade', 
                'LOGRADOURO': 'logradouro',
                'NUMERO': 'numero', 
                'COMPLEMENTO': 'complemento', 
                'BAIRRO': 'bairro', 
                'CIDADE': 'cidade',
                'UF': 'uf', 
                'CEP': 'cep', 
                'TELEFONE': 'telefone', 
                'ENDERECO_ELETRONICO': 'email',
                'REPRESENTANTE': 'representante', 
                'CARGO_REPRESENTANTE': 'cargo_representante',
                'DATA_REGISTRO_ANS': 'data_registro'
            }
            
            cols_existentes = [c for c in col_map.keys() if c in df.columns]
            
            # Verificação ajustada para a nova coluna
            if 'REGISTRO_OPERADORA' not in cols_existentes:
                print(f"❌ ERRO CRÍTICO: Chave primária não encontrada!")
                print(f"   Colunas disponiveis: {list(df.columns)}")
                sys.exit(1)

            df = df[cols_existentes].rename(columns=col_map)
            
            if 'data_registro' in df.columns:
                df['data_registro'] = pd.to_datetime(df['data_registro'], format='%d/%m/%Y', errors='coerce').dt.date

            df.to_csv(FILE_OPERADORAS, index=False, encoding='utf-8')
            print(f"Cadastro OK: {FILE_OPERADORAS}")
            
    except Exception as e:
        print(f"Erro no cadastro: {e}")

if __name__ == "__main__":
    processar_etl()