"""
liquidez.py
Cálculo determinístico dos rácios de liquidez e respetiva avaliação
face a benchmarks de referência.

Nota de arquitetura: este ficheiro NÃO usa inteligência artificial.
São apenas operações matemáticas e comparações com valores de referência.
A interpretação em linguagem natural acontece noutro sítio (na API).
"""

# ---------------------------------------------------------------------------
# BENCHMARKS (isolados de propósito)
# Estes valores são referências gerais fixas, suficientes para validar o
# esqueleto da aplicação. Variam muito por setor; tornar os benchmarks
# dependentes do setor fica como otimização futura. Para trocar um benchmark,
# muda-se aqui e em mais lado nenhum.
# ---------------------------------------------------------------------------

BENCHMARKS = {
    "liquidez_geral": {
        "confortavel": 1.5,   # >= 1,5 confortável
        "minimo": 1.0,        # 1,0 a 1,5 aceitável mas a vigiar; < 1,0 alerta
    },
    "liquidez_reduzida": {
        "confortavel": 1.0,   # >= 1,0 confortável
        "minimo": 0.8,        # 0,8 a 1,0 aceitável; < 0,8 a vigiar
    },
    "liquidez_imediata": {
        "saudavel": 0.2,      # >= 0,2 habitualmente citado como saudável
    },
}

# Dados do balanço que esta categoria precisa.
# Serve a lógica de "dados primeiro": só se mostra a análise de liquidez
# quando estes quatro valores estão disponíveis.
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
    """Ativo Corrente / Passivo Corrente."""
    return ativo_corrente / passivo_corrente


def calcular_liquidez_reduzida(ativo_corrente, inventarios, passivo_corrente):
    """(Ativo Corrente - Inventários) / Passivo Corrente."""
    return (ativo_corrente - inventarios) / passivo_corrente


def calcular_liquidez_imediata(caixa_e_depositos, passivo_corrente):
    """Caixa e Depósitos Bancários / Passivo Corrente."""
    return caixa_e_depositos / passivo_corrente


# ---------------------------------------------------------------------------
# AVALIAÇÃO FACE AOS BENCHMARKS
# Devolve uma etiqueta simples ("confortável", "a vigiar", "alerta") para
# cada rácio. É um resumo determinístico; a leitura financeira de fundo fica
# para o diagnóstico da IA.
# ---------------------------------------------------------------------------

def avaliar_liquidez_geral(valor):
    b = BENCHMARKS["liquidez_geral"]
    if valor >= b["confortavel"]:
        return "confortável"
    if valor >= b["minimo"]:
        return "aceitável, a vigiar"
    return "sinal de alerta"


def avaliar_liquidez_reduzida(valor):
    b = BENCHMARKS["liquidez_reduzida"]
    if valor >= b["confortavel"]:
        return "confortável"
    if valor >= b["minimo"]:
        return "aceitável"
    return "a vigiar"


def avaliar_liquidez_imediata(valor):
    b = BENCHMARKS["liquidez_imediata"]
    if valor >= b["saudavel"]:
        return "saudável"
    return "baixa, mas não necessariamente preocupante"


# ---------------------------------------------------------------------------
# FUNÇÃO PRINCIPAL DA CATEGORIA
# Recebe os dados confirmados pelo utilizador (um dicionário) e devolve
# uma lista de rácios, cada um com nome, fórmula, valor e avaliação.
# É este resultado que vai depois para a tabela, para o gráfico e para a IA.
# ---------------------------------------------------------------------------

def analisar_liquidez(dados):
    """
    dados: dicionário com as chaves de DADOS_NECESSARIOS.
    Devolve uma lista de dicionários, um por rácio.
    """
    ac = dados["ativo_corrente"]
    pc = dados["passivo_corrente"]
    inv = dados["inventarios"]
    caixa = dados["caixa_e_depositos"]

    geral = calcular_liquidez_geral(ac, pc)
    reduzida = calcular_liquidez_reduzida(ac, inv, pc)
    imediata = calcular_liquidez_imediata(caixa, pc)

    return [
        {
            "racio": "Liquidez Geral",
            "formula": "Ativo Corrente / Passivo Corrente",
            "valor": round(geral, 2),
            "avaliacao": avaliar_liquidez_geral(geral),
        },
        {
            "racio": "Liquidez Reduzida",
            "formula": "(Ativo Corrente - Inventários) / Passivo Corrente",
            "valor": round(reduzida, 2),
            "avaliacao": avaliar_liquidez_reduzida(reduzida),
        },
        {
            "racio": "Liquidez Imediata",
            "formula": "Caixa e Depósitos / Passivo Corrente",
            "valor": round(imediata, 2),
            "avaliacao": avaliar_liquidez_imediata(imediata),
        },
    ]
