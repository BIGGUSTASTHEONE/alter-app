"""
extracao.py
Extrai dados financeiros de um balanço em PDF usando a API da Anthropic.

Duas vias de extração, escolhidas automaticamente:
- Texto: PyMuPDF lê o texto do PDF (PDFs digitais). Mais barato.
- Visão: páginas renderizadas como imagem e enviadas ao Claude (PDFs digitalizados).

A única função pública é extrair_dados(). O resto é interno.
"""

import os
import json
import base64
import fitz  # PyMuPDF
from anthropic import Anthropic
from dotenv import load_dotenv

from config import MODELO_EXTRACAO as MODELO

load_dotenv()

# Limites de custo e robustez da extração:
# - visão: só as primeiras páginas (o balanço vem no início das demonstrações)
# - texto: tecto de caracteres enviados à API em documentos muito longos
MAX_PAGINAS_VISAO = 10
MAX_CARACTERES_TEXTO = 150_000

# Mínimo de caracteres para considerar que o PDF tem camada de texto utilizável;
# abaixo disto assume-se documento digitalizado e usa-se a via de visão.
MIN_CARACTERES_TEXTO = 150

_cliente = None


def _obter_cliente():
    """Cliente da API criado na primeira utilização — permite importar o módulo
    sem chave de API configurada (ex.: nos testes da lógica pura)."""
    global _cliente
    if _cliente is None:
        _cliente = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _cliente

_INSTRUCAO_CAMPOS = (
    "És um extrator de dados financeiros. "
    "Identifica e devolve os seis valores seguintes do balanço, "
    "em euros, como números (sem símbolos de moeda nem separadores de milhares):\n\n"
    "- ativo_corrente: 'Ativo corrente', 'Total ativo corrente', 'Activo circulante'\n"
    "- passivo_corrente: 'Passivo corrente', 'Total passivo corrente'\n"
    "- inventarios: 'Inventários', 'Existências', 'Mercadorias', 'Matérias-primas'\n"
    "- caixa_e_depositos: 'Caixa e depósitos bancários', 'Disponibilidades', 'Caixa'\n"
    "- capital_proprio: 'Capital próprio', 'Total capital próprio', 'Capitais próprios'\n"
    "- passivo_nao_corrente: 'Passivo não corrente', 'Total passivo não corrente'\n\n"
    "Usa o valor TOTAL de cada rubrica (quando há subtotais e totais, pega no total). "
    "Responde APENAS com um objeto JSON com exatamente essas seis chaves, "
    "sem texto antes ou depois, sem marcas de código. "
    "Se algum valor não existir no documento, usa null nessa chave."
)


def _abrir_documento(caminho_ou_ficheiro):
    if hasattr(caminho_ou_ficheiro, "read"):
        return fitz.open(stream=caminho_ou_ficheiro.read(), filetype="pdf")
    return fitz.open(caminho_ou_ficheiro)


def _renderizar_paginas(documento, max_paginas=MAX_PAGINAS_VISAO):
    """Renderiza as primeiras `max_paginas` como PNG em base64 a 144 DPI."""
    zoom = fitz.Matrix(2, 2)
    return [
        base64.standard_b64encode(
            documento[i].get_pixmap(matrix=zoom).tobytes("png")
        ).decode()
        for i in range(min(len(documento), max_paginas))
    ]


def _parsear_json(texto):
    texto = texto.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(texto)


def _extrair_via_texto(texto):
    texto = texto[:MAX_CARACTERES_TEXTO]
    resposta = _obter_cliente().messages.create(
        model=MODELO,
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": f"{_INSTRUCAO_CAMPOS}\n\nTEXTO DO BALANÇO:\n{texto}",
        }],
    )
    return _parsear_json(resposta.content[0].text)


def _extrair_via_vision(imagens):
    conteudo = [
        {
            "type": "image",
            "source": {"type": "base64", "media_type": "image/png", "data": img},
        }
        for img in imagens
    ]
    conteudo.append({"type": "text", "text": _INSTRUCAO_CAMPOS})

    resposta = _obter_cliente().messages.create(
        model=MODELO,
        max_tokens=500,
        messages=[{"role": "user", "content": conteudo}],
    )
    return _parsear_json(resposta.content[0].text)


def extrair_dados(caminho_ou_ficheiro):
    """
    Extrai os dados do balanço de um PDF.

    Tenta a via de texto primeiro (mais barata). Se o PDF não tiver texto
    suficiente (ex: documento digitalizado), usa visão computacional sobre
    as primeiras MAX_PAGINAS_VISAO páginas.

    Devolve (dados, texto_extraido):
    - dados: dicionário com as seis chaves do balanço
    - texto_extraido: o texto lido do PDF, ou "" se visão foi usada
    """
    documento = _abrir_documento(caminho_ou_ficheiro)
    texto = "".join(pagina.get_text() for pagina in documento)

    if len(texto.strip()) >= MIN_CARACTERES_TEXTO:
        documento.close()
        return _extrair_via_texto(texto), texto

    # Fallback para visão (PDF sem camada de texto)
    imagens = _renderizar_paginas(documento)
    documento.close()
    return _extrair_via_vision(imagens), ""
