-- tabela de demonstracoes contabeis
CREATE TABLE IF NOT EXISTS demonstracoes_contabeis (
    data_referencia DATE, -- os formatos já estão em YYYY-MM-DD
    reg_ans VARCHAR(6), -- de primeira coloquei INT, mas pelo que parece registro ANS podem ter 0's a esquerda, irei tratar como um 'CPF'
    cd_conta_contabil VARCHAR(255),
    descricao TEXT,
    vl_saldo_inicial NUMERIC(20,2),
    vl_saldo_final NUMERIC(20,2),
    arquivo_origem TEXT
);

CREATE INDEX IF NOT EXISTS idx_reg_ans ON demonstracoes_contabeis (reg_ans);
CREATE INDEX IF NOT EXISTS idx_data_ref ON demonstracoes_contabeis (data_referencia);

-- tabela de cadastro das operadoras
CREATE TABLE IF NOT EXISTS operadoras (
    reg_ans VARCHAR(10) PRIMARY KEY,
    cnpj VARCHAR(20),
    razao_social TEXT,
    nome_fantasia TEXT,
    modalidade TEXT,
    logradouro TEXT,
    numero TEXT,
    complemento TEXT,
    bairro TEXT,
    cidade TEXT,
    uf VARCHAR(2),
    cep VARCHAR(20),
    telefone VARCHAR(50),
    email TEXT,
    representante TEXT,
    cargo_representante TEXT,
    data_registro DATE
);

CREATE INDEX IF NOT EXISTS idx_demo_reg_ans ON demonstracoes_contabeis (reg_ans);
CREATE INDEX IF NOT EXISTS idx_ops_uf ON operadoras (uf);