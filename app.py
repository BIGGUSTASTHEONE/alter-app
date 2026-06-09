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
# SISTEMA DE DESIGN
# ---------------------------------------------------------------------------

NAVY     = "#0A2540"
CIANO    = "#41c3e0"   # acento estrutural (luminoso sobre fundo escuro)
TXT      = "#EAF2F8"   # texto primário sobre vidro escuro
TXT_DIM  = "#9FB3C8"   # texto secundário
TXT_MUTE = "#6B7E92"   # texto terciário / notas
VERDE    = "#34D399"   # confortável  (brilhante p/ fundo escuro)
AMBAR    = "#FBBF24"   # dentro da norma
VERMELHO = "#F87171"   # abaixo da norma

# Receita de vidro reutilizada nos cards
_GLASS = (
    "background:linear-gradient(160deg,rgba(255,255,255,0.07),rgba(255,255,255,0.028));"
    "border:1px solid rgba(255,255,255,0.10);"
    "backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);"
    "box-shadow:0 12px 38px rgba(3,12,24,0.50),inset 0 1px 0 rgba(255,255,255,0.08);"
)

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, .stApp {{
    background:
        radial-gradient(1200px 620px at 50% -12%, rgba(65,195,224,0.16), transparent 60%),
        radial-gradient(900px 500px at 100% 4%, rgba(65,195,224,0.07), transparent 55%),
        linear-gradient(180deg, #0C2C4B 0%, #08203A 42%, #061528 100%) !important;
    background-attachment: fixed !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}}

.block-container {{
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 880px !important;
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
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(65,195,224,0.55), transparent) !important;
    margin: 1.8rem 0 !important;
}}

/* Pills: estilo gerido por nivel_pills_selector() via session_state + CSS .st-key-* */

