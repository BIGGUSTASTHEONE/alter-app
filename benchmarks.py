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
        "liquidez_geral": {"p25": 0.802, "p50": 1.082, "p75": 1.422},
        "liquidez_reduzida": {"p25": 0.397, "p50": 0.585, "p75": 0.853},
        "solvabilidade": {"p25": 0.1857, "p50": 0.3177, "p75": 0.4485},
    },
    ("Comércio a retalho", "Micro"): {
        "liquidez_geral": {"p25": 0.629, "p50": 1.416, "p75": 3.603},
        "liquidez_reduzida": {"p25": 0.216, "p50": 0.758, "p75": 2.18},
        "solvabilidade": {"p25": 0.2017, "p50": 0.4416, "p75": 0.7287},
    },
    ("Comércio a retalho", "Média"): {
        "liquidez_geral": {"p25": 1.016, "p50": 1.34, "p75": 1.941},
        "liquidez_reduzida": {"p25": 0.472, "p50": 0.748, "p75": 1.235},
        "solvabilidade": {"p25": 0.242, "p50": 0.3904, "p75": 0.5824},
    },
    ("Comércio a retalho", "Pequena"): {
        "liquidez_geral": {"p25": 1.102, "p50": 1.736, "p75": 3.1},
        "liquidez_reduzida": {"p25": 0.562, "p50": 1.03, "p75": 1.997},
        "solvabilidade": {"p25": 0.2811, "p50": 0.4972, "p75": 0.7099},
    },
    ("Comércio por grosso", "Grande"): {
        "liquidez_geral": {"p25": 1.0933, "p50": 1.3275, "p75": 1.7668},
        "liquidez_reduzida": {"p25": 0.7512, "p50": 1.0425, "p75": 1.389},
        "solvabilidade": {"p25": 0.1819, "p50": 0.3496, "p75": 0.5831},
    },
    ("Comércio por grosso", "Micro"): {
        "liquidez_geral": {"p25": 0.845, "p50": 1.579, "p75": 3.886},
        "liquidez_reduzida": {"p25": 0.493, "p50": 1.168, "p75": 2.982},
        "solvabilidade": {"p25": 0.2085, "p50": 0.4535, "p75": 0.7455},
    },
    ("Comércio por grosso", "Média"): {
        "liquidez_geral": {"p25": 1.174, "p50": 1.658, "p75": 2.557},
        "liquidez_reduzida": {"p25": 0.816, "p50": 1.185, "p75": 1.889},
        "solvabilidade": {"p25": 0.2697, "p50": 0.4417, "p75": 0.6467},
    },
    ("Comércio por grosso", "Pequena"): {
        "liquidez_geral": {"p25": 1.2258, "p50": 1.8, "p75": 3.0682},
        "liquidez_reduzida": {"p25": 0.83, "p50": 1.268, "p75": 2.1395},
        "solvabilidade": {"p25": 0.2613, "p50": 0.4603, "p75": 0.6795},
    },
    ("Construção e imobiliário", "Grande"): {
        "liquidez_geral": {"p25": 1.1445, "p50": 1.3075, "p75": 1.665},
        "liquidez_reduzida": {"p25": 1.0817, "p50": 1.2505, "p75": 1.528},
        "solvabilidade": {"p25": 0.2467, "p50": 0.3733, "p75": 0.5116},
    },
    ("Construção e imobiliário", "Micro"): {
        "liquidez_geral": {"p25": 0.954, "p50": 1.754, "p75": 4.2993},
        "liquidez_reduzida": {"p25": 0.619, "p50": 1.39, "p75": 3.398},
        "solvabilidade": {"p25": 0.2057, "p50": 0.4354, "p75": 0.7085},
    },
    ("Construção e imobiliário", "Média"): {
        "liquidez_geral": {"p25": 1.1827, "p50": 1.537, "p75": 2.154},
        "liquidez_reduzida": {"p25": 1.0408, "p50": 1.3455, "p75": 1.8542},
        "solvabilidade": {"p25": 0.2478, "p50": 0.404, "p75": 0.5803},
    },
    ("Construção e imobiliário", "Pequena"): {
        "liquidez_geral": {"p25": 1.2183, "p50": 1.728, "p75": 2.8495},
        "liquidez_reduzida": {"p25": 0.9335, "p50": 1.365, "p75": 2.188},
        "solvabilidade": {"p25": 0.2137, "p50": 0.4025, "p75": 0.6075},
    },
    ("Indústria transformadora", "Grande"): {
        "liquidez_geral": {"p25": 1.0205, "p50": 1.355, "p75": 2.103},
        "liquidez_reduzida": {"p25": 0.6005, "p50": 0.927, "p75": 1.449},
        "solvabilidade": {"p25": 0.3249, "p50": 0.4782, "p75": 0.6453},
    },
    ("Indústria transformadora", "Micro"): {
        "liquidez_geral": {"p25": 0.69, "p50": 1.4825, "p75": 3.668},
        "liquidez_reduzida": {"p25": 0.484, "p50": 1.197, "p75": 3.078},
        "solvabilidade": {"p25": 0.2249, "p50": 0.4571, "p75": 0.7337},
    },
    ("Indústria transformadora", "Média"): {
        "liquidez_geral": {"p25": 1.07, "p50": 1.554, "p75": 2.5575},
        "liquidez_reduzida": {"p25": 0.642, "p50": 1.082, "p75": 1.8405},
        "solvabilidade": {"p25": 0.3163, "p50": 0.4853, "p75": 0.6773},
    },
    ("Indústria transformadora", "Pequena"): {
        "liquidez_geral": {"p25": 1.037, "p50": 1.592, "p75": 2.746},
        "liquidez_reduzida": {"p25": 0.655, "p50": 1.165, "p75": 2.128},
        "solvabilidade": {"p25": 0.2675, "p50": 0.4595, "p75": 0.6751},
    },
    ("Outro / Não especificado", "Grande"): {
        "liquidez_geral": {"p25": 0.687, "p50": 1.123, "p75": 1.8325},
        "liquidez_reduzida": {"p25": 0.589, "p50": 1.081, "p75": 1.7155},
        "solvabilidade": {"p25": 0.2003, "p50": 0.3918, "p75": 0.5774},
    },
    ("Outro / Não especificado", "Micro"): {
        "liquidez_geral": {"p25": 0.503, "p50": 1.472, "p75": 5.191},
        "liquidez_reduzida": {"p25": 0.286, "p50": 1.127, "p75": 3.971},
        "solvabilidade": {"p25": 0.2088, "p50": 0.4938, "p75": 0.8035},
    },
    ("Outro / Não especificado", "Média"): {
        "liquidez_geral": {"p25": 0.823, "p50": 1.257, "p75": 2.0615},
        "liquidez_reduzida": {"p25": 0.666, "p50": 1.128, "p75": 1.8005},
        "solvabilidade": {"p25": 0.2187, "p50": 0.4165, "p75": 0.6337},
    },
    ("Outro / Não especificado", "Pequena"): {
        "liquidez_geral": {"p25": 0.9672, "p50": 1.5195, "p75": 2.9547},
        "liquidez_reduzida": {"p25": 0.699, "p50": 1.22, "p75": 2.339},
        "solvabilidade": {"p25": 0.2126, "p50": 0.44, "p75": 0.6851},
    },
    ("Restauração e hotelaria", "Grande"): {
        "liquidez_geral": {"p25": 0.953, "p50": 1.297, "p75": 1.594},
        "liquidez_reduzida": {"p25": 0.87, "p50": 1.254, "p75": 1.536},
        "solvabilidade": {"p25": 0.2674, "p50": 0.3839, "p75": 0.5565},
    },
    ("Restauração e hotelaria", "Micro"): {
        "liquidez_geral": {"p25": 0.241, "p50": 0.877, "p75": 2.64},
        "liquidez_reduzida": {"p25": 0.165, "p50": 0.68, "p75": 2.306},
        "solvabilidade": {"p25": 0.1951, "p50": 0.4348, "p75": 0.7205},
    },
    ("Restauração e hotelaria", "Média"): {
        "liquidez_geral": {"p25": 0.5637, "p50": 1.0325, "p75": 1.9172},
        "liquidez_reduzida": {"p25": 0.5058, "p50": 0.935, "p75": 1.822},
        "solvabilidade": {"p25": 0.2892, "p50": 0.47, "p75": 0.6475},
    },
    ("Restauração e hotelaria", "Pequena"): {
        "liquidez_geral": {"p25": 0.666, "p50": 1.239, "p75": 2.438},
        "liquidez_reduzida": {"p25": 0.5667, "p50": 1.12, "p75": 2.265},
        "solvabilidade": {"p25": 0.2446, "p50": 0.4454, "p75": 0.6647},
    },
    ("Saúde e farmácia", "Grande"): {
        "liquidez_geral": {"p25": 0.4605, "p50": 0.607, "p75": 0.923},
        "liquidez_reduzida": {"p25": 0.3902, "p50": 0.5725, "p75": 0.8935},
        "solvabilidade": {"p25": 0.143, "p50": 0.3009, "p75": 0.524},
    },
    ("Saúde e farmácia", "Micro"): {
        "liquidez_geral": {"p25": 0.974, "p50": 2.8, "p75": 9.059},
        "liquidez_reduzida": {"p25": 0.931, "p50": 2.727, "p75": 8.8953},
        "solvabilidade": {"p25": 0.4013, "p50": 0.6985, "p75": 0.8962},
    },
    ("Saúde e farmácia", "Média"): {
        "liquidez_geral": {"p25": 0.6558, "p50": 1.1565, "p75": 2.0045},
        "liquidez_reduzida": {"p25": 0.6208, "p50": 1.107, "p75": 1.9547},
        "solvabilidade": {"p25": 0.3136, "p50": 0.6025, "p75": 0.8262},
    },
    ("Saúde e farmácia", "Pequena"): {
        "liquidez_geral": {"p25": 0.7572, "p50": 1.5, "p75": 3.1707},
        "liquidez_reduzida": {"p25": 0.7152, "p50": 1.4485, "p75": 3.1265},
        "solvabilidade": {"p25": 0.424, "p50": 0.6846, "p75": 0.8589},
    },
    ("Serviços profissionais", "Grande"): {
        "liquidez_geral": {"p25": 0.954, "p50": 1.296, "p75": 1.642},
        "liquidez_reduzida": {"p25": 0.881, "p50": 1.209, "p75": 1.642},
        "solvabilidade": {"p25": 0.2457, "p50": 0.3597, "p75": 0.5159},
    },
    ("Serviços profissionais", "Micro"): {
        "liquidez_geral": {"p25": 0.795, "p50": 1.858, "p75": 4.969},
        "liquidez_reduzida": {"p25": 0.708, "p50": 1.757, "p75": 4.737},
        "solvabilidade": {"p25": 0.2835, "p50": 0.559, "p75": 0.8092},
    },
    ("Serviços profissionais", "Média"): {
        "liquidez_geral": {"p25": 1.0097, "p50": 1.35, "p75": 1.8935},
        "liquidez_reduzida": {"p25": 0.922, "p50": 1.2845, "p75": 1.887},
        "solvabilidade": {"p25": 0.2429, "p50": 0.3926, "p75": 0.5774},
    },
    ("Serviços profissionais", "Pequena"): {
        "liquidez_geral": {"p25": 1.055, "p50": 1.5745, "p75": 2.583},
        "liquidez_reduzida": {"p25": 0.9962, "p50": 1.4905, "p75": 2.4698},
        "solvabilidade": {"p25": 0.2564, "p50": 0.4798, "p75": 0.6848},
    },
    ("Tecnologia e software", "Grande"): {
        "liquidez_geral": {"p25": 1.1285, "p50": 1.552, "p75": 1.9085},
        "liquidez_reduzida": {"p25": 1.125, "p50": 1.498, "p75": 1.8995},
        "solvabilidade": {"p25": 0.2415, "p50": 0.4095, "p75": 0.4959},
    },
    ("Tecnologia e software", "Micro"): {
        "liquidez_geral": {"p25": 0.843, "p50": 1.835, "p75": 4.625},
        "liquidez_reduzida": {"p25": 0.803, "p50": 1.796, "p75": 4.545},
        "solvabilidade": {"p25": 0.2996, "p50": 0.5657, "p75": 0.8041},
    },
    ("Tecnologia e software", "Média"): {
        "liquidez_geral": {"p25": 1.131, "p50": 1.469, "p75": 2.189},
        "liquidez_reduzida": {"p25": 1.114, "p50": 1.469, "p75": 2.098},
        "solvabilidade": {"p25": 0.2112, "p50": 0.4239, "p75": 0.6224},
    },
    ("Tecnologia e software", "Pequena"): {
        "liquidez_geral": {"p25": 1.09, "p50": 1.547, "p75": 2.462},
        "liquidez_reduzida": {"p25": 1.06, "p50": 1.524, "p75": 2.425},
        "solvabilidade": {"p25": 0.2445, "p50": 0.4309, "p75": 0.6328},
    },
    ("Transportes e logística", "Grande"): {
        "liquidez_geral": {"p25": 0.658, "p50": 1.074, "p75": 1.611},
        "liquidez_reduzida": {"p25": 0.649, "p50": 1.054, "p75": 1.566},
        "solvabilidade": {"p25": 0.2064, "p50": 0.3579, "p75": 0.5371},
    },
    ("Transportes e logística", "Micro"): {
        "liquidez_geral": {"p25": 0.475, "p50": 1.562, "p75": 5.868},
        "liquidez_reduzida": {"p25": 0.454, "p50": 1.522, "p75": 5.723},
        "solvabilidade": {"p25": 0.2557, "p50": 0.5431, "p75": 0.8374},
    },
    ("Transportes e logística", "Média"): {
        "liquidez_geral": {"p25": 0.84, "p50": 1.163, "p75": 1.8405},
        "liquidez_reduzida": {"p25": 0.809, "p50": 1.141, "p75": 1.8405},
        "solvabilidade": {"p25": 0.181, "p50": 0.3531, "p75": 0.55},
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
    Usa BENCHMARK_GERAL como fallback se não houver dados suficientes.
    """
    return BENCHMARKS.get((setor, dimensao), BENCHMARK_GERAL)
