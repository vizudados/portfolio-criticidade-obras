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

### 2.2 Card comum · layout "lado a lado" (padrão, 720 de largura)

- Superfície: `base/branco`, **raio 16**, contorno 1 px `base/preto`, sombra `v2/Sombra · tooltip`. Altura pelo
  conteúdo (sem rolagem); conteúdo nunca cortado.
- **Cabeçalho preto** no topo, 720 × 56, com os cantos de cima arredondados (16): "PASSO 3 DE 9" (`v2/Tour · passo`,
  `base/creme`) começando depois da coluna do personagem; **régua de progresso** logo à direita (N segmentos de 18 × 5,
  vão 5, raio 2,5; feitos `base/creme`, atual `base/branco`, futuros `base/grafite`); **Fechar ×** à direita: círculo de
  44 × 44 (fundo `base/grafite` a 0 % e, no hover, 100 %; glifo 16 px, traço 2 px `base/branco`), área de clique 56 × 56.
- **Personagem**: imagem **230 × 345**, pé na base do card (8 px da borda lateral), sobe por cima do cabeçalho e pode
  passar até 40 px acima do card. Fica do lado do card mais próximo do foco (esquerda quando o foco está à esquerda,
  acima ou abaixo; direita quando o foco está à direita) e aponta para ele.
- **Coluna de texto**: largura 410 (personagem à esquerda: x 282 a 692; à direita: x 28 a 438). Padding de 28 no topo
  do corpo.
  - título `v2/Tour · título` `base/preto`;
  - 12 px abaixo, texto `v2/Tour · texto` `base/grafite` (até 7 linhas);
  - 16 px abaixo, **dica** (se houver): caixa `base/creme` com raio 10, padding 10 × 14, ícone de cursor de 18 px
    `base/preto` à esquerda, texto `v2/Tour · dica` `base/preto`;
  - 24 px abaixo, **controles** alinhados à direita da coluna, 28 px acima da base: "Próximo →" 148 × 48, raio 10,
    fundo `base/preto`, texto `v2/Tour · botão` `base/branco`; "Anterior" 128 × 48, raio 10, contorno 1,5 px
    `base/preto`, fundo `base/branco`, texto `v2/Tour · botão` `base/preto`; vão 10; área de clique ≥ 56 de altura.
    **Passo 1:** o da esquerda é "Pular tour". **Último passo:** o da direita é "Concluir ✓" (se o ✓ não renderizar
    em Segoe, use um ícone vetorial).

### 2.3 Card comum · layout "empilhado" (quando o espaço livre ao lado do foco é menor que 720)

- Largura = espaço livre (mínimo 480). Texto, dica e título na largura toda (padding 28). O personagem (**190 × 285**)
  fica no canto de baixo do lado do foco, e os controles ficam ao lado dele, na base. Mesmo cabeçalho, mesmos estilos.

### 2.4 Card grande (um por tela)

- Mesmo cabeçalho (com rótulo, régua e Fechar), mesma superfície e raios. Usa o maior espaço livre ao lado do foco
  amplo, **mínimo 760 de largura onde couber**; nunca cobre o foco.
- Personagem P6 **grande**: altura = altura útil do corpo − 40, até 480, ancorado na base, na coluna do lado do foco
  (sem coluna vazia acima dele). Coluna de conteúdo com padding 32.
- Conteúdo do `passos.json` (`conteudo`) como mini-infográfico com as cores v2, sem inventar número, fontes do §2.1
  (título 30, texto 17, rótulos de bloco `v2/Tour · rótulo`):
  - T1 · Pontuação: barra 0–100 dividida pelos pesos (35/25/20/10/10), raio 6, com nome e peso; a regra com três
    pastilhas (raio 10) `status/estavel-claro`, `status/atencao-claro`, `status/critico-claro`; o **exemplo** numa caixa
    `base/creme`; a régua das faixas (`status/estavel` #A9CDB9 · `status/atencao` #C9821F · `status/critico` #C43737,
    raio 6) com os limites 25 e 50; a mobilização com a marca tracejada; a nota em `v2/Tour · dica`.
  - T2 · Quadradinho: a conta em degraus (+ + − − =) com nome e explicação de cada parte; o fecho em caixa creme; dica.
  - T3 · Curva S: mini-legenda tracejado × sólido e área de atraso; a régua do desvio físico; mobilização; fecho; dica.
  - T4 · Resultado mês a mês: mini-legenda barra cheia × hachurada (`Hachura · v2`); leitura; régua do resultado; dica.
- Os limites de faixa ficam neutros (`base/grafite`).

## 3. Posição do card

Use o `lado` do `passos.json` como preferência. Regras, em ordem:
1. O card (e a cabeça do personagem) nunca cobre o recorte nem as cantoneiras.
2. 40 px até o anel; alinhado ao início do foco no eixo transversal, limitado pelas margens.
3. Se no lado preferido couber 720, use "lado a lado"; se couber entre 480 e 720, "empilhado"; se não couber 480,
   tente o lado oposto, depois acima/abaixo. Registre o lado e o layout finais.
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
