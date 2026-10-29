# Figma · Tour guiado · T1 (v2, final)

Arquivo: `FjBWDk5odF9HaZ2pwhGosl`, página `04 · Redesenho v2 · Painel Criticidade de Obras` (`372:685`).
Frames da T1: https://www.figma.com/design/FjBWDk5odF9HaZ2pwhGosl?node-id=433-11294

## 1. IDs

| Item | ID | Observação |
|---|---|---|
| Seção `Tour · sistema` | `432:8381` | 2400 × 2100, em y 20300 |
| Seção `Tour · T01` | `433:11294` | 18240 × 1200, em y 22260 |
| `Tour · personagem` (Pose P1 a P6) | `432:8406` | 230 × 345, raio 16; variantes `432:8382` (P1), `432:8386` (P2), `432:8390` (P3), `432:8394` (P4), `432:8398` (P5), `432:8402` (P6) |
| `Tour · foco` | `432:8407` | anel raio 14; cantoneiras com curva (raio 20), braço 24, ponta arredondada |
| `Tour · cota` (Eixo) | `433:8421` | sem alteração |
| `Tour · controles` (Passo) | `433:8443` | Primeiro `433:8422` · Meio `433:8429` · Último `433:8436` |
| `Tour · dica` | `439:14847` | caixa creme, raio 10, ícone de cursor |
| `Tour · card` (Layout × Personagem) | `442:11791` | 1500 × 1040. Lado a lado Esq `442:11647` · Lado a lado Dir `442:11683` · Empilhado Esq `442:11719` · Empilhado Dir `442:11755` |
| `Tour · card grande` | `447:12086` | 748 de largura; infográfico do passo 3 (T1). Substitui `440:11663` |
| Amostra de documentação | `437:11936` | fundo escuro atrás do foco e da cota, só para leitura no board |

Estilos de texto: `v2/Tour · passo`, `v2/Tour · título`, `v2/Tour · texto`, `v2/Tour · dica`, `v2/Tour · botão`,
`v2/Tour · rótulo`, e `v2/Tour · pastilha` (Segoe UI Semibold 17/24, criado nesta revisão para a 1ª linha das pastilhas).

Frames (IDs mantidos): `433:11295`, `433:11654`, `433:12013`, `433:12372`, `433:12731`, `433:13090`, `433:13449`,
`433:13808`, `433:14167`. Dentro de cada um: `Tela 01 · v2`, véu, `Tour · foco`, `Tour · card` (ou `Tour · card grande`) e
`Tour · cota`. O card grande do passo 3 é a instância `447:12178`; a cota é `447:12270`.

## 2. Poses

As seis poses de `assets/personagem/poses/` estão no Figma como preenchimento de imagem (FIT) das variantes de
`Tour · personagem`. Foram reduzidas para 690 px de altura (cópias em `scratchpad/poses690`); os originais não foram
mexidos. Hashes: P1 `2dcca4bd…`, P2 `59e800c8…`, P3 `88fa7b8f…`, P4 `d552133e…`, P5 `117486e0…`, P6 `b841434e…`.
Cada variante ficou só com a imagem: sem fundo creme, sem silhueta e sem rótulo. Como a moldura é 230 × 345 e a imagem
é mais alta que larga, o FIT encosta a imagem na base da moldura. Todas as instâncias (cards e card grande) mostram a pose.

## 3. Passos (card final, layout, personagem, lado)

| # | Passo | Layout | Card (x, y, w, h) | Personagem | Lado final (pref.) | Controles |
|---|---|---|---|---|---|---|
| 1 | BOASVINDAS | lado a lado | 344, 130, 720, 444 | esquerda | abaixo (abaixo) | Primeiro |
| 2 | CARTOES | lado a lado | 344, 297, 720, 444 | esquerda | abaixo (abaixo) | Meio |
| 3 | PONTUACAO | grande | 1156, 38, 748, 1026 | esquerda | direita (direita) | Meio |
| 4 | OBRAS | empilhado | 1404, 265, 500, 681 | esquerda | direita (direita) | Meio |
| 5 | PESA | lado a lado | 628, 265, 720, 444 | direita | esquerda (esquerda) | Meio |
| 6 | MESES | lado a lado | 628, 620, 720, 444 | direita | esquerda (esquerda) | Meio |
| 7 | LEITURA | lado a lado | 344, 493, 720, 403 | esquerda | acima (acima) | Meio |
| 8 | FILTROS | lado a lado | 1184, 130, 720, 422 | esquerda | abaixo (abaixo) | Meio |
| 9 | NAVEGACAO | lado a lado | 328, 226, 720, 444 | esquerda | direita (direita) | Último |

