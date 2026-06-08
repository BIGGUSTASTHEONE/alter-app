"""
app.py
Interface da aplicação Alter (Streamlit) e orquestração do fluxo.

Fluxo:
  0. Contexto: setor de atividade e nível de linguagem do diagnóstico.
  1. Entrada: upload do PDF.
  2. Extração: a IA lê o documento e propõe os dados.
  3. Confirmação: o utilizador vê e corrige os dados antes de avançar.
  4. Cálculo determinístico dos rácios (liquidez.py).
  5. Diagnóstico em linguagem natural pela IA, contextualizado pelo setor.
"""

import os
import streamlit as st
import pandas as pd
from anthropic import Anthropic
from dotenv import load_dotenv

import liquidez
import extracao

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


def gerar_diagnostico(racios, setor, nivel_linguagem):
    _, instrucao_linguagem = NIVEIS_LINGUAGEM[nivel_linguagem]
    linhas = "\n".join(
        f"- {r['racio']}: {r['valor']} ({r['avaliacao']})" for r in racios
    )
    instrucao = (
        f"És um analista financeiro a dar uma segunda opinião sobre a liquidez "
        f"de uma empresa do setor '{setor}'. "
        f"{instrucao_linguagem} "
        "Com base nos rácios calculados em baixo, escreve um diagnóstico em "
        "português europeu que identifique pontos fortes, sinais de alerta e uma "
        "conclusão. Contextualiza os valores face ao que é habitual no setor indicado. "
        "Não inventes valores nem outros rácios; usa apenas os que te são dados.\n\n"
        f"RÁCIOS DE LIQUIDEZ:\n{linhas}"
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

st.set_page_config(page_title="Alter", page_icon="📊")
st.title("Alter")
st.caption("Análise financeira inteligente. Uma segunda opinião, sempre disponível.")

if "dados_extraidos" not in st.session_state:
    st.session_state.dados_extraidos = None
if "texto_pdf" not in st.session_state:
    st.session_state.texto_pdf = None

# --- Passo 0: contexto ---
st.header("0. Contexto da empresa")
col1, col2 = st.columns(2)
with col1:
    setor = st.selectbox("Setor de atividade", SETORES, key="setor")
with col2:
    nivel_linguagem = st.select_slider(
        "Nível de linguagem do diagnóstico",
        options=[1, 2, 3],
        value=2,
        format_func=lambda x: NIVEIS_LINGUAGEM[x][0],
        key="nivel_linguagem",
    )

st.divider()

# --- Passo 1: entrada ---
st.header("1. Carregar balanço (PDF)")
ficheiro = st.file_uploader("Escolhe o PDF do balanço", type="pdf")

# --- Passo 2: extração ---
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
            with st.expander("Ver texto extraído do PDF (para diagnóstico)"):
                st.text(st.session_state.texto_pdf[:3000])
        else:
            st.info("PDF digitalizado — dados extraídos por visão computacional.")

# --- Passo 3: confirmação ---
if st.session_state.dados_extraidos is not None:
    st.header("2. Confirmar os dados")
    st.write(
        "Verifica os valores que a IA extraiu e corrige o que for preciso "
        "antes de avançar."
    )
    d = st.session_state.dados_extraidos

    ac = st.number_input("Ativo Corrente", value=float(d.get("ativo_corrente") or 0.0))
    pc = st.number_input("Passivo Corrente", value=float(d.get("passivo_corrente") or 0.0))
    inv = st.number_input("Inventários", value=float(d.get("inventarios") or 0.0))
    caixa = st.number_input("Caixa e Depósitos Bancários", value=float(d.get("caixa_e_depositos") or 0.0))

    # --- Passos 4 e 5: cálculo e diagnóstico ---
    if st.button("Analisar liquidez"):
        if pc == 0:
            st.error("O Passivo Corrente não pode ser zero (é o denominador dos rácios).")
        else:
            dados = {
                "ativo_corrente": ac,
                "passivo_corrente": pc,
                "inventarios": inv,
                "caixa_e_depositos": caixa,
            }
            racios = liquidez.analisar_liquidez(dados)

            st.header("3. Rácios de liquidez")
            tabela = pd.DataFrame(racios)
            tabela.columns = ["Rácio", "Fórmula", "Valor", "Avaliação"]
            st.table(tabela)

            st.subheader("Comparação visual")
            grafico = pd.DataFrame(
                {r["racio"]: [r["valor"]] for r in racios}
            ).T
            grafico.columns = ["Valor"]
            st.bar_chart(grafico)

            st.header("4. Diagnóstico")
            with st.spinner("A gerar o diagnóstico..."):
                st.write(gerar_diagnostico(racios, setor, nivel_linguagem))
