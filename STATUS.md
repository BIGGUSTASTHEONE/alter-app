# Estado do Projecto — Alter

_Última actualização: 10 de junho de 2026 (rev. robustez e arquitectura)_

## Mudanças desta revisão (robustez e arquitectura)
- **Diagnóstico com tratamento de erro**: se a chamada à API falhar, a app mostra o erro e mantém os cards (os rácios são deterministas e já estão calculados); um aviso persistente convida a carregar em «Analisar» de novo. Antes, a app rebentava com o traceback cru.
- **Visão limitada a 10 páginas** (`MAX_PAGINAS_VISAO`): PDFs digitalizados longos deixam de gerar pedidos enormes à API; a via de texto tem tecto de 150 000 caracteres (`MAX_CARACTERES_TEXTO`).
- **Cliente da API lazy em `extracao.py`** — o módulo importa-se sem chave configurada (necessário para testar a lógica pura).
- **`ui.py` novo**: todo o sistema de design (tokens, CSS, cabeçalho, cards, legenda, pills, inputs) saiu de `app.py`, que ficou só com a orquestração do fluxo e o prompt do diagnóstico (700 → ~260 linhas).
- **Diagnóstico renderiza listas**: `_md_to_html` agrupa `- item` / `* item` / `1. item` em `<ul>`/`<ol>` — antes os hífenes apareciam como texto cru.
- **Fallback de solvabilidade centralizado** em `benchmarks.BENCHMARK_GERAL` (estava à parte em `solvabilidade.py`); comentário desatualizado "Banco de Portugal" → SABI.
- **Testes: 27 → 38** — novos `tests/test_extracao.py` (parsing do JSON, limite de páginas) e `tests/test_ui.py` (markdown→HTML do diagnóstico).

## O que está feito

### Categoria: Liquidez e Solvabilidade (completa)
- Upload de PDF do balanço
- Extração automática dos dados via API (dois modos: texto e visão computacional)
- Extrai 6 campos: ativo corrente, inventários, caixa, passivo corrente, passivo não corrente, capital próprio
- Confirmação e correcção manual dos valores (layout em 2 colunas: Ativo | Passivo e Capital); caption com separadores de milhares por baixo de cada input
- Cálculo determinístico dos 4 rácios num único bloco "Analisar":
  - Liquidez Geral (Ativo Corrente / Passivo Corrente)
  - Liquidez Reduzida ((Ativo Corrente − Inventários) / Passivo Corrente)
  - Liquidez Imediata (Caixa e Depósitos / Passivo Corrente)
  - Solvabilidade (Capital Próprio / Passivo Total)
- Avaliação e percentil face a benchmarks por setor+dimensão (interpolação linear P25/P50/P75)
- Resultados em grelha de cards 2×2 com barra de percentil visual e badge semântico
- Diagnóstico em linguagem natural gerado pela IA, contextualizado pelo setor
- Resultados persistem em `session_state` — sobrevivem a reruns e poupam chamadas à API
- Falha da API no diagnóstico não destrói a análise: cards mantêm-se, diagnóstico pode ser retentado

### Extração de PDF (robusta)
- PDFs digitais: extração de texto com PyMuPDF
- PDFs digitalizados (scan): fallback automático para visão computacional (Claude Vision)
- Limites de custo: visão usa só as primeiras 10 páginas; texto limitado a 150k caracteres
- Suporte a terminologia SNC portuguesa (Disponibilidades, Existências, Capitais próprios, etc.)
- Expander para o utilizador ver o texto extraído

### Contexto da empresa
- Setor de atividade (11 setores, com tooltip explicativa e exemplo)
- Dimensão da empresa (Micro/Pequena/Média/Grande, com tooltip com os 3 critérios EU)
- Nível de linguagem do diagnóstico via pills custom (Simples/Equilibrada/Técnica)
- Todos os campos passados ao diagnóstico da IA e ao motor de benchmarks

### Benchmarks sectoriais (dados reais SABI)
- 928 463 empresas portuguesas (SABI, Bureau van Dijk — exportação completa, junho 2026)
- 40 combinações setor×dimensão com benchmarks P25/P50/P75 reais
- Liquidez Geral, Liquidez Reduzida e Solvabilidade por setor+dimensão
- Liquidez Imediata com fallback para BENCHMARK_GERAL (sem dado SABI disponível)
- Script `importar_sabi.py`: processa até 9 exports SABI, classifica dimensão EU (2-de-3), mapeia CAE→setor
- Mapeamento SABI correcto: "liquidez corrente" → Liquidez Geral; "liquidez" → Liquidez Reduzida; solvabilidade ÷ 100

### Design e identidade visual (completo)
- Sistema de cores: navy `#0A2540` (fundo), ciano `#41c3e0` (acento estrutural), verde/âmbar/vermelho (semântico)
- Tipografia Inter via Google Fonts
- Cabeçalho branded "ALTER" com sublinhado ciano
- Steps com borda esquerda ciana em vez de badges numerados
- Dividers horizontais na cor do acento ciano
- Resultados: cards 2×2 com fundo `#E3E8EF`, barra de percentil colorida, badge semântico
- Percentagens "top X%" em destaque — fonte aumentada (`1.1rem`)
- Hover dos botões em ciano claro `#6dd9f0` (alinhado com o acento)
- Diagnóstico em card com borda ciana — estilo parecer consultivo
- Texto do diagnóstico: corpo `1.15rem`, títulos `##` a `1.32rem`, título principal `#` a `1.55rem`
- Markdown do diagnóstico renderizado correctamente (negrito, títulos, separadores `---`)
- Nível de linguagem: pills custom via `session_state` + CSS `st-key-*`; cores Simples=verde, Equilibrada=ouro `#C9912A`, Técnica=violeta (independentes do acento estrutural)
- Tema Streamlit configurado via `.streamlit/config.toml`
- Gráfico de barras removido em favor dos cards

### Infraestrutura
- Repositório GitHub: github.com/BIGGUSTASTHEONE/alter-app
- Deploy online: Streamlit Cloud (URL activo)
- Nota de fonte dos dados comparativos visível na interface após análise
- Testes: 38 (`pytest`) — núcleo determinístico, lógica pura da extração, markdown do diagnóstico
- Modelos centralizados em `config.py`; `requirements.txt` fixado (app) separado de `requirements-dev.txt` (pipeline SABI + testes)

## Decisões técnicas
- Modelo da API: `claude-sonnet-4-6` (extração e diagnóstico)
- Framework de interface: Streamlit
- Leitura de PDF: PyMuPDF (fitz)
- Arquitectura: extração (IA) → cálculo determinístico → diagnóstico (IA)
- Separação apresentação/fluxo: `ui.py` (design system e componentes HTML) vs `app.py` (orquestração e prompt)
- Benchmarks: SABI (928 463 empresas, junho 2026) — população completa, não amostra
- Percentil: interpolação linear P25/P50/P75 — sem IA, só math
- Resultados: HTML custom com CSS inline — não depende de widgets Streamlit para os cards
- Design system: navy/ciano/semântico — filosofia "o design serve a comparação"
- Pills: `ui.nivel_pills_selector()` usa `st.button` + CSS `.st-key-{key}` para styling robusto (sem depender de internos React do Streamlit)

## Próximos passos

### A seguir
- [ ] Restantes categorias de análise (rendibilidade, endividamento)
- [ ] Seleção de categoria na interface (quando houver mais do que uma)
- [ ] Geração de relatório PDF com todas as análises feitas
