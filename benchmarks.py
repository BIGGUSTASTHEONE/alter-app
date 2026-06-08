"""
benchmarks.py
Benchmarks de referência (P25/P50/P75) por setor de atividade e dimensão.

Fonte: Banco de Portugal — Quadros do Setor (Central de Balanços)
URL:   https://www.bportugal.pt/QS/qsweb/
Dados: exercício de 2024 (ano mais recente disponível)

Nota: A Liquidez Imediata não é publicada pelo Banco de Portugal nos
Quadros do Setor; usa-se um benchmark de referência geral para esse rácio.

COMO ACTUALIZAR:
1. Acede a https://www.bportugal.pt/QS/qsweb/
2. Selecciona o setor (CAE) e a dimensão pretendidos
3. No separador "Indicadores" > "Liquidez", copia P25/Mediana/P75
4. Actualiza as entradas correspondentes neste ficheiro
"""

# ---------------------------------------------------------------------------
# METADADOS DA FONTE
# ---------------------------------------------------------------------------

FONTE = {
    "nome": "Banco de Portugal — Quadros do Setor (Central de Balanços)",
    "ano_dados": 2024,
    "url": "https://www.bportugal.pt/QS/qsweb/",
    "data_consulta": "2026-06-08",
    "nota_liquidez_imediata": (
        "Liquidez Imediata não publicada pelo BdP. "
        "Usa-se benchmark de referência geral (P25=0.10, P50=0.20, P75=0.40)."
    ),
}

# ---------------------------------------------------------------------------
# FALLBACK GERAL
# Usado quando não há dados específicos para a combinação setor+dimensão.
# Valores baseados na média do total das empresas não financeiras (BdP 2024).
# ---------------------------------------------------------------------------

BENCHMARK_GERAL = {
    "liquidez_geral":   {"p25": 0.90, "p50": 1.20, "p75": 1.65},
    "liquidez_reduzida": {"p25": 0.65, "p50": 0.90, "p75": 1.25},
    "liquidez_imediata": {"p25": 0.10, "p50": 0.20, "p75": 0.40},
}

# ---------------------------------------------------------------------------
# BENCHMARKS POR SETOR E DIMENSÃO
# Chave: (setor, dimensao) — strings exactas usadas na interface
# Valor: dicionário com P25/P50/P75 para cada rácio
#
# Estado actual:
#   [REAL]  — valor extraído directamente do BdP QS ou fonte oficial
#   [APROX] — estimativa a substituir com dados reais do BdP QS
# ---------------------------------------------------------------------------

BENCHMARKS = {

    # --- Construção e imobiliário ---
    # [REAL] Fonte: IMPIC, Análise Económico-Financeira da Construção 2023
    ("Construção e imobiliário", "Micro"): {
        "liquidez_geral":   {"p25": 1.00, "p50": 1.20, "p75": 1.55},  # [APROX]
        "liquidez_reduzida": {"p25": 0.90, "p50": 1.10, "p75": 1.40},  # [APROX]
        "liquidez_imediata": BENCHMARK_GERAL["liquidez_imediata"],
    },
    ("Construção e imobiliário", "Pequena"): {
        "liquidez_geral":   {"p25": 1.10, "p50": 1.30, "p75": 1.65},  # [APROX]
        "liquidez_reduzida": {"p25": 1.00, "p50": 1.18, "p75": 1.48},  # [APROX]
        "liquidez_imediata": BENCHMARK_GERAL["liquidez_imediata"],
    },
    ("Construção e imobiliário", "Média"): {
        "liquidez_geral":   {"p25": 1.17, "p50": 1.35, "p75": 1.74},  # [REAL] IMPIC 2023
        "liquidez_reduzida": {"p25": 1.05, "p50": 1.25, "p75": 1.58},  # [APROX]
        "liquidez_imediata": BENCHMARK_GERAL["liquidez_imediata"],
    },
    ("Construção e imobiliário", "Grande"): {
        "liquidez_geral":   {"p25": 1.10, "p50": 1.35, "p75": 1.80},  # [APROX]
        "liquidez_reduzida": {"p25": 1.00, "p50": 1.28, "p75": 1.65},  # [APROX]
        "liquidez_imediata": BENCHMARK_GERAL["liquidez_imediata"],
    },

    # --- Comércio a retalho ---
    # [APROX] A extrair do BdP QS (CAE 47)
    ("Comércio a retalho", "Micro"): {
        "liquidez_geral":   {"p25": 0.75, "p50": 1.05, "p75": 1.45},  # [APROX]
        "liquidez_reduzida": {"p25": 0.45, "p50": 0.70, "p75": 1.05},  # [APROX]
        "liquidez_imediata": BENCHMARK_GERAL["liquidez_imediata"],
    },
    ("Comércio a retalho", "Pequena"): {
        "liquidez_geral":   {"p25": 0.85, "p50": 1.15, "p75": 1.55},  # [APROX]
        "liquidez_reduzida": {"p25": 0.50, "p50": 0.78, "p75": 1.10},  # [APROX]
        "liquidez_imediata": BENCHMARK_GERAL["liquidez_imediata"],
    },
    ("Comércio a retalho", "Média"): {
        "liquidez_geral":   {"p25": 0.90, "p50": 1.20, "p75": 1.60},  # [APROX]
        "liquidez_reduzida": {"p25": 0.55, "p50": 0.82, "p75": 1.15},  # [APROX]
        "liquidez_imediata": BENCHMARK_GERAL["liquidez_imediata"],
    },
    ("Comércio a retalho", "Grande"): {
        "liquidez_geral":   {"p25": 1.00, "p50": 1.30, "p75": 1.70},  # [APROX]
        "liquidez_reduzida": {"p25": 0.60, "p50": 0.90, "p75": 1.20},  # [APROX]
        "liquidez_imediata": BENCHMARK_GERAL["liquidez_imediata"],
    },

}


# ---------------------------------------------------------------------------
# FUNÇÃO DE ACESSO
# ---------------------------------------------------------------------------

def obter(setor, dimensao):
    """
    Devolve os benchmarks para a combinação setor+dimensão.
    Se não existir entrada específica, devolve BENCHMARK_GERAL.
    """
    return BENCHMARKS.get((setor, dimensao), BENCHMARK_GERAL)
