"""
test_nucleo.py
Testes do núcleo determinístico (sem IA): rácios, percentis, avaliação,
classificação de dimensão e mapeamento CAE.

Correr:  pytest          (a partir da raiz do projeto)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest

import liquidez
import solvabilidade
import benchmarks
from importar_sabi import classificar_dimensao, mapear_cae


# ---------------------------------------------------------------------------
# RÁCIOS
# ---------------------------------------------------------------------------

def test_liquidez_geral():
    assert liquidez.calcular_liquidez_geral(200, 100) == 2.0


def test_liquidez_reduzida_exclui_inventarios():
    assert liquidez.calcular_liquidez_reduzida(200, 50, 100) == 1.5


def test_liquidez_imediata():
    assert liquidez.calcular_liquidez_imediata(30, 100) == 0.3


def test_solvabilidade():
    assert solvabilidade.calcular_solvabilidade(100, 400) == 0.25


# ---------------------------------------------------------------------------
# PERCENTIL — interpolação linear entre P25/P50/P75
# ---------------------------------------------------------------------------

P = dict(p25=1.0, p50=1.5, p75=2.0)


def test_percentil_nos_quartis():
    assert liquidez.calcular_percentil(1.0, **P) == 25
    assert liquidez.calcular_percentil(1.5, **P) == 50
    assert liquidez.calcular_percentil(2.0, **P) == 75


def test_percentil_interpola_no_meio():
    p = liquidez.calcular_percentil(1.25, **P)
    assert 37 <= p <= 38


def test_percentil_limitado_entre_1_e_99():
    assert liquidez.calcular_percentil(0.0, **P) == 1
    assert liquidez.calcular_percentil(100.0, **P) == 99


# ---------------------------------------------------------------------------
# AVALIAÇÃO — fronteiras determinísticas
# ---------------------------------------------------------------------------

BM = {"p25": 1.0, "p50": 1.5, "p75": 2.0}


def test_avaliacao_confortavel_no_p75_ou_acima():
    assert liquidez.avaliar_racio(2.0, BM)[0] == "confortável"
    assert liquidez.avaliar_racio(3.0, BM)[0] == "confortável"


def test_avaliacao_dentro_da_norma():
    assert liquidez.avaliar_racio(1.0, BM)[0] == "dentro da norma"
    assert liquidez.avaliar_racio(1.7, BM)[0] == "dentro da norma"


def test_avaliacao_abaixo_da_norma():
    assert liquidez.avaliar_racio(0.5, BM)[0] == "abaixo da norma"


# ---------------------------------------------------------------------------
# FUNÇÕES PRINCIPAIS DE CATEGORIA — forma do output
# ---------------------------------------------------------------------------

def test_analisar_liquidez_devolve_tres_racios_com_chaves():
    dados = {
        "ativo_corrente": 200,
        "passivo_corrente": 100,
        "inventarios": 50,
        "caixa_e_depositos": 30,
    }
    res = liquidez.analisar_liquidez(dados, "Comércio a retalho", "Pequena")
    assert len(res) == 3
    for r in res:
        assert {"racio", "formula", "valor", "avaliacao", "percentil", "ref_geral"} <= r.keys()


def test_liquidez_imediata_e_sempre_referencia_geral():
    # Não há dados SABI de liquidez imediata por setor — deve cair no fallback.
    dados = {
        "ativo_corrente": 200, "passivo_corrente": 100,
        "inventarios": 50, "caixa_e_depositos": 30,
    }
    res = liquidez.analisar_liquidez(dados, "Comércio a retalho", "Pequena")
    imediata = next(r for r in res if r["racio"] == "Liquidez Imediata")
    assert imediata["ref_geral"] is True


def test_solvabilidade_em_setor_com_dados_nao_e_referencia_geral():
    dados = {"capital_proprio": 100, "passivo_corrente": 200, "passivo_nao_corrente": 100}
    res = solvabilidade.analisar_solvabilidade(dados, "Comércio a retalho", "Pequena")
    assert res[0]["ref_geral"] is False


# ---------------------------------------------------------------------------
# BENCHMARKS — acesso e merge com fallback
# ---------------------------------------------------------------------------

def test_obter_inclui_fallback_geral():
    bms = benchmarks.obter("Comércio a retalho", "Pequena")
    assert "liquidez_imediata" in bms          # vem do BENCHMARK_GERAL
    assert "liquidez_geral" in bms             # vem dos dados SABI do setor


def test_e_sectorial():
    assert benchmarks.e_sectorial("Comércio a retalho", "Pequena", "liquidez_geral")
    assert not benchmarks.e_sectorial("Comércio a retalho", "Pequena", "liquidez_imediata")
    assert not benchmarks.e_sectorial("Agricultura e agro-indústria", "Micro", "liquidez_geral")


# ---------------------------------------------------------------------------
# CLASSIFICAÇÃO DE DIMENSÃO (critérios EU, 2 de 3) — valores em th EUR
# ---------------------------------------------------------------------------

def test_dimensao_micro():
    # e<10, vendas 1M€, activo 1M€ → 3/3 micro
    assert classificar_dimensao(5, 1000, 1000) == "Micro"


def test_dimensao_media():
    # e=100 (<250), vendas 45M€ (<=50M), activo 42M€ (<=43M) → média
    assert classificar_dimensao(100, 45000, 42000) == "Média"


def test_dimensao_grande():
    # excede todos os limiares de média
    assert classificar_dimensao(300, 60000, 50000) == "Grande"


def test_dimensao_ordem_vendas_activo():
    # Limiar de média difere: vendas<=50M€, activo<=43M€.
    # vendas=48M (ok), activo=45M (excede 43M) → com empregados altos, falha média.
    # e=240 (<250 T), v=48M (<=50M T), a=45M (>43M F) → 2/3 → Média
    assert classificar_dimensao(240, 48000, 45000) == "Média"
    # Inverter para activo dentro e vendas fora isola a ordem correta dos argumentos:
    # e=240 (T), v=55M (>50M F), a=40M (<=43M T) → 2/3 → Média também,
    # mas com a ordem trocada daria contagem diferente nos limiares.
    assert classificar_dimensao(240, 55000, 40000) == "Média"


def test_dimensao_invalida_devolve_none():
    assert classificar_dimensao("n/d", None, None) is None


# ---------------------------------------------------------------------------
# MAPEAMENTO CAE → SETOR
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("cae,setor", [
    ("47110", "Comércio a retalho"),
    ("46190", "Comércio por grosso"),
    ("10110", "Indústria transformadora"),
    ("41200", "Construção e imobiliário"),
    ("62010", "Tecnologia e software"),
    ("01110", "Agricultura e agro-indústria"),
    ("99999", "Outro / Não especificado"),
])
def test_mapear_cae(cae, setor):
    assert mapear_cae(cae) == setor
