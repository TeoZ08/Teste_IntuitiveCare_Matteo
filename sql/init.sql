CREATE TABLE IF NOT EXISTS demonstracoes_contabeis (
    data_referencia DATE, -- os formatos já estão em YYYY-MM-DD
    reg_ans VARCHAR(6), -- De primeira coloquei INT, mas pelo que parece registro ANS podem ter 0's a esquerda, irei tratar como um 'CPF'
    cd_conta_contabil VARCHAR(255),
    descricao TEXT,
    vl_saldo_inicial NUMERIC(20,2),
    vl_saldo_final NUMERIC(20,2),
    arquivo_origem TEXT
);

CREATE INDEX IF NOT EXISTS idx_reg_ans ON demonstracoes_contabeis (reg_ans);
CREATE INDEX IF NOT EXISTS idx_data_ref ON demonstracoes_contabeis (data_referencia);