"""
importar_sabi.py
Processa até 3 exports do SABI e gera benchmarks P25/P50/P75
para liquidez e solvabilidade, com classificação de dimensão automática.

COMO USAR:
  python importar_sabi.py bloco1.xlsx bloco2.xlsx bloco3.xlsx

Os ficheiros são fundidos antes de calcular os percentis.
Copia o bloco BENCHMARKS gerado para benchmarks.py.

Dependências: pandas, openpyxl
  pip install pandas openpyxl
"""

import sys
import pandas as pd

# ---------------------------------------------------------------------------
# MAPEAMENTO CAE → SETOR DA INTERFACE
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
for _c in range(10, 34):
    CAE_PARA_SETOR[str(_c)] = "Indústria transformadora"


def mapear_cae(cae_raw):
    cae_str = str(cae_raw).strip().zfill(5)
    return CAE_PARA_SETOR.get(cae_str[:2], "Outro / Não especificado")


def classificar_dimensao(empregados, vendas_keur, activo_keur):
    """
    Classifica a dimensão da empresa segundo os critérios EU (2 de 3).
    vendas_keur e activo_keur estão em milhares de EUR (th EUR) — formato SABI.
    """
    try:
        e = float(empregados)
        v = float(vendas_keur) * 1000   # th EUR → EUR
        a = float(activo_keur) * 1000
    except (ValueError, TypeError):
        return None

    micro   = [e < 10,  v <= 2e6,  a <= 2e6]
    pequena = [e < 50,  v <= 10e6, a <= 10e6]
    media   = [e < 250, v <= 50e6, a <= 43e6]

    if sum(micro) >= 2:   return "Micro"
    if sum(pequena) >= 2: return "Pequena"
    if sum(media) >= 2:   return "Média"
    return "Grande"


def encontrar_coluna(df, *padroes):
    """Devolve a primeira coluna cujo nome contenha algum dos padrões (case-insensitive)."""
    for padrao in padroes:
        p = padrao.lower()
        for col in df.columns:
            if p in col.lower():
                return col
    return None


def calcular_percentis(series):
    """P25/P50/P75 removendo nulos e outliers acima do P99. Mínimo de 30 observações."""
    s = pd.to_numeric(series, errors="coerce").dropna()
    if len(s) < 30:
        return None
    s = s[(s > 0) & (s < s.quantile(0.99))]
    if len(s) < 30:
        return None
    return {
        "p25": round(float(s.quantile(0.25)), 4),
        "p50": round(float(s.quantile(0.50)), 4),
        "p75": round(float(s.quantile(0.75)), 4),
    }


def ler_ficheiro(caminho):
    if caminho.lower().endswith((".csv", ".txt")):
        return pd.read_csv(caminho, decimal=",", thousands=".", sep=None, engine="python")
    # SABI exporta para a folha "Resultados"; normaliza nomes de colunas (remove \n)
    xl = pd.ExcelFile(caminho)
    sheet = "Resultados" if "Resultados" in xl.sheet_names else xl.sheet_names[0]
    df = pd.read_excel(caminho, sheet_name=sheet)
    df.columns = [str(c).replace("\n", " ").strip() for c in df.columns]
    return df


def gerar_benchmarks(caminhos):
    # Lê e funde todos os ficheiros
    frames = [ler_ficheiro(c) for c in caminhos]
    df = pd.concat(frames, ignore_index=True)
    print(f"# Linhas após merge (antes de deduplicar): {len(df)}")
    df = df.drop_duplicates()
    print(f"# Empresas únicas: {len(df)}")

    # Detecção automática de colunas
    col_cae    = encontrar_coluna(df, "cae rev.4", "cae rev.3", "cae")
    col_emp    = encontrar_coluna(df, "empregados", "trabalhadores", "employees")
    col_activo = encontrar_coluna(df, "total do activo", "total activo", "total do ativo")
    col_vendas = encontrar_coluna(df, "servi", "vendas e serv", "proveitos operac")
    col_liq_r  = encontrar_coluna(df, "liquidez corrente", "liquidez reduzida")
    col_liq_g  = encontrar_coluna(df, "racio de liquidez %", "liquidez geral")
    if col_liq_g == col_liq_r:
        col_liq_g = None
    col_solv   = encontrar_coluna(df, "solvabilidade")

    print("\n# Colunas detectadas:")
    for nome, col in [
        ("CAE",           col_cae),
        ("Empregados",    col_emp),
        ("Total activo",  col_activo),
        ("Vendas",        col_vendas),
        ("Liq. Geral",    col_liq_g),
        ("Liq. Reduzida", col_liq_r),
        ("Solvabilidade", col_solv),
    ]:
        print(f"#   {nome:15s}: {col or 'NÃO ENCONTRADA'}")

    if not col_cae:
        raise ValueError("Coluna CAE não encontrada. Verifica os nomes das colunas no ficheiro.")
    if not (col_emp and col_activo and col_vendas):
        raise ValueError("Colunas de dimensão (empregados/activo/vendas) não encontradas.")

    # Classificação de setor e dimensão
    df["_setor"] = df[col_cae].apply(mapear_cae)
    df["_dimensao"] = df.apply(
        lambda r: classificar_dimensao(r[col_emp], r[col_activo], r[col_vendas]),
        axis=1,
    )
    df = df.dropna(subset=["_dimensao"])
    print(f"\n# Empresas com dimensão classificável: {len(df)}")
    print(f"# Distribuição por dimensão:\n{df['_dimensao'].value_counts().to_string()}")

    # SABI: "liquidez corrente" = Liquidez Geral (Ativo Corrente / Passivo Corrente)
    #        "liquidez" (sem qualif.) = Liquidez Reduzida
    #        "solvabilidade" está em percentagem — dividir por 100
    racios = {}
    if col_liq_r:  racios["liquidez_geral"]    = col_liq_r          # corrente → geral
    if col_liq_g:  racios["liquidez_reduzida"] = col_liq_g          # liquidez → reduzida
    if col_solv:
        df[col_solv] = pd.to_numeric(df[col_solv], errors="coerce") / 100
        racios["solvabilidade"] = col_solv

    if not racios:
        raise ValueError("Nenhuma coluna de rácio encontrada.")

    # Cálculo dos percentis por setor+dimensão
    benchmarks = {}
    for (setor, dimensao), grupo in df.groupby(["_setor", "_dimensao"]):
        entrada = {}
        for racio, coluna in racios.items():
            p = calcular_percentis(grupo[coluna])
            if p:
                entrada[racio] = p
        if entrada:
            benchmarks[(setor, dimensao)] = entrada

    # Output formatado para colar em benchmarks.py
    print(f"\n# Combinações setor+dimensão com dados suficientes: {len(benchmarks)}")
    print("\n# --- COLA ISTO EM benchmarks.py ---\n")
    print("BENCHMARKS = {")
    for (setor, dimensao), entrada in sorted(benchmarks.items()):
        print(f'    ("{setor}", "{dimensao}"): {{')
        for racio, vals in entrada.items():
            print(f'        "{racio}": {{"p25": {vals["p25"]}, "p50": {vals["p50"]}, "p75": {vals["p75"]}}},')
        print("    },")
    print("}")

    return benchmarks


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python importar_sabi.py bloco1.xlsx [bloco2.xlsx] [bloco3.xlsx]")
        sys.exit(1)
    gerar_benchmarks(sys.argv[1:])
