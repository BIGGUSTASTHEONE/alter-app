"""
config.py
Configuração central da aplicação Alter.

Centraliza os modelos da API num único sítio — extração e diagnóstico
podem usar modelos diferentes (custo vs. qualidade do parecer).
"""

# Extração de dados do balanço (texto e visão). Tarefa estruturada e barata.
MODELO_EXTRACAO = "claude-sonnet-4-6"

# Diagnóstico em linguagem natural — é a peça de raciocínio do produto.
MODELO_DIAGNOSTICO = "claude-sonnet-4-6"