Card grande (passo 3), ordem de leitura: título, abertura (na largura toda, no topo); abaixo, à esquerda a figura P6
(260 × 480) na base, e à direita o infográfico: legenda de pesos com número, regra com três pastilhas (1ª linha Segoe
SemiBold 17, 2ª linha `v2/Tour · dica`), exemplo em caixa creme, faixas, chip tracejado MOBILIZAÇÃO com o texto da
mobilização, nota e os controles.

## 4. Correções desta revisão

- Empilhado (`442:11719`, `442:11755`): paddings do corpo 8, da coluna 20, e vão 0 na linha de figura e controles.
  O "Próximo →" do passo 4 ficou dentro do card.
- Conjunto `Tour · card` ampliado para 1500 × 1040: a variante lado a lado Direita não é mais cortada.
- Card grande reconstruído (título e abertura no topo, pesos com número, pastilhas em duas linhas, chip tracejado
  de mobilização, figura P6 na base). Altura 1026, y 38, dentro das margens.

## 5. Varredura (final)

- Textos nas seções novas (sem a Tela 01): 148. Sem estilo v2: 0. Abaixo de 12 px: 0.
- Cores sólidas: 594. Sem variável: 0.
- Cards sobre o recorte (com cantoneiras de 6 px): 0. Fora das margens 16 a 1904 / 16 a 1064: 0.
- Textos fora do card: 0. Controles e figura dentro do card em todos os passos.

## 6. Dúvidas para o Alisson

1. **Espaço vazio no card grande.** A figura P6 está limitada a 480 px e ancorada na base; por isso sobra cerca de
   330 px entre a abertura e a figura, na coluna da esquerda. Se quiser a figura maior, é preciso ceder altura do infográfico.
2. **"Marca tracejada de 14 px".** Interpretei como o chip tracejado MOBILIZAÇÃO da lista (22 px de altura), seguido do
   texto da mobilização. Se o desenho for outro, troco.
3. **Pastilhas.** Coube lado a lado com a 1ª linha em Segoe SemiBold 17 (a largura útil do infográfico passou para 416).
4. **Empilhado.** A figura e os controles ficam alinhados, 28 px acima da base (é a linha dos controles).
5. **Amostra escura (`437:11936`).** Mantida só para legibilidade das cantoneiras no board.
6. **T2 a T4** não foram tocadas. O infográfico do passo 3 vive no card grande (T1); as outras telas criam a própria base.

## 7. Arquivos

- PNG dos 9 frames: `pbi/qa/tour/figma/t1-01.png` a `t1-09.png`.
- PNG da seção: `pbi/qa/tour/figma/sistema.png`.
- `passos.json` (T1): `card`, `personagem`, `layout`, `lado_final`, `figma_frame` em cada passo; `figma_componentes` novo no
  topo com os IDs desta revisão (`figma_componentes_v1` ficou como histórico).

## Parado em 07/10 (pedido do Alisson)

O trabalho no Figma foi interrompido por decisão do Alisson. O foco passa ao Power BI. Nenhuma chamada ao Figma ficou em curso, e nenhuma captura nova foi feita depois desta seção.

### Feito (arquivo `FjBWDk5odF9HaZ2pwhGosl`)

- Estilos: `v2/Tour · passo`, `título`, `texto`, `dica`, `botão`, `rótulo` e `pastilha`.
- `Tour · personagem` (`432:8406`): poses P1 a P6 como imagem FIT (variantes `432:8382`, `432:8386`, `432:8390`, `432:8394`, `432:8398`, `432:8402`), sem fundo creme e sem rótulo.
- `Tour · foco` (`432:8407`), `Tour · controles` (`433:8443`; variantes `433:8422`, `433:8429`, `433:8436`), `Tour · dica` (`439:14847`) e `Tour · cota` (`433:8421`, sem alteração).
- `Tour · card` (`442:11791`, 1500 × 1040; variantes `442:11647`, `442:11683`, `442:11719`, `442:11755`), com os paddings do empilhado corrigidos.
- `Tour · card grande` (`447:12086`), com instância `447:12178` e cota `447:12270` no frame `433:12013`. O componente antigo `440:11663` foi removido.
- Frames `433:11295` a `433:14167` (passos 1 a 9) montados no layout v2.
- PNG em `pbi/qa/tour/figma/`: `t1-01.png` a `t1-09.png` e `sistema.png`.
- `passos.json` (T1): card, layout, personagem, lado final e frame de cada passo, mais o bloco `figma_componentes`.

### Falta (ficou para depois)

- Nenhuma pendência obrigatória da T1 v2 no Figma; os itens acima estão completos.
- Pendências de decisão, já registradas na seção 6: espaço vazio de cerca de 330 px acima da figura P6 no card grande (passo 3); e a leitura de "marca tracejada de 14 px" como chip MOBILIZAÇÃO (22 px).
- T2 a T4 não foram iniciadas.
- Amostra escura `437:11936` mantida, com a opção de remoção em aberto.
