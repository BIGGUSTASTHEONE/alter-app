"""
ui.py
Sistema de design e componentes visuais da aplicação Alter.

Tokens de cor, CSS global e componentes HTML: cabeçalho, step headers,
cards de rácio, legenda do percentil, card do diagnóstico, inputs e o
selector de nível de linguagem. Sem lógica de negócio nem chamadas à API —
a apresentação serve a comparação, não a calcula.
"""

import re

import streamlit as st

from benchmarks import FONTE

# ---------------------------------------------------------------------------
# TOKENS DE COR
# ---------------------------------------------------------------------------

NAVY     = "#0A2540"
CIANO    = "#41c3e0"   # acento estrutural (luminoso sobre fundo escuro)
TXT      = "#EAF2F8"   # texto primário sobre vidro escuro
TXT_DIM  = "#9FB3C8"   # texto secundário
TXT_MUTE = "#6B7E92"   # texto terciário / notas
ROXO     = "#A88BFF"   # confortável      (violeta-periwinkle, frio p/ condizer com o cian)
VERDE    = "#34D399"   # dentro da norma  (esmeralda limpo)
VERMELHO = "#F2607E"   # abaixo da norma  (magenta-coral)

# Receita de vidro reutilizada nos cards
_GLASS = (
    "background:linear-gradient(160deg,rgba(255,255,255,0.07),rgba(255,255,255,0.028));"
    "border:1px solid rgba(255,255,255,0.10);"
    "backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);"
    "box-shadow:0 12px 38px rgba(3,12,24,0.50),inset 0 1px 0 rgba(255,255,255,0.08);"
)

