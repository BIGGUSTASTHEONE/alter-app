# Alter

*Análise financeira inteligente. Uma segunda opinião, sempre disponível.*

Aplicação web que recebe demonstrações financeiras de uma empresa, extrai os dados, calcula os rácios relevantes e gera um diagnóstico em linguagem natural com recurso a inteligência artificial. Funciona como uma segunda opinião financeira independente, acessível a quem precisa de interpretar contas sem dominar a parte técnica.

Projeto de Mestrado em Finanças e Contabilidade, Universidade da Beira Interior (UBI).

## Stack tecnológica

- Python 3.14
- Streamlit (interface)
- API Anthropic, Claude (interpretação)
- PyMuPDF (extração de PDF)
- Pandas (manipulação de dados)

## Como correr localmente

1. Instalar as bibliotecas:
   ```
   pip install -r requirements.txt
   ```
2. Criar o ficheiro `.env` a partir do `.env.example` e colocar a chave de API da Anthropic.
3. Arrancar a aplicação:
   ```
   streamlit run app.py
   ```

## Estado atual

Protótipo da categoria de liquidez (Liquidez Geral, Liquidez Reduzida, Liquidez Imediata).
