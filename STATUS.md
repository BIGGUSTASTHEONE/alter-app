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
- Resultados em grelha de cards 2×2 com barra de percentil visual e badge semântico
- Diagnóstico em linguagem natural gerado pela IA, contextualizado pelo setor

### Extração de PDF (robusta)
- PDFs digitais: extração de texto com PyMuPDF
- PDFs digitalizados (scan): fallback automático para visão computacional (Claude Vision)
- Suporte a terminologia SNC portuguesa (Disponibilidades, Existências, Capitais próprios, etc.)
- Expander para o utilizador ver o texto extraído

### Contexto da empresa
- Setor de atividade (11 setores, com tooltip explicativa e exemplo)
- Dimensão da empresa (Micro/Pequena/Média/Grande, com tooltip com os 3 critérios EU)
- Nível de linguagem do diagnóstico via `st.pills` (Simples/Equilibrada/Técnica, com tooltip)
- Todos os campos passados ao diagnóstico da IA e ao motor de benchmarks

### Benchmarks sectoriais (dados reais SABI)
- 928 463 empresas portuguesas (SABI, Bureau van Dijk — exportação completa, junho 2026)
- 40 combinações setor×dimensão com benchmarks P25/P50/P75 reais
- Liquidez Geral, Liquidez Reduzida e Solvabilidade por setor+dimensão
- Liquidez Imediata com fallback para BENCHMARK_GERAL (sem dado SABI disponível)
- Script `importar_sabi.py`: processa até 9 exports SABI, classifica dimensão EU (2-de-3), mapeia CAE→setor
- Mapeamento SABI correcto: "liquidez corrente" → Liquidez Geral; "liquidez" → Liquidez Reduzida; solvabilidade ÷ 100

### Design e identidade visual (completo)
- Sistema de cores: navy `#0A2540` (fundo), ouro `#C9912A` (acento), verde/âmbar/vermelho (semântico)
- Tipografia Inter via Google Fonts
- Cabeçalho branded "ALTER" com sublinhado dourado
- Steps com borda esquerda dourada em vez de badges numerados
- Resultados: cards 2×2 com barra de percentil colorida (verde/âmbar/vermelho por avaliação)
- Diagnóstico em card com borda dourada — estilo parecer consultivo
- Nível de linguagem: pills clicáveis com cores Simples=verde, Equilibrada=ouro, Técnica=violeta
- Tema Streamlit configurado via `.streamlit/config.toml`
- Gráfico de barras removido em favor dos cards

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
- Resultados: HTML custom com CSS inline — não depende de widgets Streamlit para os cards
- Design system: navy/ouro/semântico — filosofia "o design serve a comparação"

## Próximos passos

### Imediato (antes de sexta 13/jun)
- [ ] Resolver cor das pills por opção quando selecionadas (CSS vs. emotion do Streamlit)

### A seguir
- [ ] Restantes categorias de análise (rendibilidade, endividamento)
- [ ] Seleção de categoria na interface (quando houver mais do que uma)
- [ ] Geração de relatório PDF com todas as análises feitas
