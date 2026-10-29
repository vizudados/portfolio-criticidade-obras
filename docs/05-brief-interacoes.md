# Brief · interações do mockup (verso dos cartões, tooltips e storytelling do "?")

Para o **Fable 5.1**. Pedido do Alisson em 06/10/2026, ao abrir a produção no Power BI:

> "Peça para o Fable desenhar os tooltips, com total liberdade criativa — todos os gráficos terão, com exceção dos
> cards, é claro: no caso deles serão flips. E quero excelentes storytellings também (que se acionam quando clica na
> interrogação, padrão do trabalho Vizu Dados). Desenhar todos dentro do mockup no Figma."

**Liberdade criativa total** no desenho e na escrita das três peças. O que segue é o contrato mínimo (o que o Power BI
precisa para reconstruir) e o mapa do que existe — não um layout.

## Onde

- Figma: arquivo `FjBWDk5odF9HaZ2pwhGosl`, página **`03 · Mockup · Painel Criticidade de Obras`** (`269:685`).
- Ferramentas: o conector **figma-conta2** (`mcp__figma-conta2__*`, conta alisson@vizudados.com.br — tem edição).
  O outro conector do Figma não enxerga as páginas novas.
- Telas existentes (componentes): `281:720` Tela 01 · Visão geral · `281:724` Tela 01 · Filtros abertos ·
  `281:721` Tela 02 · Análise crítica · `281:722` Tela 03 · Avanço físico · `281:723` Tela 04 · Resultado no tempo.
  Prints em `mockup/prints-figma/`.
- A página `02 · Proposta` (`246:685`) usa **instâncias** dessas telas: o que mudar nelas aparece lá também. Não
  edite a proposta.

## 0. Antes das interações: dois ajustes nas telas

1. **Tirar o Efetivo do painel.** Decisão do Alisson (06/10): a aba de pessoas fica para outro momento e **não
   aparece no dashboard**. Remova da sidebar o bloco "ETAPA 2 · A COMBINAR / 05 Efetivo · prévia" nas cinco telas
   (inclusive "Filtros abertos") e refaça o respiro da sidebar sem buraco.
2. **"?" em cada painel de gráfico.** Padrão Vizu: todo painel de gráfico tem um "?" no canto que abre o
   storytelling daquele gráfico. **Cartão de KPI não tem "?"** (ele tem o verso). O "?" redondo do cabeçalho
   continua e abre o **guia da página** (§3).

## 1. Verso dos cartões (flip)

Cada cartão da faixa de KPIs (5 por tela, 20 no total) tem verso. No Power BI o flip é um HTML Content: frente e
verso no mesmo visual; no hover (e no foco) a frente desliza para cima e o verso entra. Contrato:

- O verso ocupa **a coluna inteira do cartão** (da régua à régua), não só a largura do texto da frente.
- Conteúdo: **como é calculado** (regra curta, até 3 linhas, em pt-BR de gente — sem nome de coluna) e **de onde
  vem** (1 linha: aba/célula da planilha Análise Crítica, ou "Power Query · todas as obras"). Pode ter a faixa de
  criticidade quando o cartão for um indicador da régua.
- Superfície do verso: uma das cores da paleta, com contraste AA. O cartão escuro da frente já é preto — o verso
  dele precisa se distinguir (decisão sua).
- Desenhe os 20 versos como componentes à parte (`Verso · T1 · <cartão>`), mais **um** estado "cartão virando"
  montado sobre uma tela, para mostrar o gesto.

## 2. Tooltip de cada gráfico

Todo gráfico tem tooltip que **aprofunda** o ponto sob o mouse — composição, causa, tempo ou distribuição — e
**nunca repete** o número que já está visível no gráfico. Pode ter mini gráfico, status com a forma da régua
(sólido / hachura / creme / tracejado), selo REAL / ILUSTR.

Mapa do que existe hoje (você pode juntar, separar ou mudar o gráfico se a tela pedir — avise):

| Tela | Gráfico | Ponto do tooltip | Pistas do que aprofundar |
|---|---|---|---|
| 01 | Obras por criticidade | a obra | os 5 sinais com faixa e pontos; série de pontos jan–jun; o que mudou desde maio |
| 01 | O que pesa na carteira | o indicador | quais obras em crítico / atenção, com o valor de cada uma; a faixa |
| 01 | Como o semestre evoluiu | o mês | quais obras em cada status naquele mês; quem entrou ou saiu de crítico |
| 02 | O quadradinho | o item (linha) | o que é o item (texto da própria planilha) e as linhas da tabela anexada que o compõem (`itens_ultimo_mes`) |
| 02 | Como o resultado se forma | o degrau | composição do degrau (itens), peso no orçamento |
| 02 | Resultado da obra, mês a mês | o mês | estoque, adiantamentos, crédito e desembolso naquele mês; variação |
| 02 | Sinais do mês | o indicador | faixa, peso, valor nos 6 meses |
| 03 | Curva S | o mês | previsto × executado no mês e acumulado, desvio, tendência |
| 03 | Ritmo do mês | o mês | idem, com foco no mês |
| 03 | Avanço das sete obras | a obra | início, término, orçamento, status, desvio |
| 03 | Linha do tempo das obras | a obra | idem; obras a iniciar com orçamento legal (cronograma) |
| 04 | Resultado da carteira, mês a mês | o mês | contribuição de cada obra; ativos não consumidos |
| 04 | Resultado por obra | a obra | série de 6 meses, melhor e pior mês |
| 04 | Desembolso da carteira | o mês | previsto × desembolsado por obra |
| 04 | Desembolso de jun/26 por obra | a obra | histórico do desvio e das justificativas |

