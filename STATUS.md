# Estado do Projecto — Alter

_Última actualização: 9 de junho de 2026_

## O que está feito

### Categoria: Liquidez e Solvabilidade (completa)
- Upload de PDF do balanço
- Extração automática dos dados via API (dois modos: texto e visão computacional)
- Extrai 6 campos: ativo corrente, inventários, caixa, passivo corrente, passivo não corrente, capital próprio
- Confirmação e correcção manual dos valores (layout em 2 colunas: Ativo | Passivo e Capital)
- Cálculo determinístico dos 4 rácios num único bloco "Analisar":
  - Liquidez Geral (Ativo Corrente / Passivo Corrente)
  - Liquidez Reduzida ((Ativo Corrente − Inventários) / Passivo Corrente)
  - Liquidez Imediata (Caixa e Depósitos / Passivo Corrente)
  - Solvabilidade (Capital Próprio / Passivo Total)
- Avaliação e percentil face a benchmarks por setor+dimensão (interpolação linear P25/P50/P75)
- Tabela combinada com todos os rácios, gráfico de barras e diagnóstico integrado
- Diagnóstico em linguagem natural gerado pela IA, contextualizado pelo setor

### Extração de PDF (robusta)
- PDFs digitais: extração de texto com PyMuPDF
- PDFs digitalizados (scan): fallback automático para visão computacional (Claude Vision)
- Suporte a terminologia SNC portuguesa (Disponibilidades, Existências, Capitais próprios, etc.)
- Expander de diagnóstico para o utilizador ver o texto extraído

### Contexto da empresa
- Setor de atividade (11 setores, com tooltip explicativa e exemplo)
- Dimensão da empresa (Micro/Pequena/Média/Grande, com tooltip com os 3 critérios EU)
- Nível de linguagem do diagnóstico (Simples/Equilibrada/Técnica, com tooltip)
- Todos os campos passados ao diagnóstico da IA e ao motor de benchmarks

### Benchmarks sectoriais (dados reais SABI)
- 928 463 empresas portuguesas (SABI, Bureau van Dijk — exportação completa, junho 2026)
- 40 combinações setor×dimensão com benchmarks P25/P50/P75 reais
- Liquidez Geral, Liquidez Reduzida e Solvabilidade por setor+dimensão
- Liquidez Imediata com fallback para BENCHMARK_GERAL (sem dado SABI disponível)
- Script `importar_sabi.py`: processa até 9 exports SABI, classifica dimensão EU (2-de-3), mapeia CAE→setor
- Mapeamento SABI correcto: "liquidez corrente" → Liquidez Geral; "liquidez" → Liquidez Reduzida; solvabilidade ÷ 100

### Infraestrutura
- Repositório GitHub: github.com/BIGGUSTASTHEONE/alter-app
- Deploy online: Streamlit Cloud (URL activo)
- Nota de fonte dos dados comparativos visível na interface após análise

## Decisões técnicas
- Modelo da API: `claude-sonnet-4-6` (extração e diagnóstico)
- Framework de interface: Streamlit
- Leitura de PDF: PyMuPDF (fitz)
- Arquitectura: extração (IA) → cálculo determinístico → diagnóstico (IA)
- Benchmarks: SABI (928 463 empresas, junho 2026) — população completa, não amostra
- Percentil: interpolação linear P25/P50/P75 — sem IA, só math

## Próximos passos

### A seguir
- [ ] Restantes categorias de análise (rendibilidade, endividamento)
- [ ] Seleção de categoria na interface (quando houver mais do que uma)
- [ ] Geração de relatório PDF com todas as análises feitas
- [ ] Melhorias de design e experiência de utilizador
