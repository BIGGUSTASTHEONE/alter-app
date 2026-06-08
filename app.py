"""
app.py
Interface da aplicação Alter (Streamlit) e orquestração do fluxo.

Segue o fluxo de seis etapas do projeto, por agora só com a categoria
de liquidez:
  1. Entrada: upload do PDF.
  2. Extração: a IA lê o documento e propõe os dados.
  3. Confirmação: o utilizador vê e corrige os dados antes de avançar.
  4. (Para já a liquidez é a única análise; a seleção entra quando
     houver mais categorias.)
  5. Cálculo determinístico dos rácios (liquidez.py).
  6. Diagnóstico em linguagem natural pela IA.
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


# ---------------------------------------------------------------------------
# PASSO 6 (parte da IA): gerar o diagnóstico a partir dos rácios já calculados
# A IA recebe números prontos. Não calcula nada, só interpreta.
# ---------------------------------------------------------------------------

def gerar_diagnostico(racios):
    linhas = "\n".join(
        f"- {r['racio']}: {r['valor']} ({r['avaliacao']})" for r in racios
    )
    instrucao = (
        "És um analista financeiro a dar uma segunda opinião sobre a liquidez "
        "de uma empresa. Com base nos rácios já calculados em baixo, escreve um "
        "diagnóstico curto em português europeu, claro e acessível a quem não "
        "domina finanças. Identifica pontos fortes, sinais de alerta e uma "
        "conclusão. Não inventes valores nem inventes outros rácios; usa apenas "
        "os que te são dados.\n\n"
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
# st.session_state guarda o estado entre cliques (o Streamlit recorre o
# script inteiro a cada interação; sem isto, os dados perdiam-se).
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Alter", page_icon="📊")
st.title("Alter")
st.caption("Análise financeira inteligente. Uma segunda opinião, sempre disponível.")

if "dados_extraidos" not in st.session_state:
    st.session_state.dados_extraidos = None
if "texto_pdf" not in st.session_state:
    st.session_state.texto_pdf = None

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

    # --- Passos 5 e 6: cálculo e diagnóstico ---
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
                st.write(gerar_diagnostico(racios))
