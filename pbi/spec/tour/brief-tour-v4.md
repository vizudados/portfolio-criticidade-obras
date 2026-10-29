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

### 2.2 Estrutura v4 do card (proposta do Alisson, 07/10 à noite — vale para TODOS os cards, comuns e grandes)

Pedido do Alisson ao ver a v3: "e se ele ficar de um lado com o botão de pular e seguir um abaixo do outro e do outro
cabeçalho e texto empilhados? do jeito atual ainda não está bom". A v3 (rodapé palco) sai. A v4 tem DUAS COLUNAS:

```
┌───────────────┬─────────────────────────────────────────┐
│ FAIXA DO      │ CABEÇALHO preto 56 · PASSO 3 DE 9 ▬▬▬  × │
│ GESTOR        ├─────────────────────────────────────────┤
│ offwhite      │ CORPO branco · padding 24 28             │
│               │ Título (Barlow SemiBold 30/36)           │
│   [busto]     │ Texto (Segoe UI 17/26, grafite)          │
│   aponta →    │ ↖ dica (Segoe 15/22) — se houver         │
│ ┌───────────┐ │                                         │
│ │ Seguir →  │ │                                         │
│ ├───────────┤ │                                         │
│ │ ← Voltar  │ │                                         │
│ └───────────┘ │                                         │
└───────────────┴─────────────────────────────────────────┘
```

- **Faixa do gestor** do lado do FOCO (esquerda quando o foco está à esquerda, acima ou abaixo; direita quando à
  direita), na ALTURA TODA do card (canto de cima e de baixo daquele lado com raio 16), fundo `base/offwhite` #F7F4EE,
  separada do resto por 1 px `base/creme` #E9E0CF. Largura **220** nos cards de 600+ e nos grandes; **180** nos estreitos.
  - **Botões empilhados** na base da faixa, padding 16 nas laterais e na base: em cima "Seguir →" (fundo preto, texto
    branco), embaixo "← Voltar" (contorno 1,5 px preto, fundo branco); largura = faixa − 32; altura 44; vão 8; raio 10;
    Segoe UI SemiBold 16. Passo 1: "Pular tour" no lugar de "← Voltar". Último passo: "Concluir ✓" no lugar de
    "Seguir →". Área de clique dos botões transparentes do Power BI ≥ 56 de altura, centrada no desenho (a área de cima
    e a de baixo não podem se sobrepor: divida o vão entre elas).
  - **Busto** centrado na faixa, apontando para o foco, com a CINTURA ESCONDIDA atrás do bloco de botões: a base do busto
    fica 24 px abaixo do topo do botão de cima (os botões são desenhados por cima). Altura do busto = espaço da faixa
    acima dos botões + 24 − 12 de folga no topo, limitada a **300** (comuns) e **340** (grandes) e no mínimo 160; se
    sobrar espaço acima da cabeça, ele fica na faixa offwhite (não é vão branco). Margem ≥ 12 px entre qualquer pixel
    opaco do busto e as bordas da faixa (bbox do alfa).
- **Coluna do texto** (o resto da largura): **cabeçalho preto** 56 no topo (canto de cima do lado oposto à faixa com
  raio 16): "PASSO n DE N" a 24 px da borda, régua de passos, × de 44 com área de 56 no canto. Abaixo, **corpo branco**,
  padding 24 28 24 28: título (30/36), 12 px, texto (17/26), 16 px, dica (ícone de cursor 16 px + Segoe 15/22, preto,
  sem caixa) — tudo empilhado, na largura da coluna.
- **Altura do card** = max(cabeçalho + corpo, mínimo da faixa = 12 + 160 − 24 + 44 + 8 + 44 + 16 = 260). Nada de altura
  fixa nem a `h` do Figma (do `card` só `w` como teto e o lado). Se o lado final for "acima", recalcule `y`.
  Nenhum vão branco > 24 px na coluna do texto.
- **Larguras:** comum **720** (texto com ~444); se o espaço livre ao lado do foco for menor, a largura livre (mínimo
  480; T1 passo 4 = 500, faixa 180).
- **Card grande:** mesma estrutura. Faixa de 220 com o busto P6 (até 340) e os botões; coluna do texto com o cabeçalho
  preto e o corpo: título + abertura e, abaixo, o infográfico do `conteudo` (uma ou duas colunas conforme a largura) e,
  no fim, a nota/dica. Nos de altura limitada (T3 e T4 passo 3, abaixo do gráfico, ~363–373 px livres), o corpo usa
  duas ou três colunas internas para caber; fontes nunca abaixo do §2.1 (sem escala). Conteúdo do infográfico como na
  v2/v3 (T1 pesos com número, regra em três pastilhas, exemplo em caixa creme, faixas, mobilização com marca tracejada
  de 14 px, nota; T2 conta em degraus e fecho; T3 legenda e régua do desvio; T4 régua do resultado). Limites de faixa
  neutros.
- A **linha de cota** sai do meio da borda da FAIXA (o lado do foco) até o anel.

## 3. Posição do card

Use o `lado` do `passos.json` como preferência. Regras, em ordem:
1. O card (e a cabeça do personagem) nunca cobre o recorte nem as cantoneiras.
2. 40 px até o anel; alinhado ao início do foco no eixo transversal, limitado pelas margens.
3. Se no lado preferido couber 720, use 720; se couber entre 480 e 720, use a largura livre; se não couber 480,
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
