# Dashboard de Análise Financeira - Operadoras de Saúde (ANS)

> Teste Técnico para Estágio em Desenvolvimento de Software - IntuitiveCare

Este projeto é uma solução Full Stack para extração, transformação, carregamento e visualização de dados financeiros de Operadoras de Planos de Saúde, utilizando dados abertos da ANS (Agência Nacional de Saúde Suplementar).

---

## Arquitetura do Projeto

O sistema foi desenvolvido seguindo uma arquitetura modular baseada em 4 Pilares, garantindo separação de responsabilidades e facilidade de manutenção.

```mermaid
graph TD
    classDef python fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1;
    classDef database fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20;
    classDef file fill:#fff3e0,stroke:#ef6c00,stroke-width:2px,stroke-dasharray: 5 5,color:#e65100;
    classDef external fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c;
    classDef infra fill:#eceff1,stroke:#455a64,stroke-width:2px,stroke-dasharray: 3 3,color:#37474f;
    classDef web fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#f57f17;

    subgraph EXTERNO ["🌐 Fonte de Dados"]
        ANS_Site[Portal Dados Abertos ANS]:::external
    end

    subgraph APP_ETL ["⚙️ Engenharia de Dados (ETL)"]
        direction TB
        MainETL("etl/main_etl.py"):::python

        subgraph TEMP ["📂 Staging (CSV)"]
            DemoCSV(demonstracoes_contabeis.csv):::file
            OpCSV(operadoras.csv):::file
        end

        Loader("etl/loader.py"):::python
    end

    subgraph INFRA_DOCKER ["🐳 Infraestrutura"]
        DockerComp("docker-compose.yml"):::infra

        subgraph DB_SERVICE ["Container: intuitive_postgres"]
            InitSQL("sql/init.sql"):::database
            Postgres[("PostgreSQL DB")]:::database
        end
    end

    subgraph WEB_APP ["🚀 Aplicação Web"]
        direction TB
        API("🐍 Backend (FastAPI)"):::python
        Front("🎨 Frontend (Vue.js)"):::web
    end

    subgraph ANALYTICS ["📊 Análise"]
        Queries("sql/queries_analiticas.sql"):::external
    end

    ANS_Site -->|Download ZIPs| MainETL
    MainETL -->|Gera| DemoCSV
    MainETL -->|Gera| OpCSV
    DemoCSV -->|Lê| Loader
    OpCSV -->|Lê| Loader
    Loader -- "COPY (Alta Performance)" --> Postgres
    InitSQL -.->|Cria Tabelas no Boot| Postgres
    Postgres <-->|Lê Dados| API
    API <-->|JSON / Axios| Front
    Queries -.->|Consulta Ad-Hoc| Postgres
```

### Tecnologias Utilizadas

| Camada             | Tecnologia              | Motivação da Escolha                                                                    |
| ------------------ | ----------------------- | --------------------------------------------------------------------------------------- |
| **Banco de Dados** | **PostgreSQL (Docker)** | Robustez, suporte a queries complexas e facilidade de setup via container.              |
| **ETL**            | **Python (Pandas)**     | Melhor ferramenta de mercado para manipulação de dados e tratamento de encodings/erros. |
| **Backend**        | **FastAPI**             | Alta performance (async), documentação automática (Swagger) e sintaxe moderna.          |
| **Frontend**       | **Vue.js 3 + Vite**     | Curva de aprendizado rápida, reatividade performática e build otimizado.                |
| **Visualização**   | **Chart.js**            | Biblioteca leve e flexível para renderização de gráficos interativos.                   |

---

## Como Rodar o Projeto

### Pré-requisitos

- Docker e Docker Compose
- Python 3.8+
- Node.js 16+

### Passo 1: Infraestrutura (Banco de Dados)

Inicie o container do PostgreSQL. O script `init.sql` criará automaticamente as tabelas necessárias.

```bash
docker-compose up -d

```

### Passo 2: ETL (Carga de Dados)

Execute os scripts para baixar os dados da ANS, tratar inconsistências (como encoding latin1) e popular o banco.

```bash
# Instale as dependências Python
pip install pandas requests psycopg2-binary fastapi uvicorn

# 1. Baixar e tratar os arquivos (Gera CSVs na pasta etl/)
python3 etl/main_etl.py

# 2. Carregar os CSVs para o Banco de Dados
python3 etl/loader.py

```

### Passo 3: Backend (API)

Inicie o servidor da API.

```bash
uvicorn backend.main:app --reload

```

- **Documentação da API:** Acesse `http://localhost:8000/docs` para ver o Swagger UI.

### Passo 4: Frontend (Interface)

Em um novo terminal, inicie a aplicação Vue.js.

```bash
cd frontend
npm install
npm run dev

```

- **Acesse o Dashboard:** Abra `http://localhost:5173/` no seu navegador.

---

## Funcionalidades Implementadas

1. **Dashboard Financeiro:**

- Visualização do Total Geral de Despesas (Eventos/Sinistros).
- Gráfico de Barras: Top 5 Estados com maiores despesas.
- Lista: Top 5 Operadoras com maiores gastos no último trimestre.

2. **Busca de Operadoras:**

- Listagem paginada de todas as operadoras ativas.
- **Busca Textual:** Filtro dinâmico por Razão Social ou CNPJ.

3. **Detalhe da Operadora:**

- Visualização de dados cadastrais (Registro ANS, Endereço, Modalidade).
- **Histórico Financeiro:** Gráfico de linha mostrando a evolução das despesas (trimestre a trimestre).

---

## Decisões de Design e Trade-offs

- **FastAPI vs Flask:** Optei pelo FastAPI devido à sua validação de dados nativa (Pydantic) e geração automática de documentação, o que acelerou o desenvolvimento e facilita testes.
- **ETL em Python vs SQL Puro:** O tratamento dos arquivos da ANS exigiu lógica complexa de limpeza (erros de encoding, colunas renomeadas), o que seria inviável fazer apenas com SQL. O Pandas ofereceu a flexibilidade necessária.
- **Paginação no Backend:** Para garantir performance, a paginação é feita diretamente na query SQL (LIMIT/OFFSET), evitando trafegar milhares de registros desnecessários para o frontend.

* **Tipo de Dados Monetário (DECIMAL vs FLOAT):** Optei por utilizar `NUMERIC(20,2)` (Decimal) no PostgreSQL para armazenar os valores monetários. O tipo `FLOAT` utiliza ponto flutuante binário e pode apresentar erros de precisão em operações financeiras. O `NUMERIC` garante a exatidão dos centavos, essencial para demonstrativos contábeis.

---

**Desenvolvido por Matteo**

```

```
