# Mecânica do tour guiado no Power BI · Criticidade de Obras (v4)

07/10/2026 · v4: busto do personagem (cortado na cintura, ancorado na base do card) e aplicação no PBIP. Fontes:
`pbi/spec/tour/passos.json` (só `poses_arquivos` mudou: aponta para `assets/personagem/poses/busto/`) e
`pbi/spec/tour/brief-tour.md` (v2). O HTML de desenho é a referência; o Figma fica para depois.

## 1. Arquivos

| Arquivo | Situação | O que faz |
|---|---|---|
| `pbi/scripts/tour_lib.py` | v4 | Lê o passos.json e gera a medida de cada passo (`T<n> · Tour · Passo NN · HTML`), a de cada pose (`Comum · Tour · Pose Pn · HTML`) e a folha `Comum · Tour · CSS`. Constantes do busto: `BUSTO_COMUM_ALTURA = 260`, `BUSTO_COMUM_MIN = 220`, `BUSTO_LARGURA_MAX = 240`, `GRANDE_PH_MAX = 400`, `POSE_ALTURA_PX = 600`. Funções: `busto_comum(n)`, `pose_dados` (lê `busto/`), `_opcao_comum`, `_opcao_grande`, `_alturas_novo` (card grande), `_alturas_mes` (T4 passo 3), `_pastilhas`, `_infog`/`_cabecalho`, `html_passo`, `medidas_tela`, `medidas_poses`, `medida_css`. |
| `pbi/scripts/poses_busto.py` | novo | Lê `assets/personagem/poses/P1..P6-*.png` e grava `assets/personagem/poses/busto/` com o mesmo nome. Corte: primeira linha, a partir de 40 % da figura, em que pelo menos 3 % dos pixels opacos da largura são azul-marinho (calça), menos 4 px. Reexecutável; `--info` só mostra os cortes. |
| `assets/personagem/poses/busto/P1..P6-*.png` | gerado | 6 bustos (cabeça até a cintura), cerca de 290 a 340 KB cada em disco. |
| `pbi/scripts/paginas/tour.py` | sem mudança de estrutura | `declarar(ctx)`: visuais HTML, botões e marcadores (usa `geometria()["hits"]`). |
| `pbi/dax/T<n>/Tour/*.dax` | regerado | 32 medidas de passo, de 2,5 KB a 5,2 KB de DAX cada. A pose não está no .dax: o passo referencia `[Comum · Tour · Pose Pn · HTML]`. |
| `pbi/dax/comum/Desenho/Comum · Tour · Pose P1..P6 · HTML.dax` | regerado | 6 poses (PNG em base64, 600 px de altura): de 77 a 90 KB de DAX cada. |
| `pbi/dax/comum/Desenho/Comum · Tour · CSS.dax` | regerado | Folha de estilo v4. |
| `pbi/qa/tour/html/t<n>-NN.html` e `.png` | regerados | 32 prévias, 1920 × 1080, com busto. |

`passos.json` ainda não tem os campos `card`, `layout` e `personagem`: a geometria sai da regra §3 do brief. Quando o Figma
gravar esses campos, `tour_lib` usa os valores e recusa card que cubra o recorte.

## 2. Visuais e marcadores (inalterados)

- HTML do passo: `T<n>_Tour_PNN`, em (0, 0, 1920, 1080), z 7000, oculto.
- Botões: `T<n>_TourAnt_PNN` (Anterior; passo 1: "Pular tour"), `T<n>_TourProx_PNN` (Próximo →; último: "Concluir ✓"),
  `T<n>_TourFecha_PNN` (×). Área de clique de 56 px de altura nos controles (128 × 48 e 148 × 48); no ×, 56 × 56. z 7010, ocultos.
- Marcadores: `T<n>_TOUR_00` (fechado) e `T<n>_TOUR_NN`, grupo `("tour", "Tour")`, só exibição.
- Entrada: `T<n>_Aj_Guia` → `T<n>_TOUR_01`. Navegação: Próximo n → n+1; último → `_00`; Anterior n → n−1; Pular → `_00`; Fechar → `_00`.

## 3. Card grande e busto (v4)

Ordem de leitura: título → abertura → (leitura, no mês) na largura toda do card. Abaixo, duas colunas: o busto na base
(à esquerda ou à direita, conforme o foco) e o infográfico. O infográfico segue a ordem pedida: pesos → regra → pastilhas →
exemplo → faixas → mobilização → nota → dica. Cada campo de `conteudo` é opcional (o T4 passo 3 não tem `fecho`).

