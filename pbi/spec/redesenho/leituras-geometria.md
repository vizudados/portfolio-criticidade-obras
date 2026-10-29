# Leituras do "?" · geometria e recuo do "?" (07/10/2026)

Alisson pediu que o visual da leitura coincida com o retângulo do painel, que o × desenhado seja igual ao "?" da casca
e que os botões de abrir e fechar tenham o mesmo retângulo. Depois, por pedido do Alisson ("Então recue"), o "?" de
todos os painéis com leitura foi recuado em −11 px no x e +6 px no y.

## Regra geométrica
- Visual da leitura (HTML Content): exatamente o retângulo do painel (x, y, w, h). Sem margem e sem sombra. Superfície
  `.lv .pn` com inset 0, fundo #FFFFFF, contorno 1 px #0B0B0C, raio 16 px, `overflow:hidden`.
- Centro do "?" da casca e do × da leitura: (x + w − 24, y + 20) do painel, círculo r 12,375, contorno 1,25 px #3B3B3F.
  O × tem glifo de 8 px (traço 1,5 px #0B0B0C) e é um SVG irmão do painel, por cima dele (z-index 5).
- Botão de abrir (`<T>_Aj_<chave>`) e botão de fechar (`<T>_LeiX_<chave>`): mesmo retângulo (cx − 15, cy − 15, 30 × 30),
  mesmo raio (15) e mesmo realce. Os dois são calculados do mesmo centro em `leituras_lib.declarar_tela`.
- Folga do conteúdo: nenhum texto ou gráfico do painel a menos de 8 px da borda do círculo. A menor folga medida
  foi de 20,9 px (T1 Pesa). O arco de 16 px do canto da leitura é contorno, não conteúdo, e foi excluído da medição.

## Tabela das 15 leituras
Coordenadas no canvas 1920 × 1080. Conferência: fotos com dados reais do Desktop aberto (foto_tN, sem aplicar no PBIP),
papel de parede novo; recortes em `pbi/qa/leituras/pbi/recortes/`.

| Tela | Leitura | Painel (x, y, w, h) | Centro do "?" = centro do × | Botão abrir (x, y, w, h) | Botão fechar (x, y, w, h) | Conferência |
|---|---|---|---|---|---|---|
| T1 | Obras por criticidade | 352, 273, 1004, 631 | (1332, 293) | 1317, 278, 30, 30 | 1317, 278, 30, 30 | anel desloc 0,00 / 0,00 px (IoU 1,00); bordas 0 px; folga do conteúdo sem tinta até 40 px |
| T1 | O que pesa na carteira | 1396, 273, 464, 406 | (1836, 293) | 1821, 278, 30, 30 | 1821, 278, 30, 30 | anel desloc 0,00 / 0,00 px (IoU 1,00); bordas 0 px; folga do conteúdo 20,90 px |
| T1 | Como os meses evoluíram | 1396, 719, 464, 321 | (1836, 739) | 1821, 724, 30, 30 | 1821, 724, 30, 30 | anel desloc 0,00 / 0,00 px (IoU 1,00); bordas 0 px; folga do conteúdo 31,30 px |
| T2 | O quadradinho | 352, 273, 548, 584 | (876, 293) | 861, 278, 30, 30 | 861, 278, 30, 30 | anel desloc 0,00 / 0,00 px (IoU 1,00); bordas 0 px; folga do conteúdo 24,90 px |
| T2 | Como o resultado se forma | 940, 273, 508, 350 | (1424, 293) | 1409, 278, 30, 30 | 1409, 278, 30, 30 | anel desloc 0,12 / -0,03 px (IoU 0,99); bordas 0 px; folga do conteúdo 31,00 px |
| T2 | Resultado da obra, mês a mês | 940, 663, 508, 377 | (1424, 683) | 1409, 668, 30, 30 | 1409, 668, 30, 30 | anel desloc 0,12 / -0,03 px (IoU 0,99); bordas 0 px; folga do conteúdo 24,60 px |
| T2 | Sinais do mês | 1488, 273, 372, 388 | (1836, 293) | 1821, 278, 30, 30 | 1821, 278, 30, 30 | anel desloc 0,00 / 0,00 px (IoU 1,00); bordas 0 px; folga do conteúdo 27,50 px |
| T3 | Curva S | 352, 273, 900, 370 | (1228, 293) | 1213, 278, 30, 30 | 1213, 278, 30, 30 | anel desloc 0,00 / 0,00 px (IoU 1,00); bordas 0 px; folga do conteúdo sem tinta até 40 px |
| T3 | Ritmo do mês | 1292, 273, 568, 290 | (1836, 293) | 1821, 278, 30, 30 | 1821, 278, 30, 30 | anel desloc 0,00 / 0,00 px (IoU 1,00); bordas 0 px; folga do conteúdo sem tinta até 40 px |
| T3 | Avanço das obras | 1292, 603, 568, 437 | (1836, 623) | 1821, 608, 30, 30 | 1821, 608, 30, 30 | anel desloc 0,00 / 0,00 px (IoU 1,00); bordas 0 px; folga do conteúdo sem tinta até 40 px |
| T3 | Linha do tempo das obras | 352, 683, 900, 357 | (1228, 703) | 1213, 688, 30, 30 | 1213, 688, 30, 30 | anel desloc 0,00 / 0,00 px (IoU 1,00); bordas 0 px; folga do conteúdo sem tinta até 40 px |
| T4 | Resultado da carteira, mês a mês | 352, 273, 1068, 380 | (1396, 293) | 1381, 278, 30, 30 | 1381, 278, 30, 30 | anel desloc 0,00 / 0,00 px (IoU 1,00); bordas 0 px; folga do conteúdo sem tinta até 40 px |
| T4 | Resultado por obra | 1460, 273, 400, 380 | (1836, 293) | 1821, 278, 30, 30 | 1821, 278, 30, 30 | anel desloc 0,00 / 0,00 px (IoU 1,00); bordas 0 px; folga do conteúdo sem tinta até 40 px |
| T4 | Desembolso da carteira | 352, 693, 1068, 347 | (1396, 713) | 1381, 698, 30, 30 | 1381, 698, 30, 30 | anel desloc 0,00 / 0,00 px (IoU 1,00); bordas 0 px; folga do conteúdo sem tinta até 40 px |
| T4 | Desembolso por obra | 1460, 693, 400, 347 | (1836, 713) | 1821, 698, 30, 30 | 1821, 698, 30, 30 | anel desloc 0,00 / 0,00 px (IoU 1,00); bordas 0 px; folga do conteúdo sem tinta até 40 px |

Resultado: 15 de 15 leituras com deslocamento de até 0,2 px no anel e bordas exatas. A diferença de 0,12 px
(IoU 0,99) nas leituras T2 Forma e T2 Mes é de 1 pixel de antialias do anel.

## Arquivos alterados
- `pbi/scripts/leituras_lib.py`: sem margem (MARGEM_* removido); `BOTAO_AJ = 15` para abrir e fechar; `X_SVG` (×
  desenhado) e `CSS_X` (posição: right 11 px, top 7 px).
- `pbi/scripts/leituras_t1.py` … `leituras_t4.py`: painel() com o × como irmão do painel; CSS com `.lv .pn` inset 0,
  sem sombra e `+ CSS_X`; reserva do sobretítulo à direita (T2: 32 px, antes 26 px).
- `pbi/scripts/paginas/leituras_t1.py` … `leituras_t4.py`: centros (cx, cy) do recuo (x + w − 24, y + 20).
- `pbi/spec/casca/_fonte_v2/T1.svg` … `T4.svg`: `transform="translate(-11 6)"` nos 15 grupos "Ajuda · <painel>"
  (o "Ajuda · Guia da página" não mudou). Cópia dos originais em `pbi/spec/casca/_fonte_v2/_antes-recuo/`.
  Os D1…D4 não têm grupos "?" de painel (não mudaram).
- `pbi/assets/wallpapers/wp-t1…t4.svg` e `wp-d1…d4.svg`: regenerados por `pbi/scripts/gerar_casca.py`. Só grava nesta
  pasta; não toca o PBIP.
- `pbi/dax/T1…T4` (pastas de Leituras e T3/T4): medidas HTML e CSS das leituras regeradas.
- `pbi/qa/leituras/pbi/`: fotos `t<n>-abertas.png` e `t<n>-fechada.png`, 30 recortes em `recortes/`, `conferencia.json`,
  `folga_conteudo.json`.

## Verificações
- Lint (`lint_conta_desenho.py pbi/dax --so-erros`): 0 ERRO, 837 medidas (193 desenho, 644 conta), 1984 AVISO. Os avisos
  são de linha longa nas medidas HTML; não comparei com a linha de base.
- Simulação `gerar_modelo.py` (sem `--aplicar`): plano de 837 medidas; lint TOM ok, 0 erros; nada gravado.
- Simulação `montar_pbip.py` (sem `--aplicar`): 319 visuais, 63 bookmarks, 9 recursos; 0 ERRO; 0 L018 (nenhuma
  medida nova do tour fora do TMDL). Plano: 133 arquivos mudam: 4 papéis de parede, 45 visuais de leitura (15 `Lei_`,
  15 `LeiX_`, 15 `Aj_`) e 84 visuais `T*_Tour*` de outro agente em andamento (não são deste trabalho).
- PBIP não foi aplicado. Power BI Desktop não foi fechado. As fotos só leram o modelo.

## Pendência
- Figma não acompanha o recuo (Figma pausado). Ao retomar, aplicar o mesmo (−11, +6) nos componentes e instâncias
  "Ajuda" dos painéis nas telas v2 e nas leituras.

## Observações
- `foto_t1.py --v2` grava uma cópia do papel em `pbi/qa/redesenho/pbi/`. As fotos de T1 foram copiadas para
  `pbi/qa/leituras/pbi/`.
- Sobretítulo da Tela 02 com 32 px reservados à direita: sem reticências nos recortes T2 Mes e T2 Sinais.
