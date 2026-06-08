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
- Avaliação e percentil estimado face a benchmarks por setor+dimensão
- Tabela de resultados com coluna de percentil ("melhor que X%")
- Gráfico de barras dos rácios
- Diagnóstico em linguagem natural gerado pela IA com contexto sectorial

### Extração de PDF (robusta)
- PDFs digitais: extração de texto com PyMuPDF
- PDFs digitalizados (scan): fallback automático para visão computacional (Claude Vision)
- Suporte a terminologia SNC portuguesa (Disponibilidades, Existências, etc.)
- Expander de diagnóstico para o utilizador ver o texto extraído

### Contexto da empresa
- Setor de atividade (11 setores, com tooltip explicativa e exemplo)
- Dimensão da empresa (Micro/Pequena/Média/Grande, com tooltip com os 3 critérios EU)
- Nível de linguagem do diagnóstico (Simples/Equilibrada/Técnica, com tooltip)
- Todos os campos passados ao diagnóstico da IA e ao motor de benchmarks

### Benchmarks sectoriais
- Arquitectura P25/P50/P75 por setor+dimensão implementada em `benchmarks.py`
- Percentil calculado por interpolação linear — math pura, sem IA
- Fallback para BENCHMARK_GERAL (BdP 2024) enquanto não há dados SABI
- Script `importar_sabi.py` pronto: lê export SABI, calcula percentis, gera código
- Acesso ao SABI (via UBI) pendente — quando disponível, popula automaticamente

### Infraestrutura
- Repositório GitHub: github.com/BIGGUSTASTHEONE/alter-app
- Deploy online: Streamlit Cloud (URL activo)
- Nota de fonte dos dados comparativos visível na interface após análise

## Decisões técnicas
- Modelo da API: `claude-sonnet-4-6` (extração e diagnóstico)
- Framework de interface: Streamlit
- Leitura de PDF: PyMuPDF (fitz)
- Arquitectura: extração (IA) → cálculo determinístico → diagnóstico (IA)
- Benchmarks: SABI como fonte principal (acesso pendente); BdP QS como referência
- Percentil: interpolação linear P25/P50/P75 — sem IA, só math

## Próximos passos

### Em curso
- [ ] Obter acesso ao SABI via UBI e popular benchmarks com dados reais
- [ ] Segunda categoria de análise (solvabilidade)
- [ ] Seleção de categoria na interface (quando houver mais do que uma)

### A seguir
- [ ] Restantes categorias (rendibilidade, endividamento)
- [ ] Geração de relatório PDF com todas as análises feitas
- [ ] Melhorias de design e experiência de utilizador
