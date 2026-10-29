# Brief · Tour guiado da Construtora (Figma e Power BI) · v2

07/10/2026 · orquestrador Opus 5.5 · execução por agentes Haiku 5.5.
Fonte única dos passos: `pbi/spec/tour/passos.json` (textos v2). Mecânica de referência: a referência de outro projeto (fora deste repositório)
**Parte A só** (a Parte B é visual do painel de referência e NÃO se reproduz). Inventário do guia atual: `pbi/spec/tour/inventario-guia.md`.

**O que mudou da v1 para a v2 (pedido do Alisson ao ver a T1):** "Cantos arredondados, ocupar mais espaço e não ser tão
resumido, fonte maior". Ou seja: cantos arredondados em card, botões, foco e pastilhas; card maior; texto mais completo
(até 7 linhas + uma linha de dica); tipografia maior; personagem maior. O resto (véu, recorte, cantoneiras, cota, cabeçalho
preto com régua de passos, mecânica) continua.

## 1. O que é

O "Guia da página" (quadro de 1120 que cobre a tela) sai. Entra um **tour guiado passo a passo**, aberto pelo "?" redondo
do cabeçalho (`T<n>_Aj_Guia`, 1816,38). Cada passo escurece a página, recorta o elemento explicado e mostra, **ao lado do
elemento e nunca por cima dele**, um card com o gestor da Construtora (personagem 3D) narrando. Um passo por tela é um **card
grande** que explica o gráfico principal (T1: a pontuação de criticidade).

**O visual é próprio da Construtora.** Da painel de referência valem só o objetivo e a mecânica. Não copie nada visual do painel de referência.

## 2. Linguagem visual · "esquadro de obra", com cantos arredondados

Tudo com as variáveis e estilos v2 do arquivo Figma (`pbi/spec/redesenho/ledger-figma.json`).

| Peça | Especificação |
|---|---|
| Véu | retângulo 1920 × 1080, `base/preto` #0B0B0C a **64 %**, com o recorte do foco subtraído |
| Recorte do foco | retângulo do elemento (do `passos.json`) + **8 px** de folga em cada lado, **raio 14** |
| Anel do foco | traço **2 px** `base/creme` #E9E0CF, mesmo retângulo e raio do recorte |
| Cantoneiras de esquadro | 4 cantos em "L" com a curva do canto acompanhando o raio (raio 20 no L), braço **24 px**, traço **3 px** `base/branco`, ponta arredondada, **6 px** para fora do anel |
| Linha de cota (conector) | do meio da borda do card voltada ao foco até o anel; traço **1,5 px** `base/creme`, tracejado **[6, 4]**, tique de **10 px** perpendicular em cada ponta. Só se o vão for ≥ 24 px |
| Distância card–anel | **40 px** |
| Margem do canvas | o card (e a cabeça do personagem) fica entre x 16 e 1904, y 16 e 1064 |

### 2.1 Estilos de texto novos (criar no Figma, família v2)

| Estilo | Fonte | Uso |
|---|---|---|
| `v2/Tour · passo` | Segoe UI SemiBold 14, caixa alta, espaçamento 1,2 | "PASSO 3 DE 9" |
| `v2/Tour · título` | Barlow SemiBold 30 / 36 | título do card |
| `v2/Tour · texto` | Segoe UI 17 / 26 | texto do card |
| `v2/Tour · dica` | Segoe UI 15 / 22 | linha "como usar" |
| `v2/Tour · botão` | Segoe UI SemiBold 16 | Anterior / Próximo / Pular / Concluir |
| `v2/Tour · rótulo` | Segoe UI SemiBold 13, caixa alta, espaçamento 1 | rótulos de bloco no card grande |

### 2.2 Estrutura v3 do card (revisão do orquestrador, 07/10 à noite — vale para TODOS os cards)

Pedido do Alisson ao abrir o tour no Desktop: "os elementos não estão bem posicionados e fica um vão branco. Se for o
caso coloque um rodapé com os botões de voltar e seguir." A v2 (personagem numa coluna ao lado do texto, botões soltos no
corpo, altura vinda do Figma) sai. A v3 tem **três faixas empilhadas, sem coluna de personagem no corpo**:

