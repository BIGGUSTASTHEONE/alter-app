"""
benchmarks.py
Benchmarks de referência (P25/P50/P75) por setor de atividade e dimensão.

Fonte: SABI — Sistema de Análise de Balanços Ibéricos (Bureau van Dijk)
928.463 empresas portuguesas activas, exportadas em Junho de 2026.
Dimensão classificada pelos critérios EU (2 de 3: trabalhadores/VN/balanço).
"""

# ---------------------------------------------------------------------------
# METADADOS DA FONTE
# ---------------------------------------------------------------------------

FONTE = {
    "nome": "SABI — Sistema de Análise de Balanços Ibéricos (Bureau van Dijk)",
    "ano_dados": 2026,
    "url": "https://sabi.bvdinfo.com/",
    "data_consulta": "2026-06-09",
    "nota": (
        "Benchmarks calculados sobre 928.463 empresas portuguesas activas. "
        "P25/P50/P75 por setor (CAE Rev.4) e dimensão (critérios EU). "
        "Agricultura e agro-indústria usa referência geral por insuficiência de dados."
    ),
}

# ---------------------------------------------------------------------------
# FALLBACK GERAL
# Usado quando não há dados suficientes para o setor+dimensão específico.
# ---------------------------------------------------------------------------

BENCHMARK_GERAL = {
    "liquidez_geral":    {"p25": 0.90, "p50": 1.20, "p75": 1.65},
    "liquidez_reduzida": {"p25": 0.65, "p50": 0.90, "p75": 1.25},
    "liquidez_imediata": {"p25": 0.10, "p50": 0.20, "p75": 0.40},
}

# ---------------------------------------------------------------------------
# BENCHMARKS POR SETOR E DIMENSÃO
# Fonte: SABI, 928.463 empresas portuguesas, Junho 2026
# Chave: (setor, dimensao) — strings exactas usadas na interface
# ---------------------------------------------------------------------------

