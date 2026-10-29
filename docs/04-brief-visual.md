# Brief visual · mockup Criticidade de Obras

Para o **Fable 5.1**. Este brief separa o pouco que é **fixo** do muito que é **seu**. Onde ele sugere algo, é
ponto de partida, não ordem.

> **Recado do Alisson:** o gabarito de componentes que está em `referencias/figma/proposta_kit_gabarito.png`
> **não é para ser seguido à risca**. Adote um estilo diferenciado, autoral, e use a liberdade total que você
> tem para construir um storytelling excelente. O Painel de referência e a proposta antiga mostram o nível de
> acabamento esperado — não o desenho a copiar.

---

## 1. Fixo

1. **Canvas 1920 × 1080** (página Power BI). As telas serão reconstruídas no Power BI depois — desenhe algo que
   possa existir lá (visuais nativos, HTML Content, SVG em DAX, Deneb, imagens de fundo).
2. **Sidebar + prancheta**, como o painel de referência: navegação fixa à esquerda, área de trabalho à direita.
3. **Somente a paleta do projeto** (seção 3). Nenhuma outra matiz — nem para status, alerta ou "positivo/negativo".
4. **Artes vetoriais de construção na sidebar:** **a maior na parte inferior**; **poucas e pequenas espalhadas
   na parte superior**. No painel de referência, a arte grande ocupa a base da sidebar e as pequenas ficam atrás do item ativo.
5. **A primeira tela mostra os maiores problemas**: quais obras e quais indicadores estão críticos neste mês, e por quê.
6. **A análise crítica de cada obra continua imprimível** — o cliente imprime o "quadradinho" (A4). Mostre como
   ela fica impressa (estado ou tela própria).
7. **Todo número vem de `mockup/data/criticidade-obras.json`.** Nada inventado. Formato pt-BR: `R$ 1,36 mi`,
   `R$ 293 mil`, `52,4%`, `−3,9 p.p.` (sinal de menos tipográfico).
8. **Selo de dado ilustrativo** onde aparecer POTENGI, DUNAS, REDINHA, JANGADA, TIROL, PONTA NEGRA ou efetivo.
   CAJUEIRO é real. Histórico: jan/26 a jun/26.

## 2. Livre

Estilo e linguagem visual, composição, número e ordem das telas, tipo de gráfico, hierarquia, tipografia de
destaque, microcopy, narrativa, interações, estados (filtros, tooltips, drill), forma de codificar status sem cor,
motivo das artes. Se achar que a pergunta de uma tela é outra, mude a tela.

## 3. Paleta do projeto

| Token | Hex | Origem / uso sugerido |
|---|---|---|
| `--offwhite` | `#F7F4EE` | fundo da proposta Construtora; canvas |
| `--branco` | `#FFFFFF` | superfícies |
| `--creme` | `#E9E0CF` | destaque quente, faixas, preenchimentos |
| `--grafite` | `#3B3B3F` | texto secundário, superfícies escuras secundárias |
| `--preto` | `#0B0B0C` | tinta do logo Construtora; texto, dado principal, sidebar |

Pode usar **opacidades e misturas entre esses cinco** (ex.: preto a 8% para linhas de grade, grafite a 60% para
texto auxiliar). Não pode trazer outra matiz. Ajuste os hex do creme e do grafite se o conjunto pedir, mantendo o
caráter (creme quente, grafite neutro) e contraste AA no texto.

Status sem cor é um desafio de design, não um limite: preenchimento (sólido × contorno × hachura), forma, peso,
posição, rótulo. Exemplo de partida: crítico = preto sólido; atenção = grafite com hachura ou contorno;
estável = creme. Decida você.

## 4. Tipografia

O Power BI e a proposta usam **Segoe UI**. Em ambiente Linux, a equivalente métrica é a **Selawik** (open source,
da Microsoft). Uma fonte de destaque é bem-vinda se puder existir no Power BI (título em SVG/imagem ou HTML Content).

## 5. Sidebar e artes

Ideias de partida (troque à vontade, desde que fale de construção/incorporação e combine com a Construtora):

- **Inferior (grande):** a orla de Natal em traço único — torres em estágios diferentes (uma pronta, uma só
  com a estrutura em lajes, uma com grua), e a **onda do logo Construtora** virando a linha da praia. Traço creme/grafite
  em baixa opacidade sobre o preto.