# ---------------------------------------------------------------------------
# CSS GLOBAL
# ---------------------------------------------------------------------------

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, .stApp {{
    background:
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cg fill='none' stroke='%2341c3e0' stroke-width='0.7' stroke-linejoin='round' opacity='0.05'%3E%3Cpolygon points='40,26 70,56 40,86 10,56'/%3E%3Cpolygon points='62,14 92,44 62,74 32,44'/%3E%3C/g%3E%3C/svg%3E") calc(100% + 170px) -120px / 580px 580px no-repeat,
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
# CABEÇALHO E ESTRUTURA
# ---------------------------------------------------------------------------

def simbolo_svg(tamanho: int = 60, fid: str = "gAlt") -> str:
    """Símbolo da marca (dois losangos entrelaçados) como SVG inline.
    `fid` tem de ser único por instância na página — ids de filtro repetidos
    no DOM fazem o glow falhar em alguns browsers."""
    return (
        f'<svg width="{tamanho}" height="{tamanho}" viewBox="0 0 100 100" '
        f'role="img" aria-label="ALTER" style="flex:none;display:block;">'
        f'<defs><filter id="{fid}" x="-40%" y="-40%" width="180%" height="180%">'
        f'<feGaussianBlur stdDeviation="2.2" result="b"/>'
        f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
        f'</filter></defs>'
        f'<g filter="url(#{fid})">'
        f'<polygon points="40,26 70,56 40,86 10,56" fill="{CIANO}" fill-opacity="0.14" '
        f'stroke="{CIANO}" stroke-width="3" stroke-linejoin="round"/>'
        f'<polygon points="62,14 92,44 62,74 32,44" fill="{CIANO}" fill-opacity="0.18" '
        f'stroke="{CIANO}" stroke-width="3" stroke-linejoin="round"/>'
        f'</g></svg>'
    )


def cabecalho() -> str:
    return f"""
    <div style="display:flex;align-items:center;gap:20px;padding:1.6rem 0 1.5rem;
                border-bottom:1px solid rgba(65,195,224,0.22);margin-bottom:0.5rem;">
        <div style="filter:drop-shadow(0 8px 22px rgba(65,195,224,0.30));">{simbolo_svg(70, "gAlcab")}</div>
        <div style="display:inline-block;">
            <div style="font-size:2.35rem;font-weight:800;letter-spacing:0.10em;line-height:1;
                        color:#FFFFFF;
                        text-shadow:0 0 7px rgba(255,255,255,0.35),
                                    0 0 18px rgba(65,195,224,0.50),
                                    0 0 34px rgba(65,195,224,0.32);">ALTER</div>
            <div style="width:100%;height:3px;border-radius:3px;margin-top:0.55rem;
                        background:{CIANO};
                        box-shadow:0 0 10px rgba(65,195,224,0.85),
                                   0 0 22px rgba(65,195,224,0.6),
                                   0 0 38px rgba(65,195,224,0.35);"></div>
            <div style="font-size:0.9rem;color:{TXT_DIM};margin-top:0.65rem;letter-spacing:0.01em;">
                Análise financeira inteligente — uma segunda opinião, sempre disponível.
            </div>
        </div>
    </div>
    """


def step_header(titulo: str) -> str:
    return f"""
    <div style="display:flex;align-items:center;gap:14px;margin:2.2rem 0 1.2rem;">
        <div style="flex:none;width:12px;height:12px;transform:rotate(45deg);
                    border-radius:2.5px;background:rgba(65,195,224,0.16);
                    border:2px solid {CIANO};
                    box-shadow:0 0 12px rgba(65,195,224,0.55);"></div>
        <div style="font-size:1.08rem;font-weight:700;color:{TXT};
                    letter-spacing:-0.01em;
                    text-shadow:0 0 18px rgba(65,195,224,0.28);">{titulo}</div>
    </div>
    """


def rotulo_coluna(texto: str) -> str:
    """Rótulo de secção em maiúsculas (ex.: 'Ativo', 'Passivo e Capital')."""
    return (
        f"<div style='font-size:0.78rem;font-weight:700;color:#8BAAC4;"
        f"letter-spacing:0.05em;text-transform:uppercase;margin-bottom:0.6rem;"
        f"margin-top:0.4rem;'>{texto}</div>"
    )


# ---------------------------------------------------------------------------
# CARDS DE RESULTADOS
# ---------------------------------------------------------------------------

def _cor_avaliacao(avaliacao: str) -> str:
    return {
        "confortável":    ROXO,
        "dentro da norma": VERDE,
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
                    text-shadow:0 0 30px {cor}59,0 0 12px {cor}33;">
            {r['valor']}
        </div>
        <div style="font-size:0.74rem;color:{TXT_MUTE};margin-bottom:18px;font-style:italic;">
            {r['formula']}
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="background:{cor}22;color:{cor};border:1px solid {cor}66;
                         padding:5px 13px;border-radius:20px;font-size:0.74rem;
                         font-weight:700;letter-spacing:0.04em;
                         box-shadow:0 0 16px {cor}55,inset 0 0 10px {cor}1F;
                         text-shadow:0 0 12px {cor}AA;">
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


def _flat(html: str) -> str:
    """Colapsa o HTML numa única linha (sem linhas em branco).
    O markdown do Streamlit parte um bloco HTML quando encontra uma linha
    vazia — ao juntar cards isso acontecia e o resto era mostrado como código."""
    return "".join(linha.strip() for linha in html.splitlines())


def cards_grid(racios: list) -> str:
    cards = "".join(_flat(card_racio(r)) for r in racios)
    return f'<div class="alter-cards">{cards}</div>'


def legenda_percentil() -> str:
    return f"""
    <div style="display:flex;gap:12px;align-items:flex-start;margin:0 0 2rem;
                padding:14px 18px;border-radius:14px;
                background:rgba(65,195,224,0.06);border:1px solid rgba(65,195,224,0.16);">
        <div style="flex:none;width:19px;height:19px;transform:rotate(45deg);
                    border-radius:4px;background:{CIANO}26;border:1px solid {CIANO}66;
                    margin:3px 4px 0 3px;display:flex;align-items:center;
                    justify-content:center;">
            <span style="transform:rotate(-45deg);color:{CIANO};font-size:0.74rem;
                         font-weight:800;font-style:italic;line-height:1;">i</span>
        </div>
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


# ---------------------------------------------------------------------------
# DIAGNÓSTICO (markdown controlado → HTML estilizado)
# ---------------------------------------------------------------------------

_RE_ITEM_ORDENADO = re.compile(r"^\d+[.)]\s+")


def _negrito(s: str) -> str:
    return re.sub(
        r"\*\*(.+?)\*\*",
        rf'<strong style="color:{TXT};font-weight:700;">\1</strong>',
        s,
    )


def _md_to_html(texto: str) -> str:
    """Converte o markdown que o modelo produz em HTML estilizado.
    Suporta títulos (#/##/###), negrito, separadores (---) e listas
    (marcas '- ', '* ' e '1.' — agrupadas em <ul>/<ol>)."""
    html_parts = []
    lista = None  # tag da lista aberta ("ul"/"ol") ou None

    def fechar_lista():
        nonlocal lista
        if lista:
            html_parts.append(f"</{lista}>")
            lista = None

    for linha in texto.split("\n"):
        s = linha.strip()
        if not s:
            continue

        e_ul = s.startswith(("- ", "* "))
        e_ol = bool(_RE_ITEM_ORDENADO.match(s))
        if e_ul or e_ol:
            tipo = "ul" if e_ul else "ol"
            conteudo = s[2:].strip() if e_ul else _RE_ITEM_ORDENADO.sub("", s)
            if lista != tipo:
                fechar_lista()
                html_parts.append(
                    f'<{tipo} style="margin:0 0 0.85em;padding-left:1.35em;">'
                )
                lista = tipo
            html_parts.append(
                f'<li style="color:#C7D5E2;font-size:1.15rem;line-height:1.78;'
                f'margin:0 0 0.3em;">{_negrito(conteudo)}</li>'
            )
            continue

        fechar_lista()
        if s.startswith("### "):
            html_parts.append(
                f'<h4 style="margin:1.1em 0 0.3em;color:{CIANO};'
                f'font-size:1.18rem;font-weight:700;'
                f'text-shadow:0 0 16px {CIANO}66;">{_negrito(s[4:])}</h4>'
            )
        elif s.startswith("## "):
            html_parts.append(
                f'<h3 style="margin:1.2em 0 0.4em;color:{TXT};'
                f'font-size:1.32rem;font-weight:700;'
                f'text-shadow:0 0 20px rgba(65,195,224,0.26);">{_negrito(s[3:])}</h3>'
            )
        elif s.startswith("# "):
            html_parts.append(
                f'<h2 style="margin:0 0 0.5em;color:{TXT};font-size:1.55rem;'
                f'font-weight:800;letter-spacing:-0.01em;'
                f'text-shadow:0 0 26px rgba(65,195,224,0.32);">{_negrito(s[2:])}</h2>'
            )
        elif s == "---":
            html_parts.append(
                '<hr style="border:none;border-top:1px solid rgba(255,255,255,0.12);'
                'margin:0.9em 0;">'
            )
        else:
            html_parts.append(
                f'<p style="margin:0 0 0.85em 0;color:#C7D5E2;font-size:1.15rem;'
                f'line-height:1.78;">{_negrito(s)}</p>'
            )

    fechar_lista()
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
            <span style="display:inline-block;width:8px;height:8px;transform:rotate(45deg);
                         border-radius:1.5px;background:{CIANO};box-shadow:0 0 10px {CIANO};"></span>
            <span style="font-size:0.68rem;color:{CIANO};font-weight:700;
                         letter-spacing:0.12em;text-transform:uppercase;">
                Diagnóstico &nbsp;·&nbsp; IA
            </span>
        </div>
        <div style="font-size:1.15rem;">{conteudo}</div>
    </div>
    """


# ---------------------------------------------------------------------------
# INPUTS E RODAPÉ
# ---------------------------------------------------------------------------

def num_input(label: str, value: float) -> float:
    """st.number_input com caption do valor formatado (separadores de milhares)."""
    val = st.number_input(label, value=float(value), step=1.0, format="%.0f")
    st.markdown(
        f'<div style="font-size:0.72rem;color:#8BAAC4;margin-top:-0.7rem;margin-bottom:0.4rem;">'
        f'{val:,.0f} €</div>'.replace(",", "."),
        unsafe_allow_html=True,
    )
    return val


def fonte_caption() -> str:
    return f"""
    <div style="margin-top:2.2rem;padding-top:1.2rem;border-top:1px solid rgba(255,255,255,0.10);">
        <div style="display:flex;align-items:center;gap:9px;margin-bottom:0.55rem;">
            {simbolo_svg(22, "gAlfoot")}
            <span style="font-size:0.78rem;font-weight:800;letter-spacing:0.10em;
                         color:{TXT_DIM};">ALTER</span>
        </div>
        <div style="font-size:0.70rem;color:{TXT_MUTE};line-height:1.6;">
            Dados comparativos: {FONTE['nome']} &nbsp;&middot;&nbsp;
            Dados de {FONTE['ano_dados']} &nbsp;&middot;&nbsp;
            Consultado em {FONTE['data_consulta']} &nbsp;&middot;&nbsp;
            {FONTE['url']}
        </div>
    </div>
    """


# ---------------------------------------------------------------------------
# SELECTOR DE NÍVEL DE LINGUAGEM (pills via session_state)
# ---------------------------------------------------------------------------

# "nivel" corresponde às chaves de NIVEIS_LINGUAGEM em app.py.
OPCOES_PILLS = {
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
    for nome, cfg in OPCOES_PILLS.items():
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

    cols = st.columns(len(OPCOES_PILLS))
    for col, (nome, cfg) in zip(cols, OPCOES_PILLS.items()):
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
        f'{OPCOES_PILLS[current]["desc"]}</div>',
        unsafe_allow_html=True,
    )

    return current