- **Busto**: o personagem é o corte da pose na cintura, rente à base do card. Tamanho: 400 px de altura no card grande
  (`GRANDE_PH_MAX`); 260 px no card comum (`BUSTO_COMUM_ALTURA`), caindo até 220 px quando o braço estendido (P2, P3)
  passaria de 240 px de largura. A coluna do personagem tem a largura do busto + 16 px; o texto leva o resto.
- **Legenda dos pesos** com o número: "Resultado da obra · 35", "Desvio físico · 25", "Desembolso do mês · 20",
  "Variação do resultado · 10", "Sem estoque e adiantamentos · 10".
- **Pastilhas** da regra: cada uma em 2 linhas no máximo; valor em Segoe SemiBold 17 ("0", "metade do peso", "peso inteiro"),
  rótulo em 15 ("dentro da faixa", "em atenção", "crítico"); fundos #E1EFE7, #F6E7CF, #F7E3E3. A largura de cada uma é a do
  próprio texto (não três colunas iguais): com colunas iguais, "metade do peso" quebrava em 3 linhas.
- **Mobilização**: marca quadrada tracejada de 14 px antes do texto (como o chip da lista).
- **Controles** dentro do card: na base da coluna do infográfico. No empilhado, Anterior fica sobre Próximo, a menos que
  `W ≥ 8 + busto + 16 + 286 + 28` (os dois ficam dentro da borda do card).

## 4. Layouts por passo (lado final, tamanho em px, busto)

- Comum (28 passos): lado a lado, 720 de largura, no lado pedido, exceto:
  - T1 passo 4 (OBRAS): empilhado **500 × 681**, controles empilhados; busto 240 × 238.
  - T3 passo 6 (LINHA): empilhado **604 × 580**; busto 240 × 238.
  - T2 passo 5 (CASCATA): pedido abaixo, final **esquerda 720 × 394** (abaixo não cabe).
- Grande (4 passos):
  - T1 passo 3 (PONTUACAO): direita, **748 × 1026** (x 1156, y 38). Busto 296 × 400.
  - T2 passo 3 (QUADRADINHO): direita, **956 × 782** (x 948, y 265). Busto 296 × 400.
  - T3 passo 3 (CURVA): pedido abaixo, final **direita 604 × 944** (x 1300, y 120). Busto 296 × 400.
  - T4 passo 3 (MES): abaixo, **1888 × 350** (x 16, y 701), duas colunas, k = 1, cota a 40 px, sem mini-legenda. Busto 188 × 254.

## 5. Decisões e desvios do brief

1. **T4 passo 3 (MES): duas colunas em k = 1, sem escala.** Decisão do coordenador. Título, abertura e leitura à esquerda;
   régua e dica à direita; controles embaixo à direita; personagem pequeno à esquerda. Sem mini-legenda. A dica cabe em uma
   linha porque o card tem a largura livre da tela (1888 px). Substitui o layout legado com escala 0,85 da v3.
2. **Busto de 400 px no card grande** (decisão do coordenador: "~400 px no grande"). Substitui o teto de 480 px da v2 e a
   pose que ocupava o bloco inteiro da v3. O card do T1 passo 3 segue com 1026 px de altura porque o infográfico é que o
   determina; a prévia t1-03 foi conferida com Read.
3. **Card grande abaixo do mínimo de 760 px** (T1 passo 3: 748 px, o máximo livre à direita do foco).
4. **Pastilhas medem pelo texto** (ver §3).
5. **Figma**: `passos.json` ainda sem `card`, `layout` e `personagem`. Os valores vêm da regra §3.

## 6. Tamanhos das medidas

Medidas lidas no motor do Desktop aberto, em 07/10 (`LEN` do valor da medida; ver §10):

- **Passos** (`T<n> · Tour · Passo NN · HTML`): de 71.493 a **82.609 caracteres** depois da reaplicação das poses (maior:
  `T1 · Tour · Passo 01 · HTML`); antes, de 72.437 a 84.508. O valor inclui a pose referenciada, por isso o número é alto:
  o texto próprio do passo é o .dax de 2,5 a 5,2 KB.
