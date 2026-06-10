"""
solvabilidade.py
Cálculo determinístico do rácio de solvabilidade e percentil sectorial.

Nota de arquitetura: sem inteligência artificial — apenas operações matemáticas.
"""

import benchmarks
from liquidez import avaliar_racio

DADOS_NECESSARIOS = [
    "capital_proprio",
    "passivo_corrente",
    "passivo_nao_corrente",
]


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

    # obter() faz merge com BENCHMARK_GERAL — a chave existe sempre.
    bms = benchmarks.obter(setor, dimensao)

    avaliacao, percentil = avaliar_racio(racio, bms["solvabilidade"])

    return [{
        "racio":     "Solvabilidade",
        "formula":   "Capital Próprio / Passivo Total",
        "valor":     round(racio, 2),
        "avaliacao": avaliacao,
        "percentil": percentil,
        "ref_geral": not benchmarks.e_sectorial(setor, dimensao, "solvabilidade"),
    }]
