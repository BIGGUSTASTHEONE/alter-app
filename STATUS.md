# Estado do Projecto — Alter

## O que está feito

### Categoria: Liquidez (completa)
- Upload de PDF do balanço
- Extração automática dos dados via API (dois modos: texto e visão computacional)
- Confirmação e correcção manual dos valores pelo utilizador
- Cálculo determinístico dos três rácios de liquidez:
  - Liquidez Geral (Ativo Corrente / Passivo Corrente)
  - Liquidez Reduzida ((Ativo Corrente - Inventários) / Passivo Corrente)
  - Liquidez Imediata (Caixa e Depósitos / Passivo Corrente)
- Avaliação face a benchmarks de referência
- Tabela de resultados e gráfico de barras
- Diagnóstico em linguagem natural gerado pela IA

### Extração de PDF (robusta)
- PDFs digitais: extração de texto com PyMuPDF
- PDFs digitalizados (scan): fallback automático para visão computacional (Claude Vision)
- Suporte a terminologia SNC portuguesa (Disponibilidades, Existências, etc.)
- Expander de diagnóstico para o utilizador ver o texto extraído

## Decisões técnicas
- Modelo da API: `claude-sonnet-4-6` (extração e diagnóstico)
- Framework de interface: Streamlit
- Leitura de PDF: PyMuPDF (fitz)
- Arquitectura: extração (IA) → cálculo (determinístico) → diagnóstico (IA)

## Próximos passos

### Fase 1 — Alicerce (em curso)
- [x] Protótipo funcional de liquidez
- [x] Extração robusta (texto + visão)
- [ ] Repositório no GitHub
- [ ] Segunda categoria de análise (solvabilidade ou rendibilidade)
- [ ] Seleção de categoria na interface
- [ ] Deploy (Streamlit Cloud)

### Fase 2 — Crescimento (após deploy)
- [ ] Restantes categorias de análise (rendibilidade, endividamento, etc.)
- [ ] Benchmarks por setor de actividade
- [ ] Melhorias de design e experiência de utilizador
- [ ] Afinação dos prompts com base em feedback real