- **Poses** (`Comum · Tour · Pose Pn · HTML`): de 69.584 (P4) a 80.400 caracteres (P1) depois da reaplicação; antes, de
  70.528 (P4) a 82.252 (P2). PNG em base64, abaixo de 150 KB cada.
- Cada render de passo lê uma pose. O custo de abertura no Desktop é medido no teste por clique (§9).

## 7. Prova (ordem do pedido)

1. `tour_lib.py` → 32 medidas de passo, 6 poses e 1 folha de estilo gravadas, sem aviso de pastilha.
2. `lint_conta_desenho.py pbi/dax --so-erros` → **0 ERRO** (837 medidas: 193 desenho, 644 conta; 1990 AVISO, nenhum nas
   medidas do tour ou de pose).
3. `gerar_modelo.py` (simulação) → sem erro; plano de 837 medidas; lint TOM com 0 erro e 0 aviso.
4. `montar_pbip.py` (simulação, disco anterior) → exit 2 com 64 erros L018, todos das medidas novas (passos e poses). Sem erro
   de bookmark ou de alvo. Some com o `gerar_modelo --aplicar`.
5. `montar_pbip.py` com o contexto da árvore `pbi/dax` (rascunho, nada gravado) → **exit 0**; 319 visuais, 63 marcadores,
   841 medidas; plano de 424 arquivos.
6. Prévias: 32 HTML e 32 PNG de 1920 × 1080 (Edge headless) em `pbi/qa/tour/html/`.
7. Checagem geométrica nas 32 prévias (`edge_cdp.mjs`, em paralelo): texto dentro do card, nada sobre os controles, controles
   dentro do card, cabeça do personagem dentro do canvas, card fora do recorte. Resultado: §8.
8. Conferido com Read (imagens, versão com busto): `t1-01`, `t1-03`, `t1-04`, `t1-05`, `t2-03`, `t4-03`. Cabeça inteira, mãos
   inteiras, corte limpo na cintura rente à base; controles visíveis; card fora do recorte.

## 8. Checagem geométrica (resultado)

32 de 32 prévias sem aviso (versão com busto): texto dentro do card, nenhum texto sobre os controles, controles dentro do
card, cabeça do personagem dentro do canvas e card fora do recorte. Script: scratchpad/verificar_tour_paralelo.py.

## 9. Pendências

1. Teste por clique no Desktop: abrir, avançar até o último, voltar, fechar no meio; filtros e página preservados. Conferir
   fontes Segoe UI e Barlow, o véu de 4000 px (custo de desenho), o peso da pose por render e o alvo de Fechar.
2. Figma: gravar `card`, `layout`, `personagem` e `lado_final` no passos.json (o tour usa os valores quando vierem).
3. Poses novas (Magnific): os originais vão para `assets/personagem/poses/v1/`. Depois de sobrescrever `P1..P6-*.png`,
   rodar nesta ordem: `poses_busto.py`, `tour_lib.py`, `gerar_modelo.py --aplicar`, `montar_pbip.py --aplicar`, e os dois
   `--conferir` (0). Desktop fechado antes de aplicar.
4. Fade de entrada retirado (a captura saía no meio da transição). Reavaliar no Desktop.
5. `CSS_GUIA` ainda em `T<n> · Leitura · CSS` (regras de `.gv` sem uso). Remover na revisão das leituras.
6. `desktop.ps1 -Acao abrir` abre minimizado e não há ação para restaurar a janela. Restaurar pela barra de tarefas.

## 10. Aplicado em 07/10 (duas aplicações)

Primeira aplicação: busto de 16:41, poses antigas. Reaplicação: poses novas (`assets/personagem/poses/P*.png`, gravadas às
16:48; as antigas em `poses/v1/`), busto regerado às 16:52.

Primeira aplicação:

- `lint_conta_desenho.py pbi/dax --so-erros`: 0 ERRO (837 medidas: 193 desenho, 644 conta; 1990 AVISO já existentes).
- `gerar_modelo.py --aplicar`: gravado 1 arquivo, removidos 0 (backup `pbi/_backups/modelo-20261007-164508.zip`).
- `montar_pbip.py --aplicar`: gravado 39, removidos 0; `pbir validate: Valid (2 info)` (backup `report-20261007-164510.zip`).
- `--conferir`: `gerar_modelo.py` 0 arquivos mudam, 0 sobram; `montar_pbip.py` plano 424 arquivos, 0 mudam, 0 saem.
- `desktop.ps1 -Acao abrir -Espera 360`: porta 52434, pid 142104; modelo carregado em 9 s; refresh ok em 8 s. Contagens em
  `pbi/qa/modelo/refresh-20261007-164532.json` (`_Medidas` 1, dDegrau 6, dIndicador 5, dItem 10, dJanela 4, dMes 9,
  dMesRef 10, dObra 12, dObraFoco 7, fAnaliseCritica 42, fConferencia 123, fItens 450).