- **Superior (poucas e pequenas):** a lança de uma grua cruzando atrás do logo; um prumo pendurado num fio fino;
  uma marca de cota (▽ +12,00); cruzes de malha de planta baixa.
- Equivalente ao caminhão/rota do painel de referência: o cabo da grua descendo pontilhado até o item ativo da navegação.

Logos em `assets/logos/`: `construtora-branco.svg` (para fundo escuro), `construtora-tinta.svg`, `vizu-dados-horizontal.svg`
(assinatura discreta). Salve as artes finais em `assets/artes/` como SVG.

**Magnific** (conector): `images_generate_svg` gera vetor (Recraft v4). Consome créditos — gere poucas variações.
Sementes de prompt:
- *"Minimalist monoline line art of a coastal city skyline with residential high-rise towers at different
  construction stages, one tower crane, a smooth wave line as shoreline, uniform thin stroke, no fill, no text,
  transparent background, wide horizontal composition"*
- *"Minimalist monoline tower crane jib and hook with a thin dotted cable, uniform thin stroke, no fill, no text"*
Recolorir o SVG para os tokens antes de usar.

## 6. Material para o storytelling

O JSON já entrega as respostas; as telas organizam as perguntas. As sete perguntas de
`docs/03-indicadores-e-criticidade.md` são o roteiro:

1. Qual obra pede atenção agora? 2. Por quê? 3. Está piorando? 4. O resultado é de verdade (depende de estoque)?
5. Está no ritmo? 6. Gastou além do previsto no mês e justificou? 7. Posso confiar no número?

Ganchos de narrativa já presentes nos dados de jun/26:
- **REDINHA** atrasa no físico (−3,9 p.p.), gasta 36% acima do mês e acumula estoque e adiantamentos
  (R$ 811 mil): o resultado (+0,40%) se sustenta em material comprado e não aplicado.
- **POTENGI** chega à reta final (74% executado) com resultado negativo (−1,60%, −R$ 354 mil).
- **CAJUEIRO** (real) está adiantada (+4,3 p.p.) mas o resultado caiu 0,49 p.p. e depende de R$ 1,17 mi em estoque e
  adiantamentos; desembolsou 58% acima do previsto e a justificativa ficou em branco.
- **DUNAS** é a referência: +2,30% e no ritmo.
- **PONTA NEGRA** está encerrando (99,2% executado) com resultado de +1,40% — a obra que fecha bem.
- **TIROL** está em mobilização (3,6%): resultado negativo esperado nesta fase.
- **Carteira**: 7 obras, R$ 163,8 mi; R$ 731 mil de resultado (+0,45%), −R$ 361 mil no mês.
- **Conferência**: a planilha real tem R$ 78 mil fora da conta (FEV26) por um total sem fórmula.
- **Próximas obras**: quatro obras a iniciar entram entre jul e out/26 (R$ 147 mi em orçamento legal).
- **Etapa 2 (prévia, opcional)**: efetivo por categoria (841 pessoas em jun/26, fictício). A etapa 2 ainda
  será discutida com o cliente — se entrar, que seja como prévia discreta.

Campos úteis do JSON: `carteira` (KPIs + `serie` mensal + `sintese`), `obras[]` ordenadas por pontuação com
`ultimo` (indicadores, `indicadores_status`, `sinais` com frase pronta, `justificativa`), `composicao` (os dez
itens do quadradinho), `itens_ultimo_mes`, `serie`, `efetivo`, `qualidade`; `proximas`, `concluidas`, `meta`.

## 7. Entregáveis

- `mockup/` — código das telas, renderizando a partir do JSON (tecnologia à sua escolha) + `mockup/README.md`
  curto (como abrir/renderizar e decisões de design).
- `mockup/prints/` — PNG 1920 × 1080 de cada tela e dos estados principais (filtros abertos, tooltip, impressão).
- `assets/artes/` — SVGs finais da sidebar.
- Opcional, combinado com o agente principal: as telas no Figma (arquivo do portfólio Vizu, página nova
  "Criticidade de Obras").

## 8. Barra de qualidade

- Cada tela responde uma pergunta clara, escrita no título ou subtítulo.
- Hierarquia legível em 3 segundos; nada sobreposto, cortado ou desalinhado; respiro generoso.
- Números conferidos com o JSON; unidades e sinais certos; rótulos sem jargão desnecessário.
- Contraste AA; status distinguível em escala de cinza e por quem não enxerga cor.
- Nada com cara de template genérico.