```
┌──────────────────────────────────────────────────────┐
│ CABEÇALHO preto 56 · PASSO 3 DE 9 ▬▬▬▬▬▬▬▬▬       ×  │  cantos de cima com raio 16
├──────────────────────────────────────────────────────┤
│ CORPO branco · padding 24 28 24 28                    │
│ Título (Barlow SemiBold 30/36, preto)                 │
│ Texto (Segoe UI 17/26, grafite) — LARGURA TODA        │
├──────────────────────────────────────────────────────┤  linha 1 px #E9E0CF
│ RODAPÉ "palco" offwhite #F7F4EE · cantos de baixo 16  │
│ ┌busto┐  ↖ cursor  dica (Segoe 15/22, preto)          │
│ │     │                                              │
│ │     │                    [← Voltar] [Seguir →]      │
└─┴─────┴──────────────────────────────────────────────┘
   busto cortado na cintura, rente à base do card
```

- **Altura = conteúdo.** Corpo = título + 12 + texto, mais o padding. Rodapé = altura do busto. Nada de altura fixa
  nem a `h` gravada pelo Figma: do `card` do `passos.json` só valem `x`, `w` e o lado. Se o lado final for "acima",
  `y` = topo do recorte − 40 − altura. **Nenhum vão vazio maior que 24 px** em lugar nenhum do card.
- **Rodapé (palco):** fundo `base/offwhite` #F7F4EE, linha de cima 1 px `base/creme` #E9E0CF, padding 16 20 20 20.
  - **Busto** do lado do foco (esquerda quando o foco está à esquerda, acima ou abaixo; direita quando à direita),
    ancorado na BASE do card (o corte da cintura rente à borda de baixo), apontando para o foco. Altura do busto =
    altura do rodapé: **190** nos cards de 600 ou mais de largura, **170** nos mais estreitos; largura proporcional,
    no máximo 220 (se a pose de braço estendido passar disso, reduza a altura até caber, mínimo 150). Margem mínima de
    12 px entre qualquer pixel opaco do busto e a borda lateral do card (use o bbox do alfa).
  - **Coluna do rodapé** (o resto da largura, do outro lado do busto): dica no topo (ícone de cursor 16 px + texto
    `v2/Tour · dica`, sem caixa, até 3 linhas) e, na base, os **botões lado a lado**, alinhados ao lado oposto ao
    busto: "← Voltar" (contorno 1,5 px preto, fundo branco) e "Seguir →" (fundo preto, texto branco), **mesma altura
    44 e mesma largura** (132 nos cards de 600+, 116 nos estreitos), raio 10, vão 8, texto Segoe UI SemiBold 16; área
    de clique ≥ 56 de altura (o botão transparente do Power BI pode ser maior que o desenho, centrado nele).
    **Passo 1:** "Pular tour" no lugar de "← Voltar". **Último passo:** "Concluir ✓" no lugar de "Seguir →".
  - Sem dica: os botões ficam na base, como sempre; o palco fica com o busto e os botões.
- **Larguras:** card comum **680** (corpo com 624 de texto); quando o espaço livre ao lado do foco for menor, a
  largura é o espaço livre (mínimo 480; ex.: T1 passo 4 = 500). Não existe mais o layout "empilhado" separado: é a
  mesma estrutura, mais estreita.
- **Cabeçalho:** como na v2 ("PASSO n DE N" a 28 px da borda esquerda, régua de passos, × de 44 com área de 56).

### 2.3 Card grande (um por tela) na estrutura v3

- Mesmo cabeçalho; **corpo** com título + abertura na largura toda e, abaixo, o infográfico do `conteudo` (uma ou duas
  colunas, conforme a largura); **rodapé palco** com o busto P6 (altura **230**), a dica e os botões. Sem coluna de
  personagem no corpo.
