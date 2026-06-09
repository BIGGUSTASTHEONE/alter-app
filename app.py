"""
app.py
Interface da aplicação Alter (Streamlit) e orquestração do fluxo.

Fluxo:
  1. Contexto: setor de atividade, dimensão e nível de linguagem.
  2. Entrada: upload do PDF.
  3. Confirmação: o utilizador vê e corrige os dados antes de avançar.
  4. Resultados: cards de posicionamento sectorial + diagnóstico IA.
"""

import os
import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv

import liquidez
import solvabilidade
import extracao
from benchmarks import FONTE

load_dotenv()
cliente = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODELO_DIAGNOSTICO = "claude-sonnet-4-6"

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
# SISTEMA DE DESIGN
# ---------------------------------------------------------------------------

NAVY     = "#0A2540"
AZUL     = "#1D6FA4"
OURO     = "#C9912A"
BG       = "#0A2540"
VERDE    = "#1A7A4A"
AMBAR    = "#B45309"
VERMELHO = "#B91C1C"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, .stApp {{
    background-color: {BG} !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}}

.block-container {{
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 900px !important;
}}

#MainMenu, footer, header {{ visibility: hidden; }}

/* Labels dos inputs */
.stSelectbox label,
.stSlider label,
.stNumberInput label,
.stFileUploader label,
.stFileUploader p,
[data-testid="stFileUploaderDropzoneInstructions"] span {{
    color: #8BAAC4 !important;
    font-weight: 600 !important;
    font-size: 0.80rem !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
}}

/* Caption e texto secundário */
.stCaption, [data-testid="stCaptionContainer"] {{
    color: #6B7A8D !important;
}}

/* Divider */
hr {{
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.1) !important;
    margin: 1.8rem 0 !important;
}}

/* === Segmented control (radio horizontal → 3 segmentos) === */
[data-testid="stRadio"] [role="radiogroup"] {{
    gap: 4px !important;
    background: rgba(255,255,255,0.06) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    flex-direction: row !important;
}}
[data-testid="stRadio"] [role="radiogroup"] > label {{
    flex: 1 !important;
    border-radius: 7px !important;
    padding: 8px 2px !important;
    margin: 0 !important;
    justify-content: center !important;
    cursor: pointer !important;
    transition: background 0.15s, color 0.15s !important;
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
}}
/* Esconder o círculo do radio */
[data-testid="stRadio"] [data-baseweb="radio"] {{
    display: none !important;
}}
/* Cores por opção (estado inativo) */
[data-testid="stRadio"] [role="radiogroup"] > label:nth-child(1) {{
    color: #2D9B72 !important;
}}
[data-testid="stRadio"] [role="radiogroup"] > label:nth-child(2) {{
    color: {OURO} !important;
}}
[data-testid="stRadio"] [role="radiogroup"] > label:nth-child(3) {{
    color: {AZUL} !important;
}}

/* Botões — ouro sobre navy */
.stButton > button {{
    background-color: {OURO} !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.55rem 2rem !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 2px 12px rgba(201,145,42,0.35) !important;
    transition: all 0.18s !important;
}}
.stButton > button:hover {{
    background-color: #B8811F !important;
    box-shadow: 0 4px 18px rgba(201,145,42,0.45) !important;
    transform: translateY(-1px);
}}
.stButton > button:active {{
    transform: translateY(0px) !important;
}}

/* Inputs numéricos */
.stNumberInput > div > div > input {{
    border-radius: 8px !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    background: rgba(255,255,255,0.06) !important;
    color: white !important;
}}
.stNumberInput > div > div > input:focus {{
    border-color: {OURO} !important;
    box-shadow: 0 0 0 2px rgba(201,145,42,0.2) !important;
    outline: none !important;
}}

/* Selectbox */
.stSelectbox > div > div {{
    border-radius: 8px !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    background: rgba(255,255,255,0.06) !important;
}}

/* File uploader */
[data-testid="stFileUploaderDropzone"] {{
    border-radius: 10px !important;
    border: 1.5px dashed rgba(201,145,42,0.45) !important;
    background: rgba(255,255,255,0.04) !important;
}}

/* Expander */
.streamlit-expanderHeader,
[data-testid="stExpander"] summary {{
    color: #8BAAC4 !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
}}

/* Spinner */
[data-testid="stSpinner"] p {{
    color: #8BAAC4 !important;
}}

