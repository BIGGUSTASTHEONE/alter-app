"""
test_extracao.py
Testes da lógica pura da extração (sem chamadas à API):
parsing do JSON devolvido pelo modelo e limite de páginas na via de visão.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import fitz
import pytest

import extracao


# ---------------------------------------------------------------------------
# PARSING DO JSON DEVOLVIDO PELO MODELO
# ---------------------------------------------------------------------------

def test_parsear_json_simples():
    assert extracao._parsear_json('{"ativo_corrente": 1000}') == {"ativo_corrente": 1000}


def test_parsear_json_com_cerca_de_codigo():
    # O modelo às vezes embrulha a resposta em ```json ... ``` apesar da instrução.
    texto = '```json\n{"ativo_corrente": 1000, "inventarios": null}\n```'
    assert extracao._parsear_json(texto) == {"ativo_corrente": 1000, "inventarios": None}


def test_parsear_json_com_espacos_a_volta():
    assert extracao._parsear_json('  \n {"x": 2.5} \n ') == {"x": 2.5}


def test_parsear_json_invalido_levanta_erro():
    with pytest.raises(ValueError):
        extracao._parsear_json("isto não é json")


# ---------------------------------------------------------------------------
# LIMITE DE PÁGINAS NA VIA DE VISÃO
# ---------------------------------------------------------------------------

def test_renderizar_paginas_respeita_o_limite():
    doc = fitz.open()
    for _ in range(extracao.MAX_PAGINAS_VISAO + 5):
        doc.new_page(width=200, height=200)
    imagens = extracao._renderizar_paginas(doc)
    assert len(imagens) == extracao.MAX_PAGINAS_VISAO
    doc.close()


def test_renderizar_paginas_documento_curto_rende_todas():
    doc = fitz.open()
    for _ in range(3):
        doc.new_page(width=200, height=200)
    assert len(extracao._renderizar_paginas(doc)) == 3
    doc.close()