- `smoke_medidas.py --obras` (antes da troca das poses): **837 medidas avaliadas, 0 com erro**, exit 0.
- DAX no motor aberto (`scratchpad/avaliar_tour_dax.py`, grava `pbi/qa/tour/avaliacao-dax.json`): **38 de 38 ok**, 0 em
  branco, 0 com erro. Passos de 72.437 a 84.508 caracteres (maior: `T1 · Tour · Passo 04 · HTML`); poses de 70.528 (P4) a
  82.252 (P2).
- Fotos do canvas com o tour fechado, uma por página (`desktop.ps1 -Acao foto`; T2 a T4 com `fechar` →
  `montar_pbip.py --aplicar --ativa Tn` → `abrir -Espera 360`): `pbi/qa/redesenho/desktop/tour-fechado-t1.png` (Visão geral,
  1 de 19), `tour-fechado-t2.png` (Análise crítica, 2 de 19), `tour-fechado-t3.png` (Avanço físico, 3 de 19),
  `tour-fechado-t4.png` (Resultado no tempo, 4 de 19). Na T2, T3 e T4 a primeira foto saiu com o canvas em branco ou com os
  visuais carregando; repetida só com `foto` depois de renderizar. Conferidas com Read: tour fechado, sem véu nem card.

Reaplicação com as poses novas:

- `poses_busto.py`: 6 bustos regerados, corte na cintura em 51 % da figura (P1 663 px, P2 660, P3 664, P4 662, P5 662, P6
  659 de altura). Conferidos com Read: P1 e P2 (cabeça e braço inteiros, corte reto na cintura, sem calça).
- `tour_lib.py`: exit 0, sem aviso de geração.
- `lint_conta_desenho.py pbi/dax --so-erros`: 0 ERRO.
- `desktop.ps1 -Acao fechar`: fechado sem salvar (pid 84848).
- `gerar_modelo.py --aplicar`: gravado 1 arquivo (`_Medidas.tmdl`), removidos 0 (backup `pbi/_backups/modelo-20261007-165313.zip`).
- `montar_pbip.py --aplicar --ativa T1`: gravado 25, removidos 0; `pbir validate: Valid (2 info)` (backup
  `report-20261007-165314.zip`). Os visuais de tour da T4 voltam ao estado da T1.
- `--conferir`: `gerar_modelo.py` 0 arquivos mudam, 0 sobram; `montar_pbip.py` plano 424 arquivos, 0 mudam, 0 saem.
- `desktop.ps1 -Acao abrir -Espera 360`: porta 54476, pid 164872; modelo carregado em 11 s; refresh ok em 9 s; mesmas
  contagens (`pbi/qa/modelo/refresh-20261007-165342.json`).
- DAX no motor aberto: **38 de 38 ok**, 0 em branco, 0 com erro. Poses: P1 80.400, P2 79.604, P3 78.156, P4 69.584,
  P5 70.112, P6 69.772 caracteres. Passos de 71.493 a 82.609 (maior: `T1 · Tour · Passo 01 · HTML`). Grava
  `pbi/qa/tour/avaliacao-dax.json`.
- Desktop aberto na T1: `pbi/qa/redesenho/desktop/reaplicado-t1.png` (Visão geral, 1 de 19, tour fechado).

Não repetido após a troca das poses: `smoke_medidas.py --obras`. As 38 medidas do tour foram reavaliadas no motor aberto
(todas ok). O teste por clique segue na §9.

## 11. Aplicado v5 (07/10, tarde)