/* Alerts */
.stAlert {{
    border-radius: 10px !important;
}}
</style>
"""


# ---------------------------------------------------------------------------
# COMPONENTES HTML
# ---------------------------------------------------------------------------

def step_header(titulo: str) -> str:
    return f"""
    <div style="border-left:3px solid {OURO};padding-left:14px;margin:2rem 0 1.2rem;">
        <div style="font-size:1.05rem;font-weight:700;color:white;
                    letter-spacing:-0.01em;">{titulo}</div>
    </div>
    """


def _cor_avaliacao(avaliacao: str) -> str:
    return {
        "confortável":    VERDE,
        "dentro da norma": AMBAR,
        "abaixo da norma": VERMELHO,
    }.get(avaliacao, NAVY)


def _label_avaliacao(avaliacao: str) -> str:
    return {
        "confortável":    "Confortável",
        "dentro da norma": "Dentro da norma",
        "abaixo da norma": "Abaixo da norma",
    }.get(avaliacao, avaliacao.title())


def card_racio(r: dict) -> str:
    cor   = _cor_avaliacao(r["avaliacao"])
    label = _label_avaliacao(r["avaliacao"])
    pct   = r["percentil"]
    return f"""
    <div style="background:white;border-radius:12px;padding:22px 24px 18px;
                border-top:4px solid {cor};
                box-shadow:0 1px 3px rgba(10,37,64,0.06),0 2px 8px rgba(10,37,64,0.04);">
        <div style="font-size:0.70rem;color:#8A96A8;font-weight:700;
                    letter-spacing:0.08em;text-transform:uppercase;margin-bottom:8px;">
            {r['racio']}
        </div>
        <div style="font-size:2.4rem;font-weight:800;color:{NAVY};
                    line-height:1;letter-spacing:-0.02em;margin-bottom:6px;">
            {r['valor']}
        </div>
        <div style="font-size:0.72rem;color:#A0AEC0;margin-bottom:12px;font-style:italic;">
            {r['formula']}
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="background:{cor}18;color:{cor};border:1px solid {cor}40;
                         padding:3px 10px;border-radius:20px;font-size:0.73rem;
                         font-weight:700;letter-spacing:0.03em;">
                {label.upper()}
            </span>
            <span style="font-size:0.78rem;color:#8A96A8;">
                top <strong style="color:{NAVY};font-size:0.90rem;">{pct}%</strong>
            </span>
        </div>
        <div style="background:#EEF2F7;border-radius:4px;height:3px;margin-top:10px;">
            <div style="width:{pct}%;background:{cor};height:3px;border-radius:4px;"></div>
        </div>
    </div>
    """


def cards_grid(racios: list) -> str:
    cards = "".join(card_racio(r) for r in racios)
    return f"""
    <div style="display:grid;grid-template-columns:repeat(2,1fr);
                gap:14px;margin-bottom:2rem;">
        {cards}
    </div>
    """


def diagnostico_card(texto: str) -> str:
    paragrafos = "".join(
        f'<p style="margin:0 0 0.85em 0;color:{NAVY};line-height:1.78;">{p.strip()}</p>'
        for p in texto.split("\n") if p.strip()
    )
    return f"""
    <div style="background:white;border-radius:12px;padding:28px 32px;
                border-left:4px solid {OURO};
                box-shadow:0 1px 3px rgba(10,37,64,0.06),0 2px 8px rgba(10,37,64,0.04);">
        <div style="font-size:0.70rem;color:#8A96A8;font-weight:700;
                    letter-spacing:0.08em;text-transform:uppercase;margin-bottom:16px;">
            Diagnóstico &nbsp;·&nbsp; IA
        </div>
        <div style="font-size:0.95rem;">{paragrafos}</div>
    </div>
    """


def fonte_caption() -> str:
    return f"""
    <div style="margin-top:1.8rem;padding-top:1rem;border-top:1px solid #E2E8F0;
                font-size:0.70rem;color:#B0BAC8;line-height:1.6;">
        Dados comparativos: {FONTE['nome']} &nbsp;&middot;&nbsp;
        Dados de {FONTE['ano_dados']} &nbsp;&middot;&nbsp;
        Consultado em {FONTE['data_consulta']} &nbsp;&middot;&nbsp;
        {FONTE['url']}
    </div>
    """


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
        f"Não inventes valores nem outros rácios.\n\n"
        f"RÁCIOS DE {categoria.upper()}:\n{linhas}"
    )
    resposta = cliente.messages.create(
        model=MODELO_DIAGNOSTICO,
        max_tokens=700,
        messages=[{"role": "user", "content": instrucao}],
    )
    return resposta.content[0].text.strip()


# ---------------------------------------------------------------------------
# INTERFACE
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Alter", page_icon="◆", layout="centered")
st.markdown(CSS, unsafe_allow_html=True)

# Cabeçalho
st.markdown(f"""
<div style="padding:1.5rem 0 1.2rem;border-bottom:1px solid rgba(201,145,42,0.4);margin-bottom:0.5rem;">
    <div style="font-size:1.9rem;font-weight:800;color:white;
                letter-spacing:-0.03em;line-height:1;">
        ALTER
    </div>
    <div style="font-size:0.88rem;color:#6B7A8D;margin-top:0.4rem;letter-spacing:0.01em;">
        Análise financeira inteligente — uma segunda opinião, sempre disponível.
    </div>
