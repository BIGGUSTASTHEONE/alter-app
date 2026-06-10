"""
liquidez.py
Cálculo determinístico dos rácios de liquidez, avaliação face a benchmarks
sectoriais e estimativa de percentil dentro do setor e dimensão.

Nota de arquitetura: este ficheiro NÃO usa inteligência artificial.
São apenas operações matemáticas. A interpretação em linguagem natural
acontece noutro sítio (na API), e recebe os percentis como factos prontos.
"""

import benchmarks

DADOS_NECESSARIOS = [
    "ativo_corrente",
    "passivo_corrente",
    "inventarios",
    "caixa_e_depositos",
]


# ---------------------------------------------------------------------------
# CÁLCULO DOS RÁCIOS
# ---------------------------------------------------------------------------

def calcular_liquidez_geral(ativo_corrente, passivo_corrente):
    return ativo_corrente / passivo_corrente


def calcular_liquidez_reduzida(ativo_corrente, inventarios, passivo_corrente):
    return (ativo_corrente - inventarios) / passivo_corrente


def calcular_liquidez_imediata(caixa_e_depositos, passivo_corrente):
    return caixa_e_depositos / passivo_corrente


# ---------------------------------------------------------------------------
# PERCENTIL POR INTERPOLAÇÃO LINEAR
# Dado um valor e os três quartis (P25/P50/P75), estima em que percentil
# da distribuição o valor se encontra.
# Não envolve IA — é math pura aplicada aos benchmarks sectoriais (SABI).
# ---------------------------------------------------------------------------

def calcular_percentil(valor, p25, p50, p75):
    """
    Estima o percentil de um valor usando interpolação linear entre P25, P50 e P75.
    Extrapola suavemente abaixo do P25 e acima do P75.
    Resultado entre 1 e 99.
    """
    if valor <= p25:
        p0 = p25 - 2 * (p50 - p25)
        if p0 >= p25:
            return 1
        return max(1, round(25 * (valor - p0) / (p25 - p0)))
    elif valor <= p50:
        return round(25 + 25 * (valor - p25) / (p50 - p25))
    elif valor <= p75:
        return round(50 + 25 * (valor - p50) / (p75 - p50))
    else:
        p100 = p75 + 2 * (p75 - p50)
        if p100 <= p75:
            return 99
        return min(99, round(75 + 25 * (valor - p75) / (p100 - p75)))


def avaliar_racio(valor, bm):
    """
    Devolve (avaliacao, percentil) com base nos benchmarks P25/P50/P75.
    A avaliação é determinística — apenas compara números.
    """
    percentil = calcular_percentil(valor, bm["p25"], bm["p50"], bm["p75"])
    if valor >= bm["p75"]:
        avaliacao = "confortável"
    elif valor >= bm["p25"]:
        avaliacao = "dentro da norma"
    else:
        avaliacao = "abaixo da norma"
    return avaliacao, percentil


# ---------------------------------------------------------------------------
# FUNÇÃO PRINCIPAL DA CATEGORIA
# ---------------------------------------------------------------------------

def analisar_liquidez(dados, setor, dimensao):
    """
    dados:    dicionário com as chaves de DADOS_NECESSARIOS
    setor:    string com o setor de atividade (usado para escolher benchmarks)
    dimensao: string com a dimensão da empresa (id.)

    Devolve lista de dicionários — um por rácio — com nome, fórmula, valor,
    avaliação e percentil estimado no setor+dimensão.
    """
    ac = dados["ativo_corrente"]
    pc = dados["passivo_corrente"]
    inv = dados["inventarios"]
    caixa = dados["caixa_e_depositos"]

    bms = benchmarks.obter(setor, dimensao)

    geral = calcular_liquidez_geral(ac, pc)
    reduzida = calcular_liquidez_reduzida(ac, inv, pc)
    imediata = calcular_liquidez_imediata(caixa, pc)

    av_geral, pct_geral = avaliar_racio(geral, bms["liquidez_geral"])
    av_reduzida, pct_reduzida = avaliar_racio(reduzida, bms["liquidez_reduzida"])
    av_imediata, pct_imediata = avaliar_racio(imediata, bms["liquidez_imediata"])

    return [
        {
            "racio": "Liquidez Geral",
            "formula": "Ativo Corrente / Passivo Corrente",
            "valor": round(geral, 2),
            "avaliacao": av_geral,
            "percentil": pct_geral,
            "ref_geral": not benchmarks.e_sectorial(setor, dimensao, "liquidez_geral"),
        },
        {
            "racio": "Liquidez Reduzida",
            "formula": "(Ativo Corrente - Inventários) / Passivo Corrente",
            "valor": round(reduzida, 2),
            "avaliacao": av_reduzida,
            "percentil": pct_reduzida,
            "ref_geral": not benchmarks.e_sectorial(setor, dimensao, "liquidez_reduzida"),
        },
        {
            "racio": "Liquidez Imediata",
            "formula": "Caixa e Depósitos / Passivo Corrente",
            "valor": round(imediata, 2),
            "avaliacao": av_imediata,
            "percentil": pct_imediata,
            "ref_geral": not benchmarks.e_sectorial(setor, dimensao, "liquidez_imediata"),
        },
    ]