- Modelo: `gerar_modelo.py --aplicar` gravou 1 arquivo (`definition/tables/_Medidas.tmdl`); backup em `pbi/_backups/modelo-20261007-185611.zip`. Lint 0 ERRO (837 medidas, 1984 AVISO).
- PBIP: `montar_pbip.py --aplicar --ativa T1` gravou 145 arquivos (backup `_backups/report-20261007-185720.zip`); `pbir validate`: Valid (2 info). Papéis de parede `wp-t1..t4.svg` copiados (hash igual ao de `assets/wallpapers/`).
- Desktop: a instância do projeto foi fechada sem salvar (pid 164872) e reaberta (pid 158516, porta 60716), na T1.
- Medidas no motor (`smoke_medidas.py`): 837 medidas, 0 com erro; filtro "Tour · Passo" 32, "Pose" 6, "Leitura" 104, todas sem erro. O smoke não confere valor em branco.
- Foto: `pbi/qa/tour/desktop/aplicado-t1.png` (2584×1540). T2 a T4 não foram fotografadas: a ação `foto` só pega a página aberta, e trocar de página exige mexer no Desktop.
- Mudanças desta rodada: legenda "previsto/executado/atraso" saiu do cabeçalho do T3 passo 3 (CURVA); `passos.json` T3 passo 3 com mobilização curta; CURVA com régua e fecho em duas colunas (balão 596×562, P6 com cabeça de 165 px).
- Pendente, ainda NÃO aplicado: (a) o último passo de cada tela usa sempre P5 (regra nova; a aplicação acima é anterior a ela); (b) P7 "apontando para cima à esquerda" e P8 "à direita" em `passos.json` (`poses` e `poses_arquivos`), `poses_busto.py` com fração 0,42, e regra de foco acima do gestor (ativa só quando os dois recortes existem: `_pose_existe`); (c) P5 refeita (sorrindo): regerar o recorte com `poses_busto.py --narrador`.

## 12. Reaplicado com poses P7/P8 e P5 sorrindo (07/10, noite)

- Desktop: fechado sem salvar (pid 158516) e reaberto na T1 (pid 176504, porta 53430); janela "Criticidade de Obras - Analise Critica".
- Modelo: `gerar_modelo.py --aplicar` gravou 1 arquivo (`_Medidas.tmdl`); backup `pbi/_backups/modelo-20261007-193914.zip`. Lint 0 ERRO (839 medidas, 195 de desenho, 644 de conta).
- PBIP: `montar_pbip.py --aplicar --ativa T1` gravou 67 arquivos; `pbir validate`: Valid (2 info). Os quatro papéis de parede batem por conteúdo com `assets/wallpapers/`.
- Conferir após aplicar: `gerar_modelo --conferir` exit 0 (0 arquivos mudam); `montar_pbip --conferir` exit 0 (0 mudam, sem BLOQUEIO).
- Smoke (`smoke_medidas.py --obras`): 839 medidas, 0 erro de motor.
- Valor por DAX (`valores_medidas.py`, fora do repositório): passo 32 (0 em branco; maior 87,5 KB, T1 Passo 08); pose 8 (0 em branco; maior 84,9 KB, P8); leitura 104 (11 em branco no total da carteira, maior 52,9 KB, T4 CSS).
- As 11 em branco no total: 9 têm valor no próprio contexto (indicador, obra, mês ou mês de referência) ou são vazias por regra (empate sem empate; "acima do previsto desde" quando o mês de referência ficou abaixo). 2 estão vazias pelos dados: causas mais frequentes (a única causa registrada é "outra", que a lista exclui) e físico atrasado e caindo (desvio físico mínimo −0,9 pp; nenhuma obra abaixo de −1 pp).
- Foto: `pbi/qa/tour/desktop/reaplicado-poses-t1.png`, tour fechado, Desktop aberto na T1.
- Poses: P5 (sorriso natural) e P7/P8 (mão acima da cabeça) recortadas com corte 0,42 no topo do bbox; a ponta do dedo é detectada pelo pixel opaco mais extremo na direção do apontar; regra: foco acima do gestor → P7 ou P8 pela menor distância da ponta ao anel; último passo sempre P5; passo 1 P1.

## 13. Cabeçalho do visual oculto (07/10, noite)

Pedido: esconder o cabeçalho de hover do visual (filtro, foco, "…") nos visuais do tour, das leituras e dos botões "?".
Resultado da investigação: **nada a mudar no PBIR**. `pbip_lib._container()` já grava em todo visual
`visualContainerObjects.visualHeader[0].properties.show = false` (literal), e `visual_html` e `visual_botao` passam por ele.
Propriedade conferida na skill `pbir-format` (é a mesma dos exemplos e do tema). Não se acrescentou parâmetro.