Contrato para o Power BI:
- Tamanho real de tooltip de página: até ~**480 × 420 px**, a 100% (sem ampliar no Figma).
- Desenhe os estados **completo, parcial e vazio** onde o dado pode faltar (L036): ex. obra em mobilização (TIROL),
  mês sem previsto, item sem linhas anexadas, primeiro mês sem "mês anterior". Dado ausente some e o resto reflui;
  zero real aparece como zero.
- Cada tooltip como componente (`Tooltip · T1 · Obra`, …), e **um** exemplo montado sobre a tela, apontando o ponto.

## 3. Storytelling do "?" (e o guia da página)

O "?" de cada painel abre a **leitura** daquele gráfico (no Power BI: marcador de exibição que liga um véu e um
painel HTML; "fechar" volta ao estado normal sem mexer em filtro nem página). Padrão Vizu de conteúdo:

- **sobretítulo** (qual gráfico) · **achado no título** (a frase que responde, com o número-chave) ·
  **explicação** com estado, causa e impacto · **o que explica** (o porquê / o que puxa) · **detalhe** · **método**
  (como ler, a régua) · **fechar**.
- **Cada número aparece uma vez por leitura (L058):** o achado leva o número-chave; a explicação diz estado, causa
  ou impacto **sem repetir** os números dos destaques; os destaques (até três) trazem números novos. Mini gráfico
  pode visualizar o achado.
- Texto factual, sem frase de efeito. É leitura de diretoria de construtora.
- Os textos serão **dinâmicos** no Power BI (mudam com a obra e o mês). Escreva a leitura do recorte do mockup
  (jun/26, carteira ou REDINHA) e, no `docs/06-interacoes-spec.md` (§4), o **modelo** de cada frase com as variações
  (ex.: obra crítica × estável; desvio positivo × negativo; sem justificativa).
- Um storytelling por painel de gráfico (15), cada um como componente (`Leitura · T1 · Obras por criticidade`, …),
  e **um** exemplo montado sobre a tela aberta (véu + painel), para mostrar a composição.
- **Guia da página** (o "?" do cabeçalho): como ler a tela — o que cada bloco mostra, a régua de criticidade, o que
  se pode clicar. Um por tela (`Guia · T1`…). Prioridade menor que os 15 storytellings; se o tempo apertar, faça o
  da Tela 01 e deixe a linguagem definida para os outros.

## 4. Entregue também a especificação

Escreva **`docs/06-interacoes-spec.md`** (no repositório) com, para cada verso, tooltip e leitura:
nome do componente e id · gatilho (hover em quê / clique em qual "?") · campos do JSON usados · texto-modelo com as
variações · estados. É o que o Opus usa para gerar as medidas DAX — sem ela o Power BI improvisa.

## Estrutura que o Power BI precisa (não é estilo)

- Nomeie os blocos de cada tela: `Cartão · <nome>` (cada KPI), `Painel · <nome>` (cada gráfico, com o título e o
  subtítulo dentro), `?` do painel como `Ajuda · <painel>`. A casca (fundo) do Power BI é exportada desses nomes.
- Tipografia no Power BI: Segoe UI no texto (Barlow só em número/HTML). **Rótulos operacionais a partir de 13 px e
  valores a partir de 14 px** no canvas 1920 (L033); 9–11 px só para conteúdo terciário (sobretítulo em versalete).
  Isso vale para as peças novas; se um rótulo das telas estiver abaixo disso e a correção for simples, corrija.
- Só a paleta do projeto (offwhite `#F7F4EE`, branco, creme `#E9E0CF`, grafite `#3B3B3F`, preto `#0B0B0C`, opacidades
  e misturas entre eles). Status sem cor: crítico preto sólido · atenção hachura · estável creme · mobilização
  tracejado.
- Números só do `mockup/data/criticidade-obras.json`, em pt-BR. Formatar pode, calcular não. Faltou campo → diga qual e
  para quê no retorno.

## Organização na página

Crie uma seção por tela abaixo das telas (`Interações · Tela 01`, …), com: a tela atualizada (instância) · os
versos · os tooltips (com estados) · as leituras · o guia · os exemplos montados. Nada sobreposto às telas atuais.
