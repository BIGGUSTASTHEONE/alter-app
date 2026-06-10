# Estado do Projecto — Alter

_Última actualização: 10 de junho de 2026 (rev. integração da identidade na app)_

## Mudanças desta revisão (integração da identidade na app)
- **Símbolo SVG inline no cabeçalho**: `ui.cabecalho()` mostra os dois losangos (com glow) ao lado do wordmark; o `◆` emoji desapareceu. Sublinhado ciano agora à largura do wordmark, como no lockup `alter-logo.svg`.
- **Helper `ui.simbolo_svg(tamanho, fid)`**: gera o símbolo em qualquer tamanho; `fid` único por instância evita colisão de ids de filtro SVG no DOM.
- **Favicon**: `st.set_page_config` usa `alter-app-icon.svg` em vez do `◆`.
- **Step headers**: barra vertical substituída por marcador em losango rodado — eco da geometria da marca em cada secção.
- **Marca de água no fundo**: os dois losangos a 5% de opacidade no canto superior direito (data-URI no stack de gradientes do CSS).
- **Detalhes**: ícone "i" da legenda do percentil e ponto do card "Diagnóstico · IA" passaram a losangos; rodapé ganhou assinatura símbolo + ALTER.
- Pendentes do design (ver "Próximos passos"): JetBrains Mono, `TXT_MUTE`, glass base-ciano.

## Mudanças da revisão anterior (identidade gráfica — assets de design revistos)
- **SVG assets exportados do Claude Design** adicionados à raiz de `app/`: `alter-logo.svg`, `alter-logo-navy.svg`, `alter-symbol.svg`, `alter-symbol-flat.svg`, `alter-app-icon.svg`.
- **Símbolo escolhido: SymbolA** — dois losangos sobrepostos (representa "segunda opinião / comparação"), geometria pura em ciano `#41c3e0`.
- **Sistema de cores do design confirmado**: navy `#0A2540`, ciano `#41c3e0`, branco `#EAF2F8`, muted `#6f93ad` — maioritariamente alinhado com o que já está em `ui.py`; divergência menor em `TXT_MUTE` (`#6B7E92` vs `#6f93ad`).
- **JetBrains Mono** identificada como segunda fonte do sistema (labels, captions técnicas) — ainda não importada em `ui.py`.
- **Header** usava `◆` emoji em vez do SVG do símbolo — resolvido nesta revisão.
- **Padrão glass** do design (base ciano `rgba(65,195,224,0.06)`) difere do `_GLASS` atual (base branca) — alinhamento pendente.

## Mudanças de revisões anteriores (robustez e arquitectura)
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

### Design e identidade visual
- **Identidade gráfica definida** (Claude Design, junho 2026): símbolo SymbolA (dois losangos), wordmark Inter 800, paleta navy/ciano/branco/muted
- **SVG assets na app**: `alter-logo.svg` (lockup transp.), `alter-logo-navy.svg` (lockup navy), `alter-symbol.svg` (símbolo + glow), `alter-symbol-flat.svg` (favicon ≤16px), `alter-app-icon.svg` (tile navy)
- Sistema de cores: navy `#0A2540` (fundo), ciano `#41c3e0` (acento estrutural), verde/âmbar/vermelho (semântico)
- Tipografia Inter via Google Fonts (400–800); JetBrains Mono ainda não importada
- Cabeçalho com símbolo SVG inline (losangos + glow) ao lado do wordmark "ALTER" e sublinhado ciano
- Favicon: `alter-app-icon.svg`; marca de água dos losangos no fundo (5% opacidade)
- Steps com marcador em losango (geometria da marca) em vez de badges numerados
- Dividers horizontais na cor do acento ciano
- Resultados: cards 2×2 com glass branco (`_GLASS`), barra de percentil colorida, badge semântico — padrão glass do design (base ciano) ainda não aplicado
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

### Design — alinhamentos pendentes
- [x] Header: símbolo SVG inline em `ui.cabecalho()` (feito — `ui.simbolo_svg()`)
- [ ] Fonte: adicionar JetBrains Mono ao import do Google Fonts em `ui.CSS`
- [ ] Cor: alinhar `TXT_MUTE` de `#6B7E92` para `#6f93ad` (valor do design)
- [ ] Glass: avaliar se o padrão glass base-ciano do design substitui o `_GLASS` branco atual nos cards

### A seguir
- [ ] Restantes categorias de análise (rendibilidade, endividamento)
- [ ] Seleção de categoria na interface (quando houver mais do que uma)
- [ ] Geração de relatório PDF com todas as análises feitas
