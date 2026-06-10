"""
app.py
Orquestração do fluxo da aplicação Alter (Streamlit).

Fluxo:
  1. Contexto: setor de atividade, dimensão e nível de linguagem.
  2. Entrada: upload do PDF.
  3. Confirmação: o utilizador vê e corrige os dados antes de avançar.
  4. Resultados: cards de posicionamento sectorial + diagnóstico IA.

A apresentação (tokens de cor, CSS, componentes HTML) vive em ui.py;
o cálculo determinístico em liquidez.py e solvabilidade.py; a extração
de PDF em extracao.py.
"""

import os

import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv

import extracao
import liquidez
import solvabilidade
import ui
from config import MODELO_DIAGNOSTICO

load_dotenv()
cliente = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SETORES = [
    "Comércio a retalho",
    "Comércio por grosso",
    "Indústria transformadora",
    "Construção e imobiliário",
    "Serviços profissionais",
    "Restauração e hotelaria",
    "Tecnologia e software",
    "Saúde e farmácia",
    "Transportes e logística",
    "Agricultura e agro-indústria",
    "Outro / Não especificado",
]

NIVEIS_LINGUAGEM = {
    1: (
        "Simples",
        "Usa linguagem simples e acessível a alguém sem formação financeira. "
        "Evita jargão técnico. Explica os conceitos como se estivesses a falar "
        "com o dono de um pequeno negócio.",
    ),
    2: (
        "Equilibrada",
        "Usa linguagem moderadamente técnica, adequada a um gestor ou empresário "
        "com conhecimentos básicos de finanças.",
    ),
    3: (
        "Técnica",
        "Usa linguagem técnica e especializada, adequada a um analista financeiro "
        "ou contabilista. Podes usar terminologia SNC sem precisar de explicar os conceitos.",
    ),
}


# ---------------------------------------------------------------------------
# DIAGNÓSTICO
# ---------------------------------------------------------------------------

def gerar_diagnostico(racios, categoria, setor, dimensao, nivel_linguagem):
    _, instrucao_linguagem = NIVEIS_LINGUAGEM[nivel_linguagem]
    linhas = "\n".join(
        f"- {r['racio']}: {r['valor']} ({r['avaliacao']}, "
        f"melhor que {r['percentil']}% das empresas do setor)"
        for r in racios
    )
    instrucao = (
        f"És um analista financeiro a dar uma segunda opinião sobre a {categoria.lower()} "
        f"de uma empresa do setor '{setor}', de dimensão '{dimensao}'. "
        f"{instrucao_linguagem} "
        "Com base nos rácios e posições sectoriais calculados em baixo, escreve "
        "um diagnóstico em português europeu que identifique pontos fortes, sinais "
        "de alerta e uma conclusão. Os percentis são factos matemáticos calculados "
        "com dados do SABI — usa-os para contextualizar, mas não os recalcules "
        "nem os interpretes de forma diferente do que está indicado. "
        "Sê completo mas conciso (cerca de 300 a 450 palavras) e termina sempre a "
        "conclusão — não deixes frases a meio. "
        f"Não inventes valores nem outros rácios.\n\n"
        f"RÁCIOS DE {categoria.upper()}:\n{linhas}"
    )
    resposta = cliente.messages.create(
        model=MODELO_DIAGNOSTICO,
        max_tokens=1600,
        messages=[{"role": "user", "content": instrucao}],
    )
    return resposta.content[0].text.strip()


# ---------------------------------------------------------------------------
# INTERFACE
# ---------------------------------------------------------------------------

_ICONE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "alter-app-icon.svg")
st.set_page_config(page_title="Alter", page_icon=_ICONE, layout="centered")
st.markdown(ui.CSS, unsafe_allow_html=True)
st.markdown(ui.cabecalho(), unsafe_allow_html=True)

if "dados_extraidos" not in st.session_state:
    st.session_state.dados_extraidos = None
if "texto_pdf" not in st.session_state:
    st.session_state.texto_pdf = None
if "resultados" not in st.session_state:
    st.session_state.resultados = None

