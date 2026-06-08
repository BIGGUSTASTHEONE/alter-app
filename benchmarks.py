"""
benchmarks.py
Benchmarks de referência (P25/P50/P75) por setor de atividade e dimensão.

Fonte planeada: SABI (Sistema de Análise de Balanços Ibéricos), Bureau van Dijk
Acesso via UBI — a popular quando o acesso à base de dados estiver disponível.

Para popular com dados reais, corre o script importar_sabi.py com o export
do SABI e substitui o dicionário BENCHMARKS abaixo pelo output gerado.

Nota: A Liquidez Imediata não é publicada pelo Banco de Portugal nos Quadros
do Setor; usa-se o benchmark geral também para esse rácio.
"""

# ---------------------------------------------------------------------------
# METADADOS DA FONTE
# ---------------------------------------------------------------------------

FONTE = {
    "nome": "Banco de Portugal — Quadros do Setor (Central de Balanços)",
    "ano_dados": 2024,
    "url": "https://www.bportugal.pt/QS/qsweb/",
    "data_consulta": "2026-06-08",
    "nota": (
        "Benchmarks sectoriais detalhados em desenvolvimento. "
        "Os valores comparativos actuais são referências gerais "
        "para o total das empresas não financeiras portuguesas."
    ),
}

# ---------------------------------------------------------------------------
# FALLBACK GERAL
# Valores baseados na média do total das empresas não financeiras (BdP 2024).
# Usado para todos os setores enquanto não há dados SABI disponíveis.
# ---------------------------------------------------------------------------

BENCHMARK_GERAL = {
    "liquidez_geral":    {"p25": 0.90, "p50": 1.20, "p75": 1.65},
    "liquidez_reduzida": {"p25": 0.65, "p50": 0.90, "p75": 1.25},
    "liquidez_imediata": {"p25": 0.10, "p50": 0.20, "p75": 0.40},
}

# ---------------------------------------------------------------------------
# BENCHMARKS POR SETOR E DIMENSÃO
# Chave: (setor, dimensao) — strings exactas usadas na interface
#
# Este dicionário está vazio até os dados do SABI serem importados.
# Quando tiveres o export do SABI, corre importar_sabi.py e substitui
# este bloco pelo output gerado.
# ---------------------------------------------------------------------------

BENCHMARKS = {}


# ---------------------------------------------------------------------------
# FUNÇÃO DE ACESSO
# ---------------------------------------------------------------------------

def obter(setor, dimensao):
    """
    Devolve os benchmarks para a combinação setor+dimensão.
    Usa BENCHMARK_GERAL como fallback enquanto não há dados SABI.
    """
    return BENCHMARKS.get((setor, dimensao), BENCHMARK_GERAL)
