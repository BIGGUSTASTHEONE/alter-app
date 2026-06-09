"""
solvabilidade.py
Cálculo determinístico do rácio de solvabilidade e percentil sectorial.

Nota de arquitetura: sem inteligência artificial — apenas operações matemáticas.
"""

import benchmarks
from liquidez import calcular_percentil, avaliar_racio

DADOS_NECESSARIOS = [
    "capital_proprio",
    "passivo_corrente",
    "passivo_nao_corrente",
]

BENCHMARK_SOLVABILIDADE_GERAL = {"p25": 0.20, "p50": 0.40, "p75": 0.65}


def calcular_solvabilidade(capital_proprio, passivo_total):
    return capital_proprio / passivo_total


def analisar_solvabilidade(dados, setor, dimensao):
    """
    dados:    dicionário com as chaves de DADOS_NECESSARIOS
    setor:    string com o setor de atividade
    dimensao: string com a dimensão da empresa

    Devolve lista com um dicionário: rácio, fórmula, valor, avaliação, percentil.
    """
    cp  = dados["capital_proprio"]
    pc  = dados["passivo_corrente"]
    pnc = dados["passivo_nao_corrente"]

    passivo_total = pc + pnc

    racio = calcular_solvabilidade(cp, passivo_total)

    bms   = benchmarks.obter(setor, dimensao)
    bm_sv = bms.get("solvabilidade", BENCHMARK_SOLVABILIDADE_GERAL)

    avaliacao, percentil = avaliar_racio(racio, bm_sv)

    return [{
        "racio":     "Solvabilidade",
        "formula":   "Capital Próprio / Passivo Total",
        "valor":     round(racio, 2),
        "avaliacao": avaliacao,
        "percentil": percentil,
    }]