# --- Passo 1: contexto ---
st.markdown(ui.step_header("Contexto da empresa"), unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    setor = st.selectbox(
        "Setor de atividade",
        SETORES,
        key="setor",
        help=(
            "O setor é usado para contextualizar o diagnóstico — "
            "os rácios de referência variam bastante entre setores.\n\n"
            "*Exemplo: uma Liquidez Geral de 1.2 é normal no retalho "
            "(inventário rotativo) mas preocupante na indústria transformadora.*"
        ),
    )
with col2:
    dimensao = st.selectbox(
        "Dimensão da empresa",
        ["Micro", "Pequena", "Média", "Grande"],
        index=1,
        key="dimensao",
        help=(
            "Classificação EU/Portugal — basta cumprir dois dos três critérios:\n\n"
            "**Micro** — < 10 trabalhadores · VN ≤ 2 M€ · balanço ≤ 2 M€\n\n"
            "**Pequena** — < 50 trabalhadores · VN ≤ 10 M€ · balanço ≤ 10 M€\n\n"
            "**Média** — < 250 trabalhadores · VN ≤ 50 M€ · balanço ≤ 43 M€\n\n"
            "**Grande** — ≥ 250 trabalhadores ou VN > 50 M€ ou balanço > 43 M€"
        ),
    )

nivel_str = ui.nivel_pills_selector()
nivel_linguagem = ui.OPCOES_PILLS[nivel_str]["nivel"]

st.divider()

# --- Passo 2: upload ---
st.markdown(ui.step_header("Carregar balanço (PDF)"), unsafe_allow_html=True)
ficheiro = st.file_uploader(
    "Escolhe o PDF do balanço", type="pdf", label_visibility="collapsed"
)

if ficheiro is not None:
    if st.button("Extrair dados do balanço"):
        with st.spinner("A ler o documento e a extrair os dados..."):
            try:
                dados, texto = extracao.extrair_dados(ficheiro)
                st.session_state.dados_extraidos = dados
                st.session_state.texto_pdf = texto
                st.session_state.resultados = None  # invalida análise anterior
            except Exception as e:
                st.error(f"Erro na extração: {e}")

    if st.session_state.dados_extraidos is not None:
        if st.session_state.texto_pdf:
            with st.expander("Ver texto extraído do PDF"):
                st.text(st.session_state.texto_pdf[:3000])
        else:
            st.info("PDF digitalizado — dados extraídos por visão computacional.")

# --- Passo 3: confirmação ---
if st.session_state.dados_extraidos is not None:
    st.divider()
    st.markdown(ui.step_header("Confirmar os dados"), unsafe_allow_html=True)
    st.caption(
        "Verifica os valores que a IA extraiu e corrige o que for preciso antes de avançar."
    )
    d = st.session_state.dados_extraidos

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(ui.rotulo_coluna("Ativo"), unsafe_allow_html=True)
        ac    = ui.num_input("Ativo Corrente",    d.get("ativo_corrente")    or 0.0)
        inv   = ui.num_input("Inventários",       d.get("inventarios")       or 0.0)
        caixa = ui.num_input("Caixa e Depósitos", d.get("caixa_e_depositos") or 0.0)
    with col2:
        st.markdown(ui.rotulo_coluna("Passivo e Capital"), unsafe_allow_html=True)
        pc  = ui.num_input("Passivo Corrente",     d.get("passivo_corrente")     or 0.0)
        pnc = ui.num_input("Passivo Não Corrente", d.get("passivo_nao_corrente") or 0.0)
        cp  = ui.num_input("Capital Próprio",      d.get("capital_proprio")      or 0.0)

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

    # --- Passo 4: análise ---
    if st.button("Analisar"):
        erros = []
        if pc == 0:
            erros.append("O Passivo Corrente não pode ser zero.")
        if pc + pnc == 0:
            erros.append("O Passivo Total não pode ser zero.")
        if erros:
            for e in erros:
                st.error(e)
        else:
            racios_liq = liquidez.analisar_liquidez(
                {
                    "ativo_corrente":   ac,
                    "passivo_corrente": pc,
                    "inventarios":      inv,
                    "caixa_e_depositos": caixa,
                },
                setor, dimensao,
            )
            racios_solv = solvabilidade.analisar_solvabilidade(
                {
                    "capital_proprio":      cp,
                    "passivo_corrente":     pc,
                    "passivo_nao_corrente": pnc,
                },
                setor, dimensao,
            )
            todos_racios = racios_liq + racios_solv

            with st.spinner("A gerar o diagnóstico..."):
                try:
                    texto_diag = gerar_diagnostico(
                        todos_racios,
                        "Liquidez e Solvabilidade",
                        setor, dimensao, nivel_linguagem,
                    )
                except Exception as e:
                    # Os rácios são deterministas e já estão calculados —
                    # mostram-se na mesma; só o diagnóstico fica por gerar.
                    texto_diag = None
                    st.error(f"Não foi possível gerar o diagnóstico: {e}")

            # Guarda em session_state para os resultados sobreviverem a reruns
            st.session_state.resultados = {
                "racios": todos_racios,
                "diagnostico": texto_diag,
            }

# --- Resultados (renderizados fora do bloco do botão para persistirem) ---
if st.session_state.get("resultados"):
    res = st.session_state.resultados
    st.divider()
    st.markdown(ui.step_header("Resultados"), unsafe_allow_html=True)
    st.markdown(ui.cards_grid(res["racios"]), unsafe_allow_html=True)
    st.markdown(ui.legenda_percentil(), unsafe_allow_html=True)
    if res["diagnostico"]:
        st.markdown(ui.diagnostico_card(res["diagnostico"]), unsafe_allow_html=True)
    else:
        st.warning(
            "O diagnóstico não foi gerado (falha na chamada à API). "
            "Carrega em «Analisar» para tentar de novo — os rácios mantêm-se."
        )
    st.markdown(ui.fonte_caption(), unsafe_allow_html=True)
