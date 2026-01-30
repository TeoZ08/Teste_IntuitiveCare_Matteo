import pandas as pd
import requests
import zipfile
import io
import os

# URLs das demonstracoes contabeis
URLS_DEMONSTRACOES = [
    "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/2025/3T2025.zip", 
    "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/2025/2T2025.zip",
    "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/2025/1T2025.zip"
]

# URL do cadastro de operadoras
URL_CADASTRO = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_DEMONSTRACOES = os.path.join(BASE_DIR, "demonstracoes_contabeis.csv")
FILE_OPERADORAS = os.path.join(BASE_DIR, "operadoras.csv")

def processar_etl():
    print("Iniciando ETL...")
    
    # --- Parte 1: Demonstracoes Contabeis ---
    lista_dfs = []
    for url in URLS_DEMONSTRACOES:
        print(f"Baixando: {url}...")
        try:
            r = requests.get(url, timeout=120)
            if r.status_code != 200:
                print(f"Erro HTTP {r.status_code} em {url}. Pulando...")
                continue
            
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                # procura arquivos que contenham 'despesa' ou 'evento' no nome
                # caso nao encontre, pega o primeiro csv disponivel (fallback)
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
                else:
                    print("Nenhum CSV relevante encontrado no ZIP.")

        except Exception as e:
            print(f"Erro ao processar {url}: {e}")

    if lista_dfs:
        print("Consolidando demonstracoes...")
        df_final = pd.concat(lista_dfs, ignore_index=True)
        
        # limpeza numerica
        cols_num = ['VL_SALDO_INICIAL', 'VL_SALDO_FINAL']
        for col in cols_num:
            if col in df_final.columns:
                df_final[col] = df_final[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                df_final[col] = pd.to_numeric(df_final[col], errors='coerce').fillna(0)
        
        df_final.to_csv(FILE_DEMONSTRACOES, index=False, encoding='utf-8')
        print(f"Arquivo gerado: {FILE_DEMONSTRACOES}")
    else:
        print("Nenhuma demonstracao processada.")

    # --- Parte 2: Cadastro de Operadoras ---
    print("Baixando cadastro de operadoras...")
    try:
        r = requests.get(URL_CADASTRO, timeout=60)
        if r.status_code == 200:
            # arquivo da ans usa cp1252 e ponto e virgula
            df = pd.read_csv(io.BytesIO(r.content), sep=';', encoding='cp1252', dtype=str, on_bad_lines='skip')
            
            # mapeamento de colunas para o banco
            col_map = {
                'Registro_ANS': 'reg_ans', 'CNPJ': 'cnpj', 'Razao_Social': 'razao_social',
                'Nome_Fantasia': 'nome_fantasia', 'Modalidade': 'modalidade', 'Logradouro': 'logradouro',
                'Numero': 'numero', 'Complemento': 'complemento', 'Bairro': 'bairro', 'Cidade': 'cidade',
                'UF': 'uf', 'CEP': 'cep', 'Telefone': 'telefone', 'Endereco_eletronico': 'email',
                'Representante': 'representante', 'Cargo_Representante': 'cargo_representante',
                'Data_Registro_ANS': 'data_registro'
            }
            
            # filtra e renomeia
            cols_existentes = [c for c in col_map.keys() if c in df.columns]
            df = df[cols_existentes].rename(columns=col_map)
            
            # converte data
            if 'data_registro' in df.columns:
                df['data_registro'] = pd.to_datetime(df['data_registro'], format='%d/%m/%Y', errors='coerce').dt.date

            df.to_csv(FILE_OPERADORAS, index=False, encoding='utf-8')
            print(f"Arquivo gerado: {FILE_OPERADORAS}")
        else:
            print(f"Erro HTTP {r.status_code} no cadastro.")
            
    except Exception as e:
        print(f"Erro no cadastro de operadoras: {e}")

if __name__ == "__main__":
    processar_etl()