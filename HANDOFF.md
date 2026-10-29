# Handoff · Criticidade de Obras (portfólio)

## Estado em 28/10/2026 · sessão local

O repositório nasceu de uma cópia limpa de um painel de obras já entregue. Saíram nomes, empreendimentos, caminhos,
logo, personagem, pôster e vídeo da capa, e todos os dados. O histórico do git começa aqui.

**O painel hoje:** Capa, T1 a T5 e tooltips (`ttT1…` a `ttT5…`). A régua de desempenho da obra (Nota da obra, nove itens,
trava e status, desde a F3) está em `docs/03-indicadores-e-criticidade.md`; a planilha de origem, em `docs/02`.

**Em lugar provisório:**
- **Casca:** fechada para as cinco telas (28/10/2026). `pbi/spec/casca/_fonte_v2/T1…T5.svg` e `D1…D5.svg` →
  `gerar_casca.py` → `wp-t*.svg` e `wp-d*.svg`; o item 05 · Canteiro está desenhado nas dez cascas, então o rótulo em
  HTML (`Sidebar · HTML nav Canteiro`) não sai mais em tela nenhuma e a medida pode sair do modelo. A casca provisória
  da T5 e o script dela saíram.
- **Poses do tour (aplicadas em 28/10/2026):** a narradora é a Lia de obra (capacete, óculos e colete ocre com o VD).
  Corpo inteiro em `assets/personagem/poses/P1…P11-*.png` (quadro 1308 × 1590, aprovadas pelo dono; P11 = vistoria,
  usada no passo 1 da T5) e recortes do narrador em `assets/personagem/poses/narrador/` (`poses_busto.py --narrador`).
  Regra do dono: em todo passo com pose de apontar, o raio do dedo (direção medida em `DIRECAO_DEDO`) cruza o foco
  (`tour_lib.raio_no_foco`). Imagem nova de pose só pelo Codex CLI na máquina local; nunca espelhar (o VD inverte).
- **Capa:** o pôster `wp-capa.jpg` é neutro ("Capa nova em produção"). O vídeo aponta para um endereço que ainda não
  existe. Capa nova (mesmo layout, artes novas) e vídeo vêm da sessão local.
- **Dados:** fictícios em `dados/` desde a F2 (28/10/2026): sete obras de Natal, out/25 a set/26. Gerados por
  `pipeline/gerar_ficticios.py` (openpyxl + LibreOffice) e conferidos por `pipeline/conferir_ficticios.py`; descrição
  em `docs/02`. A raiz é escolhida por `pOrigem` (ver Conferência visual). **Datas em célula:** o Power Query só lê
  como data o formato de data embutido do Excel (o gerador grava o 17, mmm-yy, e desfaz o formato personalizado que o
  LibreOffice grava); o M aceita também número de série (30000 a 60000) e o espelho em Python emula essa leitura.
- **Números de exemplo** em docs, specs e testes (`smoke_*`, oráculos nos docstrings) são do painel antigo. Ficam
  velhos quando os dados novos chegarem: atualize junto.
- Scripts que dependem do Power BI Desktop ou do Windows (`desktop.ps1`, `dax.ps1`, `ponte.ps1`, `rodar_m_excel.ps1`,
  conferências no motor) só rodam na máquina local.

## Fases da sessão na nuvem

### F1 · Critérios (feita; aprovada em 28/10/2026: `docs/08-criterios-propostos.md`)
1. Pesquise critérios públicos de avaliação de desempenho de obras. Pontos de partida: gerenciamento de valor agregado
   (IDC/IDP), PPC do Last Planner, indicadores de construção civil (CBIC, Sinduscon), qualidade (PBQP-H), segurança
   (NR-18, taxa de frequência e gravidade de acidentes), desvio de custo e de prazo, retrabalho, suprimentos. Cite a
   fonte de cada critério.
2. Cruze com o painel atual: o que a régua antiga não cobre, cobre mal ou mede de um jeito difícil de explicar.
3. Entregue `docs/08-criterios-propostos.md` com:
   - critérios novos da régua: peso, faixa de nota, de onde vem o dado, por que entra;
   - nomes novos de indicadores (tabela atual → novo);
   - lacunas que passam a ser cobertas;
   - por página: gráficos a resumir e o motivo;
   - se fizer sentido, uma tela nova que aproveite os dados completos.
4. **Pare e peça aprovação no canal** (`tipo: pergunta`). Nada muda no modelo antes do aval.