Prova no disco (`pbi/pbip/CO.Report/definition/pages/*/visuals/*/visual.json`): 319 de 319 visuais com `visualHeader.show = false`.
Contagem por tela dos visuais pedidos (todos já ocultos): Tour HTML / Anterior / Próximo / Fechar = T1 9, T2 9, T3 7, T4 7
(32 de cada); `Lei_` 4, 5, 5, 5; `LeiX_` 3, 4, 4, 4; `Aj_` (inclui `Aj_Guia`) 4, 5, 5, 5. Simulação
`montar_pbip.py`: sem erro; plano de 424 arquivos, 2 mudam (`wp-provisorio.svg` e `report.json`, deriva anterior e sem
relação com este assunto), 0 saem. Nenhum visual mudou, então não houve fechar, aplicar nem reabrir o Desktop.

Causa provável do que se viu no teste por clique: o teste foi feito no **modo de edição** do Desktop (Ctrl+clique). No modo de
edição o Desktop mostra o cabeçalho ao passar o mouse mesmo com o interruptor "Cabeçalho do visual" desligado; o interruptor
vale para o modo de leitura (Serviço e relatório publicado). Não há propriedade PBIR que mude isso. A conferir no modo de
leitura (Serviço ou Desktop em exibição) antes de tratar como defeito do painel.

Ressincronização feita junto (sem mudança de conteúdo): ao conferir, o disco tinha `report.json` e `wp-provisorio.svg` diferentes
do plano e os 11 arquivos do modelo com quebra de linha CRLF (gravados às 21:04, sem alteração nas fontes). `montar_pbip.py
--aplicar --ativa T1` (2 arquivos; Valid, 2 info; backup `report-20261007-211826.zip`) e `gerar_modelo.py --aplicar` (11 arquivos;
backup `modelo-20261007-212002.zip`) trouxeram o disco de volta ao plano: `--conferir` dos dois com 0 e 0. Desktop reaberto na T1.

## 14. narrador Nano Banana 2.1 · fase A, até as prévias (08/10, madrugada)

Poses novas em `assets/personagem/poses/` (as de antes em `poses/v3/`, com `busto/` e `narrador/`); histórico em
`assets/personagem/LEIAME.md`, seção "narrador · Nano Banana 2.1". **Nada aplicado no PBIP nem no Desktop** (fase B).

- `poses_busto.py`: `NARRADOR_FRAC = {1: 0.31, 2: 0.31, 3: 0.36, 4: 0.41, 5: 0.40, 6: 0.50, 7: 0.31, 8: 0.31}` (meio
  do peito a ~0,31; P3 leva o pulso com o relógio; P4 e P5, as mãos; P6, o prendedor e o topo da prancheta). `busto/`
  regerado com as 8 poses (só serve para `pose_arquivo` saber que a pose existe).
- `tour_lib.py`: `CABECA_FRAC` por pose `{1: 0.174, 2: 0.180, 3: 0.178, 4: 0.180, 5: 0.180, 6: 0.182, 7: 0.180, 8: 0.181}`
  (lê `NARRADOR_FRAC` de `poses_busto`, uma fonte só); `CAUDA_BOCA` 0,75 (medida nas 8 poses); `CAUDA_BOCA_SOBE` 0,05
  (o contorno da ponta da cauda é o trecho mais largo do rosto logo acima da boca: a barba afina o rosto na linha da
  boca e a cauda encostava na bochecha); ponta do dedo de P1, P7 e P8 = pixel mais alto da mão erguida, fora da faixa
  da cabeça (a mão fica abaixo do topo do cabelo); passo 1 sempre P1 (a P7 tomava o lugar dela); pose embutida com
  `POSE_BITS = 5` bits por canal, sem paleta (a paleta FASTOCTREE manchava a pele de cinza).
- Checagem Python (geometria, prova do mínimo, cauda, botões; `verificar_v6` com `CABECA_FRAC[pn]` e "passo 1 sem P1"):
  32 passos, **0 erro**, 0 aviso. Checagem no navegador (DOM das 32 prévias): 0 com problema; t4-06 com vão 0 px entre
  a dica (quebra em 2 linhas no navegador) e os controles.
- Lint `lint_conta_desenho.py dax --so-erros`: 0 ERRO (839 medidas). Valor das medidas reconstruído dos .dax: 32 passos e
  8 poses, nenhum em branco; poses de 95 a 149 KB; maior passo 151,8 KB (`T3 · Tour · Passo 03 · HTML`, com a P6).