/* Botões — gradiente ciano luminoso */
.stButton > button {{
    background: linear-gradient(135deg, #4FCDEA 0%, #2BA3C6 100%) !important;
    color: #07263C !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 2rem !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 6px 22px rgba(65,195,224,0.40), inset 0 1px 0 rgba(255,255,255,0.35) !important;
    transition: all 0.18s ease !important;
}}
.stButton > button:hover {{
    background: linear-gradient(135deg, #6FE0F5 0%, #3FB8DA 100%) !important;
    box-shadow: 0 10px 34px rgba(65,195,224,0.58), inset 0 1px 0 rgba(255,255,255,0.45) !important;
    transform: translateY(-1px);
}}
.stButton > button:active {{
    transform: translateY(0px) !important;
}}

/* Inputs numéricos */
.stNumberInput > div > div > input {{
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    background: rgba(255,255,255,0.05) !important;
    backdrop-filter: blur(8px) !important;
    color: {TXT} !important;
    transition: all 0.16s ease !important;
}}
.stNumberInput > div > div > input:focus {{
    border-color: {CIANO} !important;
    box-shadow: 0 0 0 3px rgba(65,195,224,0.22) !important;
    outline: none !important;
}}

/* Selectbox */
.stSelectbox > div > div {{
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    background: rgba(255,255,255,0.05) !important;
    backdrop-filter: blur(8px) !important;
}}

/* File uploader */
[data-testid="stFileUploaderDropzone"] {{
    border-radius: 14px !important;
    border: 1.5px dashed rgba(65,195,224,0.40) !important;
    background: rgba(255,255,255,0.035) !important;
    backdrop-filter: blur(8px) !important;
    transition: all 0.18s ease !important;
}}
[data-testid="stFileUploaderDropzone"]:hover {{
    border-color: rgba(65,195,224,0.75) !important;
    background: rgba(65,195,224,0.06) !important;
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

/* Grelha de cards de resultados — 2x2, colapsa para 1 coluna no telemóvel */
.alter-cards {{
    display: grid !important;
    grid-template-columns: 1fr 1fr !important;
    gap: 18px !important;
    margin-bottom: 1.1rem !important;
}}
@media (max-width: 640px) {{
    .alter-cards {{ grid-template-columns: 1fr !important; }}
}}
</style>
"""


# ---------------------------------------------------------------------------
# COMPONENTES HTML
# ---------------------------------------------------------------------------

def step_header(titulo: str) -> str:
    return f"""
    <div style="display:flex;align-items:center;gap:13px;margin:2.2rem 0 1.2rem;">
        <div style="width:4px;height:22px;border-radius:4px;
                    background:linear-gradient(180deg,{CIANO},rgba(65,195,224,0.25));
                    box-shadow:0 0 14px rgba(65,195,224,0.65);"></div>
        <div style="font-size:1.08rem;font-weight:700;color:{TXT};
                    letter-spacing:-0.01em;">{titulo}</div>
    </div>
    """


def _cor_avaliacao(avaliacao: str) -> str:
    return {
        "confortável":    VERDE,
        "dentro da norma": AMBAR,
        "abaixo da norma": VERMELHO,
    }.get(avaliacao, CIANO)


def _label_avaliacao(avaliacao: str) -> str:
    return {
        "confortável":    "Confortável",
        "dentro da norma": "Dentro da norma",
        "abaixo da norma": "Abaixo da norma",
    }.get(avaliacao, avaliacao.title())


def card_racio(r: dict) -> str:
    cor   = _cor_avaliacao(r["avaliacao"])
    label = _label_avaliacao(r["avaliacao"])
    pct   = r["percentil"]          # melhor que pct% das empresas do setor
    top   = max(1, 100 - pct)       # posição relativa: "top X%"
    nota  = (
        f'<div style="font-size:0.64rem;color:{TXT_MUTE};margin-top:10px;'
        'font-style:italic;">Sem dados SABI para este setor — referência geral.</div>'
        if r.get("ref_geral") else ""
    )
    return f"""
    <div style="position:relative;overflow:hidden;border-radius:20px;
                padding:30px 32px 26px;{_GLASS}">
        <div style="position:absolute;top:0;left:0;right:0;height:3px;
                    background:linear-gradient(90deg,{cor},transparent 75%);
                    box-shadow:0 0 14px {cor}99;"></div>
        <div style="font-size:0.74rem;color:{TXT_DIM};font-weight:700;
                    letter-spacing:0.10em;text-transform:uppercase;margin-bottom:12px;">
            {r['racio']}
        </div>
        <div style="font-size:3.4rem;font-weight:800;color:{TXT};
                    line-height:1;letter-spacing:-0.02em;margin-bottom:8px;
                    text-shadow:0 0 26px rgba(65,195,224,0.30);">
            {r['valor']}
        </div>
        <div style="font-size:0.74rem;color:{TXT_MUTE};margin-bottom:18px;font-style:italic;">
            {r['formula']}
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="background:{cor}22;color:{cor};border:1px solid {cor}55;
                         padding:5px 13px;border-radius:20px;font-size:0.74rem;
                         font-weight:700;letter-spacing:0.04em;">
                {label.upper()}
            </span>
            <span style="font-size:0.9rem;color:{TXT_DIM};">
                top <strong style="color:{TXT};font-size:1.32rem;">{top}%</strong>
            </span>
        </div>
        <div style="background:rgba(255,255,255,0.08);border-radius:6px;
                    height:7px;margin-top:16px;overflow:hidden;">
            <div style="width:{pct}%;height:7px;border-radius:6px;
                        background:linear-gradient(90deg,{cor},{cor}AA);
                        box-shadow:0 0 12px {cor}99;"></div>
        </div>
        {nota}
    </div>
    """


def cards_grid(racios: list) -> str:
    cards = "".join(card_racio(r) for r in racios)
    return f'<div class="alter-cards">{cards}</div>'


def legenda_percentil() -> str:
    return f"""
    <div style="display:flex;gap:12px;align-items:flex-start;margin:0 0 2rem;
                padding:14px 18px;border-radius:14px;
                background:rgba(65,195,224,0.06);border:1px solid rgba(65,195,224,0.16);">
        <div style="flex:none;width:21px;height:21px;border-radius:50%;
                    background:{CIANO}26;border:1px solid {CIANO}66;color:{CIANO};
                    font-size:0.78rem;font-weight:800;line-height:21px;
                    text-align:center;font-style:italic;">i</div>
        <div style="font-size:0.82rem;color:{TXT_DIM};line-height:1.6;">
            <strong style="color:{TXT};">Como ler o "top X%":</strong>
            indica o posicionamento da empresa neste rácio face às empresas do
            mesmo setor e dimensão (dados SABI). Por exemplo,
            <strong style="color:{TXT};">top&nbsp;17%</strong> quer dizer que está
            entre as 17% melhores — ou seja, supera 83% das empresas.
            <strong style="color:{TXT};">Quanto menor a percentagem, melhor o posicionamento.</strong>
        </div>
    </div>
    """


def _md_to_html(texto: str) -> str:
    import re
    linhas = texto.split("\n")
    html_parts = []
    for linha in linhas:
        s = linha.strip()
        if not s:
            continue
        if s.startswith("### "):
            s = f'<h4 style="margin:1.1em 0 0.3em;color:{CIANO};font-size:1.18rem;font-weight:700;">{s[4:]}</h4>'
        elif s.startswith("## "):
            s = f'<h3 style="margin:1.2em 0 0.4em;color:{TXT};font-size:1.32rem;font-weight:700;">{s[3:]}</h3>'
        elif s.startswith("# "):
            s = f'<h2 style="margin:0 0 0.5em;color:{TXT};font-size:1.55rem;font-weight:800;letter-spacing:-0.01em;">{s[2:]}</h2>'
        elif s == "---":
            s = f'<hr style="border:none;border-top:1px solid rgba(255,255,255,0.12);margin:0.9em 0;">'
        else:
            s = re.sub(r'\*\*(.+?)\*\*', rf'<strong style="color:{TXT};font-weight:700;">\1</strong>', s)
            s = f'<p style="margin:0 0 0.85em 0;color:#C7D5E2;font-size:1.15rem;line-height:1.78;">{s}</p>'
        html_parts.append(s)
    return "".join(html_parts)


def diagnostico_card(texto: str) -> str:
    conteudo = _md_to_html(texto)
    return f"""
    <div style="position:relative;overflow:hidden;border-radius:20px;
                padding:30px 34px;{_GLASS}">
        <div style="position:absolute;top:0;left:0;bottom:0;width:3px;
                    background:linear-gradient(180deg,{CIANO},transparent 80%);
                    box-shadow:0 0 16px {CIANO}99;"></div>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:18px;">
            <span style="display:inline-block;width:7px;height:7px;border-radius:50%;
                         background:{CIANO};box-shadow:0 0 10px {CIANO};"></span>
            <span style="font-size:0.68rem;color:{CIANO};font-weight:700;
                         letter-spacing:0.12em;text-transform:uppercase;">
                Diagnóstico &nbsp;·&nbsp; IA
            </span>
        </div>
        <div style="font-size:1.15rem;">{conteudo}</div>
    </div>
    """


def _num_input(label: str, value: float) -> float:
    val = st.number_input(label, value=float(value), step=1.0, format="%.0f")
    st.markdown(
        f'<div style="font-size:0.72rem;color:#8BAAC4;margin-top:-0.7rem;margin-bottom:0.4rem;">'
        f'{val:,.0f} €</div>'.replace(",", "."),
        unsafe_allow_html=True,
    )
    return val


def fonte_caption() -> str:
    return f"""
    <div style="margin-top:1.8rem;padding-top:1rem;border-top:1px solid rgba(255,255,255,0.10);
                font-size:0.70rem;color:{TXT_MUTE};line-height:1.6;">
        Dados comparativos: {FONTE['nome']} &nbsp;&middot;&nbsp;
        Dados de {FONTE['ano_dados']} &nbsp;&middot;&nbsp;
        Consultado em {FONTE['data_consulta']} &nbsp;&middot;&nbsp;
        {FONTE['url']}
    </div>
    """


# ---------------------------------------------------------------------------
# SELECTOR DE NÍVEL DE LINGUAGEM (pills via session_state)
# ---------------------------------------------------------------------------

_OPCOES_PILLS = {
    "Simples":     {"nivel": 1, "slug": "simples",
                    "desc": "Linguagem do dia-a-dia, sem jargão — para quem não trabalha com finanças."},
    "Equilibrada": {"nivel": 2, "slug": "equilibrada",
                    "desc": "Alguns termos financeiros, sempre explicados — para gestores e empresários."},
    "Técnica":     {"nivel": 3, "slug": "tecnica",
                    "desc": "Terminologia SNC completa, sem explicar os conceitos — para analistas e contabilistas."},
}


def nivel_pills_selector(key: str = "nivel_pills", default: str = "Equilibrada") -> str:
    """
    Selector de pills robusto: estado em session_state.
    Estilo via .st-key-{slug} que o Streamlit adiciona ao container do botão —
    seletor mais específico que o CSS global, sem sentinelas nem :has().
    Retorna o nome da opção seleccionada.
    """
    if key not in st.session_state:
        st.session_state[key] = default

    current = st.session_state[key]

    st.markdown(
        f'<div style="color:#8BAAC4;font-weight:600;font-size:0.80rem;'
        f'letter-spacing:0.05em;text-transform:uppercase;margin-bottom:0.25rem;">'
        f'Nível de linguagem</div>'
        f'<div style="color:{TXT_MUTE};font-size:0.78rem;line-height:1.5;margin-bottom:0.7rem;">'
        f'A mesma análise em todos os níveis — muda só o estilo da explicação, '
        f'não a profundidade nem o rigor.</div>',
        unsafe_allow_html=True,
    )

    # CSS gerado por Python com base no estado actual — sem rastrear estado em CSS.
    # Acento único (ciano) para todos: é um espetro de estilo, não uma escala de qualidade.
    css_parts = []
    for nome, cfg in _OPCOES_PILLS.items():
        btn_key = f"{key}_{cfg['slug']}"
        if nome == current:
            style = (
                f"background:{CIANO} !important;"
                f"color:#07263C !important;"
                f"border:1px solid {CIANO} !important;"
                f"box-shadow:0 0 16px rgba(65,195,224,0.45) !important;"
            )
        else:
            style = (
                "background:rgba(255,255,255,0.05) !important;"
                "color:rgba(255,255,255,0.45) !important;"
                "border:1px solid rgba(255,255,255,0.14) !important;"
                "box-shadow:none !important;"
            )
        # .st-key-{btn_key} .stButton > button — especificidade (0,2,1) > (0,1,1) do CSS global
        css_parts.append(
            f".st-key-{btn_key} .stButton > button {{"
            f"{style}"
            f"border-radius:20px !important;"
            f"font-size:0.76rem !important;"
            f"font-weight:700 !important;"
            f"letter-spacing:0.04em !important;"
            f"text-transform:uppercase !important;"
            f"transition:all 0.18s !important;}}"
        )

    st.markdown(f"<style>{''.join(css_parts)}</style>", unsafe_allow_html=True)

    cols = st.columns(len(_OPCOES_PILLS))
    for col, (nome, cfg) in zip(cols, _OPCOES_PILLS.items()):
        with col:
            if st.button(nome, key=f"{key}_{cfg['slug']}", use_container_width=True):
                st.session_state[key] = nome
                st.rerun()

    # Eixo do espetro + descrição do nível seleccionado
    st.markdown(
        f'<div style="display:flex;justify-content:space-between;font-size:0.64rem;'
        f'color:{TXT_MUTE};text-transform:uppercase;letter-spacing:0.06em;'
        f'margin-top:0.55rem;">'
        f'<span>&larr; Mais acessível</span><span>Mais técnica &rarr;</span></div>'
        f'<div style="margin-top:0.7rem;padding:11px 15px;border-radius:12px;'
        f'background:rgba(65,195,224,0.07);border:1px solid rgba(65,195,224,0.18);'
        f'font-size:0.84rem;color:{TXT_DIM};line-height:1.55;">'
        f'<strong style="color:{TXT};">{current}.</strong> '
        f'{_OPCOES_PILLS[current]["desc"]}</div>',
        unsafe_allow_html=True,
    )

    return current


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
<div style="padding:1.8rem 0 1.4rem;border-bottom:1px solid rgba(65,195,224,0.22);margin-bottom:0.5rem;">
    <div style="display:flex;align-items:center;gap:12px;">
        <div style="font-size:2.35rem;font-weight:800;letter-spacing:0.10em;line-height:1;
                    color:#FFFFFF;">ALTER</div>
        <div style="color:{CIANO};font-size:0.85rem;line-height:1;
                    filter:drop-shadow(0 0 8px {CIANO});">◆</div>
    </div>
    <div style="width:52px;height:3px;border-radius:3px;margin-top:0.6rem;
                background:{CIANO};box-shadow:0 0 14px rgba(65,195,224,0.7);"></div>
    <div style="font-size:0.9rem;color:{TXT_DIM};margin-top:0.7rem;letter-spacing:0.01em;">
        Análise financeira inteligente — uma segunda opinião, sempre disponível.
    </div>
</div>
""", unsafe_allow_html=True)

if "dados_extraidos" not in st.session_state:
    st.session_state.dados_extraidos = None
if "texto_pdf" not in st.session_state:
    st.session_state.texto_pdf = None
if "resultados" not in st.session_state:
    st.session_state.resultados = None

# --- Passo 1: contexto ---
st.markdown(step_header("Contexto da empresa"), unsafe_allow_html=True)
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

nivel_str = nivel_pills_selector()
nivel_linguagem = _OPCOES_PILLS[nivel_str]["nivel"]

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
        ac    = _num_input("Ativo Corrente",    d.get("ativo_corrente")    or 0.0)
        inv   = _num_input("Inventários",       d.get("inventarios")       or 0.0)
        caixa = _num_input("Caixa e Depósitos", d.get("caixa_e_depositos") or 0.0)
    with col2:
        st.markdown(
            f"<div style='font-size:0.78rem;font-weight:700;color:#8BAAC4;"
            f"letter-spacing:0.05em;text-transform:uppercase;margin-bottom:0.6rem;"
            f"margin-top:0.4rem;'>Passivo e Capital</div>",
            unsafe_allow_html=True,
        )
        pc  = _num_input("Passivo Corrente",     d.get("passivo_corrente")     or 0.0)
        pnc = _num_input("Passivo Não Corrente", d.get("passivo_nao_corrente") or 0.0)
        cp  = _num_input("Capital Próprio",      d.get("capital_proprio")      or 0.0)

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
                texto_diag = gerar_diagnostico(
                    todos_racios,
                    "Liquidez e Solvabilidade",
                    setor, dimensao, nivel_linguagem,
                )

            # Guarda em session_state para os resultados sobreviverem a reruns
            st.session_state.resultados = {
                "racios": todos_racios,
                "diagnostico": texto_diag,
            }

# --- Resultados (renderizados fora do bloco do botão para persistirem) ---
if st.session_state.get("resultados"):
    res = st.session_state.resultados
    st.divider()
    st.markdown(step_header("Resultados"), unsafe_allow_html=True)
    st.markdown(cards_grid(res["racios"]), unsafe_allow_html=True)
    st.markdown(legenda_percentil(), unsafe_allow_html=True)
    st.markdown(diagnostico_card(res["diagnostico"]), unsafe_allow_html=True)
    st.markdown(fonte_caption(), unsafe_allow_html=True)