### F2 · Dados fictícios de Natal (feita em 28/10/2026)
- Sete empreendimentos: DUNAS, POTENGI, PONTA NEGRA, CAJUEIRO, REDINHA, JANGADA e TIROL (dá para propor outra lista na
  F1). Bairros reais de Natal; clientes e títulos inventados, sem pessoa conhecida.
- **Dados completos** (sem buracos) e com cara de reais: variação mês a mês, uma ou duas obras em crítico, uma
  melhorando, efeito de estação de chuva no físico. Estrutura parecida com a atual, com uma coisinha ou outra
  diferente (pedido do Alisson).
- O layout que o Power Query lê está em `pbi/m/*.m` e em `docs/02`. O gerador (`pipeline/gerar_ficticios.py`) tem de
  produzir planilhas que o M leia; se a estrutura mudar, o M muda junto.
- Confira os números com o espelho em Python (`pipeline/extrair_analise_critica.py`) antes de entregar.
- `dados/` sobe no git: é tudo fictício.

### F3 · Régua, nomes e telas
- Aplicar os critérios e nomes aprovados em DAX (conta × desenho), M, specs, leituras, tooltips e textos do tour.
- Resumir os gráficos aprovados; tela nova, se aprovada.
- Montar o PBIP (`python -X utf8 pbi/scripts/montar_pbip.py --aplicar`, rodando de `pbi/`) e atualizar os números de
  exemplo.

### F4 · Tooltips que usam o espaço e animação em tudo (feita em 28/10/2026)
- **Contador por marca** (`contador.py`): no desenho, `C.marca(expr)` cerca o texto de um número (⁅…⁆) onde ele entra
  no conteúdo, e `C.envolver_marcas(dax)` troca cada marca pelo odômetro no fim da medida (`passos=C.PASSOS_DENSO`
  nas tabelas densas, C8). Nunca marque texto que vai para atributo, `title`, `aria` ou `<text>` de SVG. Os quadros
  saem com `"pt-BR"`; se o motor formatar com ponto, a marca normaliza: número nenhum sai com ponto decimal.
- **Lint** (`lint_conta_desenho.py`): `format-sem-cultura` (ERRO) para `FORMAT` de número sem `"pt-BR"`;
  `GENERATESERIES` conta como lista do desenho.
- **Tooltips** (`tooltip_lib.py`): a lista principal ganha `ls eK` e `--n` (escala pela contagem: faixas de 3, 6, 9 e
  12 linhas, fonte de 1,35× a 0,87×, piso de 13 px) e a cascata C5 de `entrada()`. Páginas mais largas: `ttT1Mes` 760
  e `ttT2Mes` 620 (`paginas/tt_t1.py`, `tt_t2.py`).
- **Entradas genéricas** no `Comum · CSS base`: `.a-pop` (pontos, marcas, pílulas), `.a-fd` (grade, eixo, rótulos de
  apoio), `.a-gx` e `.a-gy` (réguas e trilhas), com a cascata no `animation-delay` inline. Barras e linhas seguem na
  corrida (`data-rk`, `path[data-rl]`). O relatório não tem visual Deneb.
- **Tour**: mede texto pela tabela `pbi/spec/tour/metricas-fontes.json` (`metricas_fontes.py`), não pela fonte
  instalada. A Barlow está na tabela; a Segoe UI entra quando a sessão local rodar o script no Windows.

### Fica com a sessão local
Lia nova e poses; capa nova e vídeo; publicação no workspace Power BI; conferência visual no navegador.

## Conferência visual
- A nuvem não abre o Power BI Desktop. Ao fim de cada entrega da F2 e da F3: commit, push e entrada no canal. A sessão
  local publica no workspace, confere no navegador e responde no canal com o que viu.
- **Fonte de dados:** na entrega (perfil padrão do `gerar_modelo.py`) os arquivos de `dados/` vão em base64 dentro do
  modelo (`pbi/m/fxDadosEmbutidos.m`, gerada por `pipeline/embutir_dados.py`; o `--aplicar` roda o script antes de
  montar). O M não cita fonte externa nenhuma: o serviço atualiza sem credencial nem gateway, e o `--aplicar` recusa a
  gravação se o `expressions.tmdl` citar `Folder.Files`, `SharePoint`, `Expression.Evaluate` ou `#shared`. As origens
  "Pasta" e "SharePoint" ficam só no perfil local (`--perfil local`, arquivos de `pbi/m/_local`), para o Desktop deste
  computador; esse PBIP não é a entrega.

## Antes de tornar público
O repositório é privado. A versão pública sai como snapshot novo, sem histórico, depois da auditoria de rastros feita
na máquina local.