- Prévias: `pbi/qa/tour/html/t<n>-NN.html` e `.png` (32); fotos escolhidas em `pbi/qa/tour/html/fotos-nb/`.

## 15. Regra de pose, P4-a/P5-a e aplicação (08/10, madrugada)

- P4 e P5 trocadas pela P4-a (`Dokhksgpcl`, palmas para cima) e P5-a (`s7W4WX8l8e`, boca fechada). `NARRADOR_FRAC` P4 0,44;
  `CABECA_FRAC` P4 0,182 e P5 0,174.
- Regra de pose em `tour_lib` (`foco_acima_da_cabeca`, `_aponta_certo`, `_poses_do_passo`, `_escolhe_gestor`): foco acima
  (base do anel acima do topo do recorte e x do foco cobrindo o centro da cabeça) → P7/P8; acima e ao lado, ou ao lado →
  P2/P3 do lado do foco. Passo 1 P1, último P5, card grande P6 (se não couber: poses que apontam, `p6_nao_cabe`). P4 só se
  nenhuma pose que aponta couber (`p4_sem_apontar`); se nem a P4 couber, P6 (`p6_ultimo_recurso`; hoje só T4 05).
- `_dax`: acima de 800 termos, grupos de 400 entre parênteses (o motor recusa cadeia de ~1.000 `&`).
- Aplicado: `gerar_modelo --aplicar` e `montar_pbip --aplicar --ativa T1`, `--conferir` 0/0, Valid, smoke 839 medidas 0 erro,
  valor no motor: passos 97,6–151,8 KB, poses 95,2–148,5 KB, nenhuma em branco. Detalhes no HANDOFF ("Estado em 08/10/2026").

## 16. P9/P10 e regra de faixa (08/10, manhã)

- Poses P9-a (`jUn2cq3LD0`) e P10-a (`mEUsOEGhJQ`), apontando na diagonal para cima. `poses_busto.py` lê P1…P10 pelo número
  do nome; `NARRADOR_FRAC` 9/10 0,31; `CABECA_FRAC` 9 0,175 e 10 0,178; ponta do dedo: máximo de (−x − y) (P9) e (x − y) (P10).
- Regra (`faixa_do_passo`, `_escolhe_gestor`): posição de base entre todas as poses que apontam → faixa (centro do foco acima do
  topo da cabeça e cobrindo o x do rosto: cima; acima e ao lado: diagonal; na altura ou abaixo do topo da cabeça: lateral) →
  busca só com a pose da faixa (`fixas=("faixa", faixa, lado)`). Exceções P1, P5, P6 e P4/P6 de último recurso como antes.
- `medir_linhas_tour.py` + `linhas-navegador.json`: as quebras de linha medidas no Edge mandam (§ HANDOFF, vão mínimo).
- Aplicado: lint 0 ERRO (841 medidas), `--conferir` 0/0, Valid, smoke 841 medidas 0 erro, passos e poses sem branco.

## 17. O dedo sempre aponta para o foco (08/10, 10h)

- Regra: em todo passo o dedo aponta para o foco; exceções só o passo 1 (P1, acenando) e o último (P5, polegar). A P6 só
  valeria se a direção do dedo dela (1; 0,3), para a prancheta, apontasse para o foco; a P4 (sem direção) não entra.
- `DIRECAO_DEDO`, `ponta_dedo(pn, nh)` e `angulo_dedo(pn, nar, R)`: ângulo entre a direção do dedo e o vetor da ponta ao ponto
  mais próximo do foco (`ANG_DEDO_MAX` = 45°). A busca (`_escolhe_com_cabeca`) descarta posição acima de 45°; a checagem dá
  erro acima de 45° em todas as geometrias.
- `_geometria_direita` (T3 03) desce o balão de 20 em 20 px até achar gestor e cauda; `_geometria_abaixo` (T4 03) estreita o
  balão e, se a pose da faixa não couber, encosta o balão na margem direita e põe o gestor embaixo do foco.
- Último recurso (`FOCO_INVASAO_MAX` = 40): o gesto pode entrar até 40 px no foco e o balão comum pode ir a 440 de largura
  (hoje só T4 05). A checagem Python e a de navegador avisam e dão erro acima de 40 px.
- Mudou: T3 03 P6→P9, T4 03 P6→P7, T4 05 P6→P2. Maior passo no motor caiu para ~131 KB (a P6 não é mais usada).
