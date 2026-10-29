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

### 2.2 Estrutura v5 · narrador no canto e card-balão (referência do Alisson, 07/10 à noite — vale para TODOS os passos)

O Alisson mandou como "exemplo bom" o tour de outro painel da Vizu: `pbi/spec/tour/referencia-balao-people-analytics.png`.
Vale a ESTRUTURA dele, com as cores e a identidade da Construtora (preto, creme, offwhite, status v2, Barlow/Segoe,
cantoneiras de esquadro no foco). NÃO copiar o lilás nem a personagem de lá. As estruturas v2–v4 (personagem dentro do
card, palco, faixa) saem.

**Composição de cada passo (overlay 1920 × 1080):**
1. Véu `#0B0B0C` a 60 % com o recorte do foco (raio 14), anel 2 px `#E9E0CF`, cantoneiras de esquadro como antes.
2. **Narrador** — o gestor GRANDE, fora do card, num canto de BAIXO da tela, cortado na cintura pela borda inferior
   do canvas (y 1080 = linha da cintura): busto de **520 px** de altura (card grande: 560), largura proporcional.
   - Canto padrão: **direito** (busto encostado a 40 px da borda direita). Se o retângulo do busto (com 24 px de folga)
     tocar o recorte do foco, use o canto **esquerdo** (40 px da borda esquerda, por cima da sidebar escurecida). Se
     tocar nos dois cantos, reduza o busto até 380; se ainda tocar, use o canto que cobre menos e registre.
   - Pose: P1 no passo 1 (acenando), P5 no último (polegar), P6 no card grande; nos demais, o gesto para dentro da tela
     (canto direito → P2 "apontando para a esquerda" ou P4; canto esquerdo → P3 ou P4), conforme o `passos.json`
     (se a pose do json apontar para fora da tela, troque pela que aponta para dentro e registre).
   - Sombra suave no chão não precisa; o busto é PNG transparente (versão `busto/`, com resolução de origem ≥ 1x da
     altura exibida).
3. **Card-balão** — branco `#FFFFFF`, **raio 24**, sem contorno preto (contorno 1 px `#E9E0CF` opcional), sombra
   `0 18px 48px rgba(11,11,12,.28)`, padding **28 32 24 32**, largura **560** (card grande: até **760**; altura limitada
   → colunas internas, nunca fonte menor).
   - **Biquinho** (triângulo branco de 22 × 14, mesma sombra) na borda do balão voltada para a CABEÇA do narrador,
     apontando para ela (no exemplo: borda de baixo, perto do canto do lado do narrador).
   - Conteúdo, de cima para baixo:
     a. **selo** "Passo 3 de 9" — pílula `#E9E0CF`, texto `#0B0B0C` Segoe UI SemiBold 13, padding 4 × 12, raio 999;
     b. 14 px; **título** Barlow SemiBold 30/36 `#0B0B0C` (até 2 linhas);
     c. 12 px; **texto** Segoe UI 17/26 `#3B3B3F`;
     d. 14 px; **dica** (se houver): ícone de cursor 16 px + Segoe UI 15/22 `#0B0B0C`;
     e. 22 px; **linha de controles**: à esquerda a régua de passos (N traços de 26 × 4, vão 6, raio 2; atual
        `#0B0B0C`, feitos `#0B0B0C` a 45 %, futuros `#E1E1E1`); à
        direita, alinhados à direita e centrados verticalmente: **"Pular"** (link: Segoe UI 15 `#6B6B70`, sem caixa,
        área de clique 64 × 56), **"Voltar"** (contorno 1,5 px `#0B0B0C`, fundo branco, 92 × 44, raio 12) e
        **"Seguir →"** (fundo `#0B0B0C`, texto branco, 124 × 44, raio 12), vão 10; Segoe UI SemiBold 16 nos botões.
        Passo 1: "Voltar" some (fica só "Pular" e "Seguir →"). Último passo: "Seguir →" vira "Concluir ✓" e "Pular"
        some. **Não há ×**: "Pular" fecha o tour (é o terceiro controle da L030).
   - **Posição do balão:** encostado ao narrador, do lado de dentro da tela, com o biquinho chegando a ~24 px da
     cabeça (no exemplo: balão acima e à esquerda da cabeça, biquinho embaixo). Nunca cobre o recorte do foco nem o
     rosto do narrador; dentro das margens 24 px. Se não couber perto do narrador sem tocar o foco, ponha o balão ao
     lado do foco (40 px do anel) e mantenha o biquinho voltado para o narrador.
4. **Ligação com o foco:** linha pontilhada (traço 2 px `#E9E0CF`, pontos [2, 6], pontas redondas) do ponto da borda do
   balão mais próximo do foco até o anel, terminando num **ponto** de 8 px `#E9E0CF` com contorno 2 px `#0B0B0C` sobre o
   anel. Sem tiques de cota.
5. **Altura do balão = conteúdo.** Nenhum vão > 24 px. Nada de altura do Figma.

**Card grande** (um por tela): mesmo balão, maior (até 760 de largura), com selo, título, abertura e o infográfico do
`conteudo` (como na v2–v4: T1 pesos com número, regra em três pastilhas, exemplo em caixa creme, faixas, mobilização
com marca tracejada de 14 px, nota; T2 conta em degraus e fecho; T3 legenda e régua do desvio; T4 régua do resultado),
e a mesma linha de controles. Narrador com P6, 560 de altura.

**Botões transparentes do Power BI** exatamente sobre "Pular", "Voltar" e "Seguir" desenhados (centro com erro ≤ 1 px;
altura ≥ 56; sem sobreposição entre eles). O visual HTML do passo continua 1920 × 1080 em (0, 0).

## 3. Posição do card

Use o `lado` do `passos.json` como preferência. Regras, em ordem:
1. O card (e a cabeça do personagem) nunca cobre o recorte nem as cantoneiras.
2. 40 px até o anel; alinhado ao início do foco no eixo transversal, limitado pelas margens.
3. (v5) O balão segue o §2.2: perto do narrador; se não couber sem tocar o foco, ao lado do foco (40 px do anel); se não couber 480,
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
