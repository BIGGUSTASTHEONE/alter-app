"""
test_ui.py
Testes do conversor markdown→HTML do diagnóstico (lógica determinística,
sem widgets Streamlit).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import ui


def test_md_titulo_negrito_e_separador():
    html = ui._md_to_html("# Título\nTexto com **força**.\n---\nFim.")
    assert "<h2" in html
    assert "<strong" in html
    assert "<hr" in html
    assert html.count("<p") == 2


def test_md_lista_nao_ordenada_agrupada_num_so_ul():
    html = ui._md_to_html("Pontos:\n- primeiro **forte**\n- segundo\nConclusão.")
    assert html.count("<ul") == 1
    assert html.count("<li") == 2
    assert "<strong" in html
    # a lista fecha antes do parágrafo final
    assert html.index("</ul>") < html.index("Conclusão")


def test_md_lista_ordenada():
    html = ui._md_to_html("1. um\n2. dois\n3. três")
    assert html.count("<ol") == 1
    assert html.count("<li") == 3
    assert "1. um" not in html  # a marca numérica é retirada (o <ol> numera)


def test_md_lista_com_asterisco():
    html = ui._md_to_html("* item a\n* item b")
    assert html.count("<ul") == 1
    assert html.count("<li") == 2


def test_md_lista_no_fim_do_texto_fecha():
    html = ui._md_to_html("- único item")
    assert html.endswith("</ul>")