</div>
""", unsafe_allow_html=True)

if "dados_extraidos" not in st.session_state:
    st.session_state.dados_extraidos = None
if "texto_pdf" not in st.session_state:
    st.session_state.texto_pdf = None

# --- Passo 1: contexto ---
st.markdown(step_header("Contexto da empresa"), unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
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
with col3:
    _OPCOES = {"Simples": (1, "#2D9B72"), "Equilibrada": (2, "#C9912A"), "Técnica": (3, "#1D6FA4")}
    nivel_str = st.radio(
        "Nível de linguagem",
        list(_OPCOES.keys()),
        index=1,
        horizontal=True,
        key="nivel_radio",
        help=(
            "**Simples** — linguagem acessível, sem jargão.\n\n"
            "**Equilibrada** — alguma terminologia financeira.\n\n"
            "**Técnica** — linguagem de especialista (analistas, contabilistas)."
        ),
    )
    nivel_linguagem, _cor = _OPCOES[nivel_str]
    _idx = list(_OPCOES.keys()).index(nivel_str) + 1
    st.markdown(f"""
    <style>
    /* Segmento ativo — preenche com a cor do nível */
    [data-testid="stRadio"] [role="radiogroup"] > label:nth-child({_idx}) {{
        background: {_cor} !important;
        color: white !important;
    }}
    [data-testid="stRadio"] [role="radiogroup"] > label:nth-child({_idx}) * {{
        color: white !important;
    }}
    </style>
    <div style="background:{_cor}22;border:1.5px solid {_cor}70;border-radius:8px;
                padding:7px 12px;text-align:center;margin-top:8px;">
        <span style="color:{_cor};font-weight:700;font-size:0.85rem;
                     letter-spacing:0.04em;">{nivel_str.upper()}</span>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --- Passo 2: upload ---
st.markdown(step_header("Carregar balanço (PDF)"), unsafe_allow_html=True)
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
    st.markdown(step_header("Confirmar os dados"), unsafe_allow_html=True)
    st.caption(
        "Verifica os valores que a IA extraiu e corrige o que for preciso antes de avançar."
    )
    d = st.session_state.dados_extraidos

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"<div style='font-size:0.78rem;font-weight:700;color:#8BAAC4;"
            f"letter-spacing:0.05em;text-transform:uppercase;margin-bottom:0.6rem;"
            f"margin-top:0.4rem;'>Ativo</div>",
            unsafe_allow_html=True,
        )
        ac    = st.number_input("Ativo Corrente",    value=float(d.get("ativo_corrente")    or 0.0))
        inv   = st.number_input("Inventários",       value=float(d.get("inventarios")       or 0.0))
        caixa = st.number_input("Caixa e Depósitos", value=float(d.get("caixa_e_depositos") or 0.0))
    with col2:
        st.markdown(
            f"<div style='font-size:0.78rem;font-weight:700;color:#8BAAC4;"
            f"letter-spacing:0.05em;text-transform:uppercase;margin-bottom:0.6rem;"
            f"margin-top:0.4rem;'>Passivo e Capital</div>",
            unsafe_allow_html=True,
        )
        pc  = st.number_input("Passivo Corrente",     value=float(d.get("passivo_corrente")     or 0.0))
        pnc = st.number_input("Passivo Não Corrente", value=float(d.get("passivo_nao_corrente") or 0.0))
        cp  = st.number_input("Capital Próprio",      value=float(d.get("capital_proprio")      or 0.0))

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

            st.divider()
            st.markdown(step_header("Resultados"), unsafe_allow_html=True)
            st.markdown(cards_grid(todos_racios), unsafe_allow_html=True)

            with st.spinner("A gerar o diagnóstico..."):
                texto_diag = gerar_diagnostico(
                    todos_racios,
                    "Liquidez e Solvabilidade",
                    setor, dimensao, nivel_linguagem,
                )
            st.markdown(diagnostico_card(texto_diag), unsafe_allow_html=True)
            st.markdown(fonte_caption(), unsafe_allow_html=True)