- **Cards grandes com altura limitada** (T3 e T4, abaixo do gráfico, ~363–373 px livres): o palco vira uma **faixa
  lateral** do lado do foco, com 240 de largura, do cabeçalho até a base, com o busto P6 ancorado na base; o corpo
  (título, textos e infográfico em duas colunas) fica ao lado, e os botões ficam numa linha de rodapé branca de 72 na
  base do corpo, alinhados à direita. Fontes nunca abaixo do §2.1 (sem escala).
- Conteúdo do infográfico como na v2: T1 pesos com número, regra em três pastilhas, exemplo em caixa creme, faixas,
  mobilização com marca tracejada de 14 px, nota; T2 conta em degraus e fecho; T3 legenda e régua do desvio; T4 régua
  do resultado. Limites de faixa neutros.

## 3. Posição do card

Use o `lado` do `passos.json` como preferência. Regras, em ordem:
1. O card (e a cabeça do personagem) nunca cobre o recorte nem as cantoneiras.
2. 40 px até o anel; alinhado ao início do foco no eixo transversal, limitado pelas margens.
3. Se no lado preferido couber 680, use 680; se couber entre 480 e 680, use a largura livre; se não couber 480,
   tente o lado oposto, depois acima/abaixo. Registre o lado e a largura finais.
4. O card pode cobrir outros elementos (estão escurecidos).

## 4. Poses do personagem

P1 acenando · P2 apontando para a esquerda · P3 apontando para a direita · P4 explicando com as mãos · P5 polegar para
cima · P6 segurando uma prancheta. Arquivos em `assets/personagem/poses/` (nomes no `passos.json`, `poses_arquivos`).
Enquanto não existirem, o componente `Tour · personagem` mostra o espaço reservado (retângulo `base/creme` com raio 16,
silhueta em `base/offwhite`, rótulo da pose). Quando chegarem, troca-se o preenchimento das variantes por imagem (fill
"Fit", ancorado embaixo) e todas as instâncias acompanham.

## 5. Figma (arquivo `FjBWDk5odF9HaZ2pwhGosl`, página `04 · Redesenho v2 · Painel Criticidade de Obras` `372:685`)

- Seção `Tour · sistema` (`432:8381`) e seção `Tour · T01` (`433:11294`) já existem (v1). Atualize os componentes no
  lugar (mesmos IDs sempre que der) e refaça os frames da T1. Novas seções `Tour · T02`…`Tour · T04` ao lado.
- Componentes: `Tour · card` (variantes `Layout=Lado a lado|Empilhado` × `Personagem=Esquerda|Direita`),
  `Tour · card grande`, `Tour · foco`, `Tour · cota`, `Tour · controles` (`Passo=Primeiro|Meio|Último`),
  `Tour · personagem` (`Pose=P1…P6`), `Tour · dica`.
- Frame por passo 1920 × 1080, nome `Tour · T1 · 03 de 09 · PONTUACAO`: instância da `Tela 0N · v2` + véu + foco + cota
  + card (instâncias; textos por override).
- **Meça o foco no nó real** quando `foco_fonte` ≠ "figma". Grave no `passos.json` (só os campos do passo): `foco`
  exato com `foco_fonte` = "figma", `card` {x,y,w,h}, `personagem`, `layout`, `lado_final`, `figma_frame`.
- Piso de fonte 12; todos os textos com estilo v2; todas as cores por variável v2.

## 6. Power BI

- Por tela: marcador fechado `T<n>_TOUR_00` + um por passo `T<n>_TOUR_<NN>`, grupo `("tour", "Tour")`, só exibição.
- Por passo: um visual HTML Content 1920 × 1080 em (0, 0), oculto na base, com o desenho do passo (véu, recorte, anel,
  cantoneiras, cota, card, personagem, controles desenhados) + três botões transparentes por cima dos controles.
- Geometria do card, personagem e layout: do `passos.json` (gravados pelo Figma). CSS espelha o §2.
- Personagem: PNG transparente embutido em base64 (≤ ~150 KB por pose, 2x do tamanho no card), lido de
  `poses_arquivos`; se o arquivo não existir, espaço reservado em SVG.
- Prova: lint 0 ERRO, simulações, `--aplicar`, `--conferir` 0, fotos de cada passo, teste por clique no Desktop.
