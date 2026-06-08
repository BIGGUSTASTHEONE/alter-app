"""
importar_sabi.py
Utilitário para gerar benchmarks P25/P50/P75 a partir de um export do SABI.

COMO USAR:
1. No SABI, filtra as empresas portuguesas por setor (CAE) e dimensão
2. Exporta para Excel ou CSV com pelo menos estas colunas:
   - Nome ou identificador da empresa (qualquer coluna de ID)
   - CAE (código de actividade económica)
   - Dimensão (Micro / Pequena / Média / Grande)
   - Liquidez Geral   (Ativo Corrente / Passivo Corrente)
   - Liquidez Reduzida ((Ativo Corrente - Inventários) / Passivo Corrente)
   - Liquidez Imediata (Caixa e Depósitos / Passivo Corrente)  [opcional]

3. Ajusta o mapeamento COLUNAS abaixo com os nomes exactos das colunas do teu export
4. Ajusta o mapeamento CAE_PARA_SETOR com os CAE do teu export
5. Corre:  python importar_sabi.py caminho_para_o_ficheiro.xlsx
6. Copia o bloco BENCHMARKS gerado para benchmarks.py

Dependências: pandas, openpyxl (para Excel)
  pip install pandas openpyxl
"""

import sys
import pandas as pd

# ---------------------------------------------------------------------------
# MAPEAMENTO DE COLUNAS
# Ajusta com os nomes reais das colunas no teu export do SABI
# ---------------------------------------------------------------------------

COLUNAS = {
    "cae":               "CAE - Código Rev. 3",   # nome da coluna do CAE no SABI
    "dimensao":          "Dimensão",               # nome da coluna da dimensão
    "liquidez_geral":    "Rácio de liquidez geral",
    "liquidez_reduzida": "Rácio de liquidez reduzida",
    "liquidez_imediata": "Rácio de liquidez imediata",  # pode não existir — deixa None se não tiveres
}

# ---------------------------------------------------------------------------
# MAPEAMENTO CAE → SETOR DA INTERFACE
# Adiciona ou ajusta conforme os CAE presentes no teu export
# Formato: "CAE (2 dígitos ou descrição)" -> "Nome do setor na interface"
# ---------------------------------------------------------------------------

CAE_PARA_SETOR = {
    "47": "Comércio a retalho",
    "46": "Comércio por grosso",
    "41": "Construção e imobiliário",
    "42": "Construção e imobiliário",
    "43": "Construção e imobiliário",
    "55": "Restauração e hotelaria",
    "56": "Restauração e hotelaria",
    "62": "Tecnologia e software",
    "63": "Tecnologia e software",
    "69": "Serviços profissionais",
    "70": "Serviços profissionais",
    "71": "Serviços profissionais",
    "72": "Serviços profissionais",
    "73": "Serviços profissionais",
    "74": "Serviços profissionais",
    "75": "Serviços profissionais",
    "86": "Saúde e farmácia",
    "87": "Saúde e farmácia",
    "88": "Saúde e farmácia",
    "49": "Transportes e logística",
    "50": "Transportes e logística",
    "51": "Transportes e logística",
    "52": "Transportes e logística",
    "53": "Transportes e logística",
    "01": "Agricultura e agro-indústria",
    "02": "Agricultura e agro-indústria",
    "03": "Agricultura e agro-indústria",
}

# Indústria transformadora: CAE 10 a 33
for _cae in range(10, 34):
    CAE_PARA_SETOR[str(_cae)] = "Indústria transformadora"

# ---------------------------------------------------------------------------
# MAPEAMENTO DIMENSÃO SABI → DIMENSÃO DA INTERFACE
# Ajusta se o SABI usar nomes diferentes
# ---------------------------------------------------------------------------

DIMENSAO_MAP = {
    "micro":    "Micro",
    "pequena":  "Pequena",
    "média":    "Média",
    "media":    "Média",
    "grande":   "Grande",
}


def mapear_cae(cae_raw):
    """Extrai os dois primeiros dígitos do CAE e mapeia para o setor da interface."""
    cae_str = str(cae_raw).strip().zfill(5)
    prefixo = cae_str[:2]
    return CAE_PARA_SETOR.get(prefixo, "Outro / Não especificado")


def mapear_dimensao(dim_raw):
    return DIMENSAO_MAP.get(str(dim_raw).strip().lower(), str(dim_raw).strip())


def calcular_percentis(series):
    """Calcula P25, P50, P75 de uma série, ignorando nulos e outliers extremos."""
    s = series.dropna()
    s = s[(s > 0) & (s < s.quantile(0.99))]  # remove zeros e outliers extremos
    return {
        "p25": round(s.quantile(0.25), 4),
        "p50": round(s.quantile(0.50), 4),
        "p75": round(s.quantile(0.75), 4),
    }


def gerar_benchmarks(caminho):
    # Leitura do ficheiro
    if caminho.endswith(".csv"):
        df = pd.read_csv(caminho, decimal=",", thousands=".")
    else:
        df = pd.read_excel(caminho)

    # Mapeamento de colunas
    df["_setor"] = df[COLUNAS["cae"]].apply(mapear_cae)
    df["_dimensao"] = df[COLUNAS["dimensao"]].apply(mapear_dimensao)

    rácios = ["liquidez_geral", "liquidez_reduzida", "liquidez_imediata"]
    colunas_rácios = {r: COLUNAS[r] for r in rácios if COLUNAS.get(r) and COLUNAS[r] in df.columns}

    benchmarks = {}
    grupos = df.groupby(["_setor", "_dimensao"])

    for (setor, dimensao), grupo in grupos:
        entrada = {}
        for racio, coluna in colunas_rácios.items():
            try:
                entrada[racio] = calcular_percentis(pd.to_numeric(grupo[coluna], errors="coerce"))
            except Exception:
                pass
        if entrada:
            benchmarks[(setor, dimensao)] = entrada

    # Output formatado para colar em benchmarks.py
    print("\n# --- BENCHMARKS GERADOS DO SABI ---")
    print(f"# Ficheiro: {caminho}")
    print(f"# Empresas analisadas: {len(df)}")
    print(f"# Combinações setor+dimensão: {len(benchmarks)}")
    print("\nBENCHMARKS = {")
    for (setor, dimensao), entrada in sorted(benchmarks.items()):
        print(f'    ("{setor}", "{dimensao}"): {{')
        for racio, vals in entrada.items():
            print(f'        "{racio}": {{"p25": {vals["p25"]}, "p50": {vals["p50"]}, "p75": {vals["p75"]}}},')
        print("    },")
    print("}")

    return benchmarks


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python importar_sabi.py caminho_para_ficheiro.xlsx")
        sys.exit(1)
    gerar_benchmarks(sys.argv[1])
