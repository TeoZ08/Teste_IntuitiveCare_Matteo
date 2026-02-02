-- Query 1: Operadoras com despesas ACIMA DA MÉDIA do último trimestre
WITH despesas_ultimo_trimestre AS (
    SELECT 
        op.razao_social,
        op.reg_ans,
        SUM(dc.vl_saldo_final) as total_despesas
    FROM demonstracoes_contabeis dc
    JOIN operadoras op ON dc.reg_ans = op.reg_ans
    WHERE 
        dc.cd_conta_contabil LIKE '4%' 
        AND dc.data_referencia = (SELECT MAX(data_referencia) FROM demonstracoes_contabeis)
    GROUP BY op.razao_social, op.reg_ans
),
media_despesas AS (
    SELECT AVG(total_despesas) as media_geral FROM despesas_ultimo_trimestre
)
SELECT 
    d.razao_social,
    d.reg_ans,
    d.total_despesas
FROM despesas_ultimo_trimestre d, media_despesas m
WHERE d.total_despesas > m.media_geral
ORDER BY d.total_despesas DESC;

-- Query 2: Despesas por UF (JÁ ESTAVA CERTO)
SELECT 
    op.uf,
    SUM(dc.vl_saldo_final) as total_despesas_uf
FROM demonstracoes_contabeis dc
JOIN operadoras op ON dc.reg_ans = op.reg_ans
WHERE dc.cd_conta_contabil LIKE '4%'
GROUP BY op.uf
ORDER BY total_despesas_uf DESC;

-- Query 3: Evolução das despesas (Crescimento %) (JÁ ESTAVA CERTO)
WITH despesas_trimestrais AS (
    SELECT 
        reg_ans,
        data_referencia,
        SUM(vl_saldo_final) as despesa_total
    FROM demonstracoes_contabeis
    WHERE cd_conta_contabil LIKE '4%'
    GROUP BY reg_ans, data_referencia
),
inicio_fim AS (
    SELECT MIN(data_referencia) as data_ini, MAX(data_referencia) as data_fim 
    FROM demonstracoes_contabeis
)
SELECT 
    op.razao_social,
    d_fim.despesa_total as despesa_ultimo,
    d_ini.despesa_total as despesa_primeiro,
    ROUND(((d_fim.despesa_total - d_ini.despesa_total) / NULLIF(d_ini.despesa_total, 0)) * 100, 2) as crescimento_pct
FROM despesas_trimestrais d_fim
JOIN despesas_trimestrais d_ini ON d_fim.reg_ans = d_ini.reg_ans
JOIN operadoras op ON d_fim.reg_ans = op.reg_ans
CROSS JOIN inicio_fim
WHERE d_fim.data_referencia = inicio_fim.data_fim
  AND d_ini.data_referencia = inicio_fim.data_ini
ORDER BY crescimento_pct DESC
LIMIT 10;