BENCHMARKS = {
    ("Comércio a retalho", "Grande"): {
        "liquidez_geral": {"p25": 0.8412, "p50": 1.1235, "p75": 1.4613},
        "liquidez_reduzida": {"p25": 0.3922, "p50": 0.5905, "p75": 0.8745},
        "solvabilidade": {"p25": 0.1974, "p50": 0.3245, "p75": 0.4665},
    },
    ("Comércio a retalho", "Micro"): {
        "liquidez_geral": {"p25": 0.629, "p50": 1.416, "p75": 3.603},
        "liquidez_reduzida": {"p25": 0.216, "p50": 0.758, "p75": 2.18},
        "solvabilidade": {"p25": 0.2017, "p50": 0.4416, "p75": 0.7287},
    },
    ("Comércio a retalho", "Média"): {
        "liquidez_geral": {"p25": 1.0112, "p50": 1.329, "p75": 1.9245},
        "liquidez_reduzida": {"p25": 0.473, "p50": 0.741, "p75": 1.2188},
        "solvabilidade": {"p25": 0.2374, "p50": 0.3865, "p75": 0.5779},
    },
    ("Comércio a retalho", "Pequena"): {
        "liquidez_geral": {"p25": 1.102, "p50": 1.736, "p75": 3.1},
        "liquidez_reduzida": {"p25": 0.562, "p50": 1.03, "p75": 1.997},
        "solvabilidade": {"p25": 0.2811, "p50": 0.4972, "p75": 0.7099},
    },
    ("Comércio por grosso", "Grande"): {
        "liquidez_geral": {"p25": 1.078, "p50": 1.347, "p75": 1.913},
        "liquidez_reduzida": {"p25": 0.747, "p50": 1.045, "p75": 1.393},
        "solvabilidade": {"p25": 0.1818, "p50": 0.3661, "p75": 0.5867},
    },
    ("Comércio por grosso", "Micro"): {
        "liquidez_geral": {"p25": 0.845, "p50": 1.579, "p75": 3.886},
        "liquidez_reduzida": {"p25": 0.493, "p50": 1.168, "p75": 2.982},
        "solvabilidade": {"p25": 0.2085, "p50": 0.4535, "p75": 0.7455},
    },
    ("Comércio por grosso", "Média"): {
        "liquidez_geral": {"p25": 1.1755, "p50": 1.65, "p75": 2.573},
        "liquidez_reduzida": {"p25": 0.8115, "p50": 1.185, "p75": 1.899},
        "solvabilidade": {"p25": 0.2701, "p50": 0.4399, "p75": 0.6481},
    },
    ("Comércio por grosso", "Pequena"): {
        "liquidez_geral": {"p25": 1.2258, "p50": 1.8, "p75": 3.0682},
        "liquidez_reduzida": {"p25": 0.83, "p50": 1.268, "p75": 2.1395},
        "solvabilidade": {"p25": 0.2613, "p50": 0.4603, "p75": 0.6795},
    },
    ("Construção e imobiliário", "Grande"): {
        "liquidez_geral": {"p25": 1.137, "p50": 1.3, "p75": 1.665},
        "liquidez_reduzida": {"p25": 1.08, "p50": 1.256, "p75": 1.576},
        "solvabilidade": {"p25": 0.2433, "p50": 0.3789, "p75": 0.5094},
    },
    ("Construção e imobiliário", "Micro"): {
        "liquidez_geral": {"p25": 0.954, "p50": 1.754, "p75": 4.2993},
        "liquidez_reduzida": {"p25": 0.619, "p50": 1.39, "p75": 3.398},
        "solvabilidade": {"p25": 0.2057, "p50": 0.4354, "p75": 0.7085},
    },
    ("Construção e imobiliário", "Média"): {
        "liquidez_geral": {"p25": 1.185, "p50": 1.534, "p75": 2.169},
        "liquidez_reduzida": {"p25": 1.041, "p50": 1.345, "p75": 1.854},
        "solvabilidade": {"p25": 0.2485, "p50": 0.404, "p75": 0.5803},
    },
    ("Construção e imobiliário", "Pequena"): {
        "liquidez_geral": {"p25": 1.2183, "p50": 1.728, "p75": 2.8495},
        "liquidez_reduzida": {"p25": 0.9335, "p50": 1.365, "p75": 2.188},
        "solvabilidade": {"p25": 0.2137, "p50": 0.4025, "p75": 0.6075},
    },
    ("Indústria transformadora", "Grande"): {
        "liquidez_geral": {"p25": 1.031, "p50": 1.355, "p75": 2.073},
        "liquidez_reduzida": {"p25": 0.597, "p50": 0.93, "p75": 1.431},
        "solvabilidade": {"p25": 0.3248, "p50": 0.4778, "p75": 0.6324},
    },
    ("Indústria transformadora", "Micro"): {
        "liquidez_geral": {"p25": 0.69, "p50": 1.4825, "p75": 3.668},
        "liquidez_reduzida": {"p25": 0.484, "p50": 1.197, "p75": 3.078},
        "solvabilidade": {"p25": 0.2249, "p50": 0.4571, "p75": 0.7337},
    },
    ("Indústria transformadora", "Média"): {
        "liquidez_geral": {"p25": 1.069, "p50": 1.5545, "p75": 2.5652},
        "liquidez_reduzida": {"p25": 0.642, "p50": 1.081, "p75": 1.846},
        "solvabilidade": {"p25": 0.3163, "p50": 0.4854, "p75": 0.6791},
    },
    ("Indústria transformadora", "Pequena"): {
        "liquidez_geral": {"p25": 1.037, "p50": 1.592, "p75": 2.746},
        "liquidez_reduzida": {"p25": 0.655, "p50": 1.165, "p75": 2.128},
        "solvabilidade": {"p25": 0.2675, "p50": 0.4595, "p75": 0.6751},
    },
    ("Outro / Não especificado", "Grande"): {
        "liquidez_geral": {"p25": 0.6875, "p50": 1.118, "p75": 1.8317},
        "liquidez_reduzida": {"p25": 0.6, "p50": 1.0885, "p75": 1.729},
        "solvabilidade": {"p25": 0.1967, "p50": 0.3885, "p75": 0.5744},
    },
    ("Outro / Não especificado", "Micro"): {
        "liquidez_geral": {"p25": 0.503, "p50": 1.472, "p75": 5.191},
        "liquidez_reduzida": {"p25": 0.286, "p50": 1.127, "p75": 3.971},
        "solvabilidade": {"p25": 0.2088, "p50": 0.4938, "p75": 0.8035},
    },
    ("Outro / Não especificado", "Média"): {
        "liquidez_geral": {"p25": 0.823, "p50": 1.2465, "p75": 2.0543},
        "liquidez_reduzida": {"p25": 0.6625, "p50": 1.13, "p75": 1.8017},
        "solvabilidade": {"p25": 0.2212, "p50": 0.4196, "p75": 0.6343},
    },
    ("Outro / Não especificado", "Pequena"): {
        "liquidez_geral": {"p25": 0.9672, "p50": 1.5195, "p75": 2.9547},
        "liquidez_reduzida": {"p25": 0.699, "p50": 1.22, "p75": 2.339},
        "solvabilidade": {"p25": 0.2126, "p50": 0.44, "p75": 0.6851},
    },
    ("Restauração e hotelaria", "Grande"): {
        "liquidez_geral": {"p25": 0.9702, "p50": 1.4215, "p75": 1.8853},
        "liquidez_reduzida": {"p25": 0.9255, "p50": 1.266, "p75": 1.8153},
        "solvabilidade": {"p25": 0.2727, "p50": 0.4029, "p75": 0.6281},
    },
    ("Restauração e hotelaria", "Micro"): {
        "liquidez_geral": {"p25": 0.241, "p50": 0.877, "p75": 2.64},
        "liquidez_reduzida": {"p25": 0.165, "p50": 0.68, "p75": 2.306},
        "solvabilidade": {"p25": 0.1951, "p50": 0.4348, "p75": 0.7205},
    },
    ("Restauração e hotelaria", "Média"): {
        "liquidez_geral": {"p25": 0.563, "p50": 1.03, "p75": 1.887},
        "liquidez_reduzida": {"p25": 0.505, "p50": 0.931, "p75": 1.809},
        "solvabilidade": {"p25": 0.2871, "p50": 0.4644, "p75": 0.6343},
    },
    ("Restauração e hotelaria", "Pequena"): {
        "liquidez_geral": {"p25": 0.666, "p50": 1.239, "p75": 2.438},
        "liquidez_reduzida": {"p25": 0.5667, "p50": 1.12, "p75": 2.265},
        "solvabilidade": {"p25": 0.2446, "p50": 0.4454, "p75": 0.6647},
    },
    ("Saúde e farmácia", "Grande"): {
        "liquidez_geral": {"p25": 0.4762, "p50": 0.645, "p75": 0.947},
        "liquidez_reduzida": {"p25": 0.409, "p50": 0.5975, "p75": 0.9235},
        "solvabilidade": {"p25": 0.126, "p50": 0.2794, "p75": 0.5183},
    },
    ("Saúde e farmácia", "Micro"): {
        "liquidez_geral": {"p25": 0.974, "p50": 2.8, "p75": 9.059},
        "liquidez_reduzida": {"p25": 0.931, "p50": 2.727, "p75": 8.8953},
        "solvabilidade": {"p25": 0.4013, "p50": 0.6985, "p75": 0.8962},
    },
    ("Saúde e farmácia", "Média"): {
        "liquidez_geral": {"p25": 0.6438, "p50": 1.1565, "p75": 2.0143},
        "liquidez_reduzida": {"p25": 0.6028, "p50": 1.107, "p75": 1.955},
        "solvabilidade": {"p25": 0.3353, "p50": 0.6142, "p75": 0.8313},
    },
    ("Saúde e farmácia", "Pequena"): {
        "liquidez_geral": {"p25": 0.7572, "p50": 1.5, "p75": 3.1707},
        "liquidez_reduzida": {"p25": 0.7152, "p50": 1.4485, "p75": 3.1265},
        "solvabilidade": {"p25": 0.424, "p50": 0.6846, "p75": 0.8589},
    },
    ("Serviços profissionais", "Grande"): {
        "liquidez_geral": {"p25": 0.942, "p50": 1.252, "p75": 1.5475},
        "liquidez_reduzida": {"p25": 0.8655, "p50": 1.209, "p75": 1.5475},
        "solvabilidade": {"p25": 0.2507, "p50": 0.3777, "p75": 0.5263},
    },
    ("Serviços profissionais", "Micro"): {
        "liquidez_geral": {"p25": 0.795, "p50": 1.858, "p75": 4.969},
        "liquidez_reduzida": {"p25": 0.708, "p50": 1.757, "p75": 4.737},
        "solvabilidade": {"p25": 0.2835, "p50": 0.559, "p75": 0.8092},
    },
    ("Serviços profissionais", "Média"): {
        "liquidez_geral": {"p25": 1.0145, "p50": 1.358, "p75": 1.9005},
        "liquidez_reduzida": {"p25": 0.928, "p50": 1.2945, "p75": 1.889},
        "solvabilidade": {"p25": 0.2426, "p50": 0.3848, "p75": 0.573},
    },
    ("Serviços profissionais", "Pequena"): {
        "liquidez_geral": {"p25": 1.055, "p50": 1.5745, "p75": 2.583},
        "liquidez_reduzida": {"p25": 0.9962, "p50": 1.4905, "p75": 2.4698},
        "solvabilidade": {"p25": 0.2564, "p50": 0.4798, "p75": 0.6848},
    },
    ("Tecnologia e software", "Grande"): {
        "liquidez_geral": {"p25": 1.1277, "p50": 1.527, "p75": 1.8542},
        "liquidez_reduzida": {"p25": 1.1255, "p50": 1.478, "p75": 1.8455},
        "solvabilidade": {"p25": 0.2331, "p50": 0.4095, "p75": 0.4973},
    },
    ("Tecnologia e software", "Micro"): {
        "liquidez_geral": {"p25": 0.843, "p50": 1.835, "p75": 4.625},
        "liquidez_reduzida": {"p25": 0.803, "p50": 1.796, "p75": 4.545},
        "solvabilidade": {"p25": 0.2996, "p50": 0.5657, "p75": 0.8041},
    },
    ("Tecnologia e software", "Média"): {
        "liquidez_geral": {"p25": 1.138, "p50": 1.4735, "p75": 2.1555},
        "liquidez_reduzida": {"p25": 1.1162, "p50": 1.4735, "p75": 2.042},
        "solvabilidade": {"p25": 0.2119, "p50": 0.4239, "p75": 0.6187},
    },
    ("Tecnologia e software", "Pequena"): {
        "liquidez_geral": {"p25": 1.09, "p50": 1.547, "p75": 2.462},
        "liquidez_reduzida": {"p25": 1.06, "p50": 1.524, "p75": 2.425},
        "solvabilidade": {"p25": 0.2445, "p50": 0.4309, "p75": 0.6328},
    },
    ("Transportes e logística", "Grande"): {
        "liquidez_geral": {"p25": 0.7775, "p50": 1.077, "p75": 1.5825},
        "liquidez_reduzida": {"p25": 0.7632, "p50": 1.064, "p75": 1.5262},
        "solvabilidade": {"p25": 0.2207, "p50": 0.362, "p75": 0.5342},
    },
    ("Transportes e logística", "Micro"): {
        "liquidez_geral": {"p25": 0.475, "p50": 1.562, "p75": 5.868},
        "liquidez_reduzida": {"p25": 0.454, "p50": 1.522, "p75": 5.723},
        "solvabilidade": {"p25": 0.2557, "p50": 0.5431, "p75": 0.8374},
    },
    ("Transportes e logística", "Média"): {
        "liquidez_geral": {"p25": 0.8237, "p50": 1.1545, "p75": 1.8653},
        "liquidez_reduzida": {"p25": 0.7995, "p50": 1.1315, "p75": 1.8653},
        "solvabilidade": {"p25": 0.181, "p50": 0.3496, "p75": 0.5503},
    },
    ("Transportes e logística", "Pequena"): {
        "liquidez_geral": {"p25": 0.9085, "p50": 1.264, "p75": 2.0265},
        "liquidez_reduzida": {"p25": 0.8785, "p50": 1.239, "p75": 2.002},
        "solvabilidade": {"p25": 0.1848, "p50": 0.3392, "p75": 0.5581},
    },
}


# ---------------------------------------------------------------------------
# FUNÇÃO DE ACESSO
# ---------------------------------------------------------------------------

def obter(setor, dimensao):
    """
    Devolve os benchmarks para a combinação setor+dimensão.
    Faz merge com BENCHMARK_GERAL: chaves em falta no setor usam o valor geral.
    """
    return {**BENCHMARK_GERAL, **BENCHMARKS.get((setor, dimensao), {})}


def e_sectorial(setor, dimensao, racio):
    """
    True se o benchmark deste rácio vem de dados SABI do setor+dimensão;
    False se caiu no fallback geral (ex.: Liquidez Imediata, Agricultura).
    """
    return racio in BENCHMARKS.get((setor, dimensao), {})
