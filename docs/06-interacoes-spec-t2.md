# Interações · especificação · Tela 02 · Análise crítica (fase 2)

Escrito pelo Fable 5.1 em 06/10/2026, seguindo a linguagem comum da §1 de `docs/06-interacoes-spec.md`, com as duas
correções do Alisson do mesmo dia: **a leitura do "?" cobre o retângulo do painel que explica, sem véu** (L065) e
**tooltips com bordas quadradas, gráfico de uma série e rodapé de uma linha**. Tudo o que está aqui existe no Figma,
arquivo `FjBWDk5odF9HaZ2pwhGosl`, página `03 · Mockup · Painel Criticidade de Obras` (`269:685`), seção
**`Interações · Tela 02`** (`303:2769`, x 0 · y 5900 · 10180 × 3240), nas quatro fileiras da §1.1:
`Fileira · Tela atualizada e exemplos` `303:2770` · `Fileira · Versos` `303:2773` · `Fileira · Tooltips` `303:2776` ·
`Fileira · Leituras e guia` `303:2779`. Instância da tela atualizada: `303:2782`.

Recorte do mockup: **obra em foco REDINHA (AT · ILUSTR.) · junho de 2026 · aba JUN26**. A tela é da obra escolhida no
filtro; no Power BI todos os textos mudam com a obra e o mês — o modelo de cada frase está nas tabelas. Números
**só** de `mockup/data/criticidade-obras.json` (`obras[REDINHA]`, salvo onde indicado). Formatação pt-BR. Tratamento = Power
Query.

**Animação (anotação para o Power BI, o Alisson implementa):** contador nos números e barras entrando em estilo
*racing* (crescem do zero em sequência); linha se desenhando da esquerda para a direita onde houver linha. Cada peça
abaixo tem uma linha "Animação" dizendo o que conta, o que corre e em que ordem. Nesta tela não há gráfico de linha:
nenhuma peça desenha linha.

---

## 0. Ajustes na Tela 02 (`281:721`) — piso tipográfico

75 nós, só nesta tela (a proposta usa instância e acompanha):

| Bloco | Nós | De → para |
|---|---|---|
| Sublinhas dos 5 cartões | `273:1104` `273:1110` `273:1116` `273:1122` `273:1128` | Segoe 12,5 → **13**; caixa 243 → 262 px (cabe sem quebrar) |
| Subtítulos dos painéis | `273:1131` `273:1218` `273:1232` `273:1256` `273:1295` | Segoe 12,5 → **13** |
| Bloco "entradas" do quadradinho (rótulos e valores) | `273:1133` … `273:1148` | Segoe 12,5 → **13** |
| Coluna "% do orçamento" do quadradinho | `273:1153` `1159` `1165` `1171` `1177` `1183` `1189` `1195` `1201` `1207` | Barlow Regular 13 → **14** |
| "+0,72%" do resultado do mês anterior | `273:1216` | Barlow Medium 13,5 → **14** |
| Cascata: rótulos dos degraus | `273:1237` `1241` `1246` `1251` `1254` | Segoe 11,5/15 → **13/17** |
| Cascata: valores dos degraus | `273:1236` `1240` `1245` `1250` `1253` | Barlow SemiBold 13 → **14** |
| Mês a mês: valores (preto e hachura) | `273:1261` `1267` `1273` `1279` `1285` `1291` · `273:1262` `1268` `1274` `1280` `1286` `1292` | Barlow 11,5 / 11 → **14** |
| Mês a mês: rótulos de mês | `273:1263` `1269` `1275` `1281` `1287` `1293` | Segoe 11,5 → **13** |
| Sinais: "faixa … · peso …" | `273:1302` `1310` `1319` `1328` `1337` | Segoe 11,5 → **13**; x 200 → 190 (192 e 200 nas duas linhas de valor mais largo, gap de 12 px); nas duas faixas em p.p. o "p.p." saiu do texto (`faixa < −3,0 · peso 25`, `faixa −0,5 a −0,2 · peso 10`) porque a unidade já está no valor ao lado e a linha estourava os 360 px do painel |
| Versaletes do desembolso | `273:1219` `1221` `1223` `1225` `1229` | Barlow Medium 9,5 → **10** (terciário) |

Não mexi: sidebar (`273:743` Segoe 12 é a mesma das cinco telas — mudar só aqui desalinharia), rodapé `273:1342` (11,
terciário), "?" dos painéis (Barlow 12,5, é a linguagem), números de item `01…10` (Barlow Medium 11, terciário), chips.

---

## 1. Versos · Tela 02 (`Fileira · Versos`)

Gatilho: hover (ou foco) no cartão. Texto fixo; régua lê `meta.regras_criticidade` / `meta.limites`. Copiados de
`Base · Verso` `291:1149` (creme, 301,6 × 120, margens 18/14; regra 2 linhas quando há régua).

| Componente · id | Cartão (id) | `COMO É CALCULADO` | `DE ONDE VEM` | Régua | Campos JSON |
|---|---|---|---|---|---|
| `Verso · T2 · Resultado da obra` `306:10617` | `289:737` | Crédito do executado + pago e não aplicado − gasto; o % divide pelo orçamento. | D155 e E155 da aba do mês | ■ < 0 · ▨ 0 a +1,0% · □ ≥ +1,0% | `ultimo.resultado`, `.resultado_pct`; régua `meta.regras_criticidade.resultado_pct` |
| `Verso · T2 · Mês anterior` `306:10630` | `289:738` | Resultado da aba anterior. A variação é o % de agora menos o % de lá, em p.p. | D156 e E156 da aba do mês | ■ < −0,5 · ▨ −0,5 a −0,2 · □ ≥ −0,2 p.p. | `ultimo.resultado_mes_anterior`, `.resultado_pct_mes_anterior`, `.indicadores.variacao_resultado_pp`; régua `…variacao_resultado_pp` |
| `Verso · T2 · Sem estoque e adiantamentos` `306:10643` | `289:739` | Resultado menos o pago e não aplicado: adiantamentos, estoque, equipamentos. | D155 − D146 a D150 da aba | ▨ < 0 atenção · □ ≥ 0 estável | `ultimo.resultado_sem_ativos`, `.ativos_nao_consumidos`; régua `…resultado_sem_ativos` |
| `Verso · T2 · Físico acumulado` `306:10654` | `289:740` | Executado acumulado da obra; o desvio é executado menos previsto, em p.p. | F37 e F35 da aba do mês | ■ < −3,0 · ▨ −3,0 a −1,0 · □ ≥ −1,0 p.p. | `ultimo.exec_acum`, `.prev_acum`, `.indicadores.desvio_fisico_pp`; régua `…desvio_fisico_pp` |
| `Verso · T2 · Criticidade` `306:10667` | `289:741` | Soma dos pontos dos cinco sinais: crítico vale o peso inteiro, atenção a metade. | Power Query · 5 sinais | ■ ≥ 50 · ▨ 25 a 49 · □ < 25 · ⬚ mobilização | `ultimo.score`, `.pontos_por_indicador`; régua `meta.limites` |

Decisões: o "Mês anterior" levou régua porque a marca do cartão (hachura) é o status da **variação** — sem a régua a
marca fica sem explicação. "De onde vem" do mês anterior aponta a célula da planilha (D156 = `<aba anterior>!D155`);
no Power BI o valor vem do D155 da aba anterior lido pelo Power Query, não da referência manual (ver `docs/02`,
padronização 3). No verso "sem estoque" o item *saldo de contrato* ficou de fora da lista por espaço (2 linhas); a
fórmula continua D155 − D146…D150. O cartão escuro vira para creme, como na T01.

**Animação (os cinco versos):** nenhum número conta — o verso só tem regra, origem e régua. A frente sobe e o verso
entra (~220 ms); as marcas da régua aparecem da esquerda para a direita (crítico → atenção → estável → mobilização),
60 ms entre elas.

---

## 2. Tooltips · Tela 02 (`Fileira · Tooltips`)

Anatomia revisada (vale para os dez): 480 de largura, **raio 0** no cartão e no cabeçalho preto (54 px), borda 1 px
preta, sombra (0, 8, 24, 18 %); corpo offwhite, margem 18. **Mini gráfico de uma série só**: coluna = 444 ÷ n (n = meses da janela, 1 a 12; §8), barra
40 × até 36 px, **sem eixo, sem grade, sem legenda**; rótulo de valor (Barlow SemiBold 14) **só no mês do ponto e no
extremo** que não coincide com ele; rótulo do mês em Segoe 13 (o do ponto em Semibold); barra do mês do ponto na cor
do status (ou preto, em série neutra), passado em preto 18 % (neutra) ou na cor do status do mês; série toda negativa
em módulo para cima; sinais mistos com positivas para cima e negativas para baixo; valor nulo some (mês a 35 %); zero
real mostra "0". **Rodapé = uma linha de até ~70 caracteres**, ou sai quando repete o que está acima. Sem chip e sem
selo no corpo; o selo da obra vai no sobretítulo (`· ILUSTR.` / `· REAL`).

### 2.1 `Tooltip · T2 · Item` (`310:3713`, 480 × **381**) — estados `· vazio` (`310:3755`, **190**) e `· fórmula` (`310:3766`, **274**)
**Gatilho:** hover numa linha 01–10 de "O quadradinho" (`289:742`). **Ponto:** o item da conta.

| Bloco | Modelo (item 05 · Estoque de materiais) | Variações | Campos |
|---|---|---|---|
| Sobretítulo | `O QUADRADINHO · {OBRA} · {MÊS} · ABA {aba}` | — | `obra`, `ultimo.mes`, `ultimo.aba` |
| Título · código · contexto | "Estoque de materiais" · `ITEM 05` · `SOMA · TABELA ANEXADA G78:J87` | sinal da linha (`SOMA` / `DESCONTA`); tabela anexada por item: 02 B64:E73 · 03 B78:E87 · 04 G64:J73 · 05 G78:J87 · 06 B92:E101 · 07 G92:J101 · 08 B106:E114 · 10 B119:E128; 01 `FÓRMULA F39 = F37 × J28`; 09 `RELATÓRIO CONFERIDO · F55` | `composicao[].item/.sinal`; mapa fixo de células (`docs/02`) |
| `O QUE É` (13/17, 2 linhas) | "Material comprado e ainda não aplicado, informado pelo almoxarifado; soma porque o dinheiro já saiu antes da medição." | texto fixo por item, resumo do "significado de cada item" da planilha (`docs/02`), em duas linhas: 01 "Quanto a obra podia ter gasto: orçamento projetado × executado acumulado. Não tem tabela anexada — é fórmula."; 02 "Desconto obtido num contrato, usado como artifício temporário (elevador e esquadrias); abatido conforme o serviço é medido."; 03 sinal pago de contrato ainda não medido; 04 material pago que ainda não chegou; 06 equipamento reaproveitável, a valor de mercado; 07 reformas pagas pelo cliente; 08 serviço medido e ainda sendo pago; 09 desembolso acumulado desde o início, conferido; 10 material de outra obra usado nesta | fixo (tabela de itens) |
| `LINHAS DA TABELA ANEXADA · VALOR` | 5 linhas: Aço CA-50/60 para lajes R$ 198.531,39 · Blocos cerâmicos R$ 107.663,78 · Material hidrossanitário R$ 183.485,20 · Revestimento cerâmico (compra antecipada) R$ 164.893,28 · Material elétrico (fios e cabos) R$ 156.922,91 | **vazio**: "Nenhuma linha este mês: o item está em zero e não entra na conta." em itálico (Saldo de contrato); **fórmula**: bloco some (Crédito, Desembolsado, Dívida sem tabela) | `itens_ultimo_mes[grupo = item].descricao/.valor` |
| `{ITEM}, MÊS A MÊS` | 6 barras (365 · 590 · 560 · 775 · 752 · 811 mil), passado em preto 18 %, junho em preto; rótulos só em **jan (R$ 365 mil, mínimo)** e **jun (R$ 811 mil, mês do ponto)** | `· fórmula`: crédito 2,71 → 5,44 mi, rótulos jan e jun; mês sem aba: rótulo a 35 % sem barra; **vazio**: bloco some (não há série do item) | `serie[].estoque`, `serie[].credito`, `serie[].contas_pagar`, `serie[].desembolsado_acum` |
| Rodapé (1 linha) | — (sai: o tooltip já mostra tudo) | `· fórmula`: "No mês: 2,30% executado × 3,33% previsto."; `· vazio`: sem rodapé | `ultimo.exec_mes/.prev_mes` |

**Animação:** os cinco valores das linhas contam de zero, de cima para baixo (80 ms de defasagem); as barras correm
jan → jun; os dois rótulos (jan, jun) contam junto com a própria barra. `· fórmula`: barras jan → jun, rótulos jan/jun e
os 2,30 % / 3,33 % do rodapé contam. `· vazio`: nada conta; o itálico entra com fade.

### 2.2 `Tooltip · T2 · Degrau` (`310:3797`, 480 × **368**) — estado `· vazio` (`310:3918`, **368**)
**Gatilho:** hover num degrau de "Como o resultado se forma" (`289:747`). **Ponto:** o degrau (crédito · pago e não
aplicado · contas a pagar · desembolsado · resultado).

| Bloco | Modelo (degrau 2 · Pago e não aplicado · REDINHA jun/26) | Variações | Campos |
|---|---|---|---|
| Cabeçalho | `COMO O RESULTADO SE FORMA · REDINHA · JUN/26` · "Pago e não aplicado" · `DEGRAU 2 DE 4` · `SOMA · 3,60% DO ORÇAMENTO` | `DESCONTA` nos degraus 3 e 4; `DEGRAU n DE m` conta os degraus com valor (a dívida, item 10, vira 5.º degrau quando ≠ 0); mobilização: `· EM MOBILIZAÇÃO` no sobretítulo | `composicao[].sinal/.pct_orcamento`, `ultimo.mobilizacao` |
| `ITENS DO QUADRADINHO QUE FORMAM O DEGRAU · VALOR` | 02 Saldo de contrato R$ 0,00 · 03 Adiant. de serviços não medidos R$ 0,00 · 04 Adiant. de materiais não estocados R$ 0,00 · **05 Estoque de materiais R$ 811.496,56** · 06 Equipamentos R$ 0,00 · 07 Receita de personalizações R$ 0,00 (zeros a 42 %) | degrau de um item só (crédito, contas a pagar, desembolsado): uma linha; **vazio** (TIROL mar/26): os seis em zero | `composicao[]` (itens 02–07 = ativos não consumidos + receita) |
| `PAGO E NÃO APLICADO, MÊS A MÊS` | 365 · 590 · 560 · 815 · 752 · 811 mil; rótulos só em **abr (R$ 815 mil, máximo)** e **jun (R$ 811 mil)** | série do degrau: crédito `serie[].credito`, contas `serie[].contas_pagar`, desembolsado `serie[].desembolsado_acum`; **vazio**: jan/fev sem aba a 35 %, mar "0" (mês do ponto, tracejado de mobilização), abr 39 · mai 44 (rótulo R$ 44 mil, máximo) · jun 37 | `serie[].ativos_nao_consumidos` (abr = 815, não 775 do estoque: havia outro ativo) |
| Rodapé (1 linha) | "Sem este degrau, o resultado de junho seria −R$ 721 mil." | crédito: "Único degrau que cresce com o físico: {exec_acum} × orçamento."; contas a pagar: "Serviço medido e ainda em pagamento; sai antes do desembolso."; desembolsado: "Acumulado desde o início, conferido; o maior degrau da conta."; **vazio**: "Nada lançado em março: o degrau não aparece; resultado −R$ 63 mil." | `ultimo.resultado_sem_ativos`; TIROL `serie[0].resultado` |

**Animação:** o único valor ≠ 0 da lista (R$ 811.496,56) conta; zeros não. Barras correm jan → jun; rótulos abr e jun
contam com a barra; o −R$ 721 mil do rodapé conta por último. `· vazio`: barras abr → jun correm (mar fica no "0");
−R$ 63 mil conta.

### 2.3 `Tooltip · T2 · Mês` (`319:7602`, 480 × **321**) — estado `· primeiro mês` (`319:7634`, **269**)
**Gatilho:** hover numa coluna (preta ou hachurada) de "Resultado da obra, mês a mês" (`289:751`). **Ponto:** o mês.
Não repete o resultado nem o resultado sem estoque (estão no gráfico). Sem gráfico.

| Bloco | Modelo (junho) | Variações | Campos |
|---|---|---|---|
| Cabeçalho | `RESULTADO DA OBRA, MÊS A MÊS · REDINHA · ILUSTR.` · "junho de 2026" · `ABA JUN26` · `EXECUTADO 24,1% × PREVISTO 28,0%` | `REAL` para CAJUEIRO; primeiro mês: `MÊS A MÊS · {OBRA} · {SELO} · PRIMEIRO MÊS DO HISTÓRICO` | `serie[m].aba/.exec_acum/.prev_acum`, `fonte` |
| `COMO O RESULTADO SE FORMOU` | + Crédito do orçamento R$ 5,44 mi · *orçamento × executado* / + Pago e não aplicado R$ 811 mil · *só estoque de materiais* / − Contas a pagar R$ 93 mil · *medido e ainda não pago* / − Desembolsado R$ 6,06 mi · *acumulado desde o início* | detalhe do "pago e não aplicado" lista os grupos com valor ("estoque e adiantamentos", "nenhum" quando zero — zero real aparece "R$ 0"); janeiro: 2,71 mi · 365 mil · 115 mil · 2,74 mi | `serie[m].credito/.ativos_nao_consumidos/.contas_pagar/.desembolsado_acum` |
| `DESDE {MÊS ANTERIOR}` (1 linha) | "Resultado de +0,72% para +0,40% (−0,32 p.p.); o estoque era R$ 752 mil." | `Resultado de {pct m−1} para {pct m} ({variação} p.p.); o estoque era {estoque m−1}.`; **primeiro mês: bloco some** | `serie[m−1].resultado_pct/.estoque`, `serie[m].indicadores.variacao_resultado_pp` |
| `DESEMBOLSO DO MÊS` | ■ R$ 638 mil × R$ 469 mil previsto · **+36%** | marca = status do desvio no mês (jan ▨ +18%) | `serie[m].desembolsado_mes_rs/.previsto_mes_rs/.indicadores.desvio_desembolso/.indicadores_status` |
| Rodapé (1 linha) | "Justificativa: aditivo de serviço não previsto (contenção)." | "Justificativa: {texto da planilha, truncado em uma linha}"; em branco e exigida: "Justificativa exigida e não preenchida."; não exigida: sem rodapé | `serie[m].justificativa`, `justificativa_exigida` |

**Animação:** os quatro valores da conta contam na ordem da conta (crédito → pago e não aplicado → contas a pagar →
desembolsado, 120 ms entre eles); depois contam os números do "desde maio" e o +36 %. Sem barras.
`· primeiro mês`: idem sem o bloco "desde".

### 2.4 `Tooltip · T2 · Indicador` (`312:3931`, 480 × **255**) — estados `· parcial` (`319:7664`, **275**) e `· estável` (`312:4005`, **255**)
**Gatilho:** hover numa linha de "Sinais do mês" (`289:755`). **Ponto:** o indicador. Não repete valor, chip nem
"faixa · peso" da linha; traz a faixa inteira, os pontos e a série.

| Bloco | Modelo (Desvio físico acumulado · REDINHA) | Variações | Campos |
|---|---|---|---|
| Cabeçalho | `SINAIS DO MÊS · REDINHA · JUN/26` · "Desvio físico acumulado" · `25 DE 25 PONTOS · PESO 25` | `{pontos} DE {peso} PONTOS · PESO {peso}`; `· parcial`: sobretítulo + `· JANEIRO SEM MÊS ANTERIOR`; `· estável` (DUNAS): `0 DE 35 PONTOS` | `ultimo.pontos_por_indicador[ind]`, `meta.regras_criticidade[ind].peso` |
| Faixa | ■ < −3,0 p.p. crítico · ▨ −3,0 a −1,0 atenção · □ ≥ −1,0 estável | texto das três faixas de `meta`; sem estoque: `▨ < 0 atenção · □ ≥ 0 estável · nunca crítico sozinho` | `meta.regras_criticidade[ind].{critico,atencao,estavel}` |
| `{INDICADOR}, MÊS A MÊS` | barras −0,6 · −0,7 · −1,4 · −1,8 · −2,9 · −3,9 p.p. na cor do status (creme · creme · hachura · hachura · hachura · preto), em módulo para cima; rótulos só em **jan (−0,6, extremo)** e **jun (−3,9, mês do ponto)** | sinais mistos (`· parcial`, variação —/−0,09/+0,02/−0,19/−0,03/−0,32): positivas para cima, negativas para baixo; rótulos em **mar (+0,02, máximo)** e **jun (−0,32)**; **valor nulo** (jan) → sem barra, mês a 35 %; `· estável`: +1,80 … +2,30 %, todas creme, rótulos jan e jun | `serie[].indicadores[ind]`, `serie[].indicadores_status[ind]` |
| `DESDE {MÊS ANTERIOR}` (rodapé, 1 linha) | "Era atenção em maio (−2,9 p.p.); o atraso cresce todo mês." | `Era {status m−1} em {mês} ({valor m−1}); {tendência}.` / `Segue em {status}: era {valor} em {mês}.`; **estável em todos os meses da janela**: "Nada mudou: estável nos {n} meses; em maio, R$ 587 mil."; **parcial**: "Entrou em atenção: maior queda do período; janeiro sem mês anterior."; tendência ("cresce todo mês", "sobe desde janeiro", "maior queda") = comparação da série | `ultimo.mudancas_desde_mes_anterior`, `serie[m−1].indicadores`, DUNAS `ultimo.resultado_mes_anterior` |

**Animação:** "25 DE 25 PONTOS" conta; barras correm jan → jun na ordem dos meses (jan ausente na `· parcial`: começa
em fev); rótulos jan/jun (ou mar/jun) contam com a barra; o número do rodapé conta por último.

---

## 3. Leituras · Tela 02 (`Fileira · Leituras e guia`) — L065: cobrem o painel, sem véu

Cada leitura é um cartão offwhite com **a geometria exata do contêiner do painel** (canvas 1920 × 1080), **canto
reto**, contorno 1 px preto e sombra (0, 10, 30, 22 %); margem interna 20; sobretítulo Barlow Medium 10 em (20, 16);
**× fixo no canto superior direito** (28 px, contorno 30 %, em x = w − 36 · y 8 — no Power BI, botão transparente
nessa posição; clicar fora também fecha); **sem pílula "Fechar"**. O resto da tela segue visível. Tipos: achado Barlow
SemiBold **22/26** (painel grande) ou **20/24** (pequeno); explicação Segoe 13,5/18 ou 13/17 grafite; destaques em
faixa creme (número Barlow SemiBold 21/20 + rótulo 13/16); "o que explica" e "como ler" 13/17. Piso 13 px. Regra
L058 conferida em cada leitura: nenhum número aparece duas vezes (os da régua moram só em `COMO LER`).

| Leitura · id | Painel · "?" | Geometria (x · y · w × h) | O que entrou | O que saiu / foi condensado |
|---|---|---|---|---|
| `Leitura · T2 · O quadradinho` `316:11890` | `289:742` · `289:743` | **352 · 282 · 593 × 562** (grande) | completa, em duas colunas abaixo dos destaques: esquerda (300 px) `O QUE EXPLICA` + `COMO LER`; direita (233 px) `DETALHE` com as barras do estoque | explicação de 5 para 4 linhas; "o que explica" e "como ler" encurtados (3 e 4 linhas na coluna); sem pílula |
| `Leitura · T2 · Como o resultado se forma` `316:11925` | `289:747` · `289:748` | **980 · 282 · 515 × 358** (pequeno) | achado · explicação (2 linhas) · destaques · `O QUE EXPLICA` (3 linhas) | saíram `DETALHE` (pares crédito × desembolsado) e `COMO LER` |
| `Leitura · T2 · Resultado da obra, mês a mês` `316:11966` | `289:751` · `289:752` | **980 · 640 · 515 × 376** (pequeno) | achado · explicação (2 linhas) · destaques · `O QUE EXPLICA` (2 linhas) · `COMO LER` (2 linhas) | saiu `DETALHE` (tabela desembolso × previsto, mês a mês — o conteúdo está no tooltip de mês); "o que explica" de 4 para 2 linhas |
| `Leitura · T2 · Sinais do mês` `316:12026` | `289:755` · `289:756` | **1500 · 282 · 361 × 436** (pequeno e estreito) | achado (encurtado) · explicação (2 linhas) · destaques com rótulos curtos · `DETALHE` = matriz 5 sinais × n meses da janela + linha "Obra" | saíram `O QUE EXPLICA` e `COMO LER`; sobretítulo com `JUN/26` em vez de "junho de 2026" (cabe antes do ×) |

### 3.1 `Leitura · T2 · O quadradinho` (`316:11890`, 593 × 562)
| Bloco | Texto | Modelo e variações | Campos |
|---|---|---|---|
| Sobretítulo | `LEITURA · O QUADRADINHO · REDINHA · JUNHO DE 2026` | obra e mês por extenso | `obra`, `ultimo.mes` |
| Achado (22/26) | "O resultado de junho, R$ 90 mil, é menor que o estoque que o sustenta: R$ 811 mil comprados e ainda não aplicados." | `resultado_sem_ativos < 0`: "O resultado de {mês}, {resultado}, é menor que o estoque que o sustenta: {ativos} comprados e ainda não aplicados." · `≥ 0` (DUNAS, PONTA NEGRA): "O resultado de {mês}, {resultado}, fica positivo mesmo sem os {ativos} pagos e ainda não aplicados." · resultado negativo (POTENGI, TIROL): "A obra fecha {mês} com {resultado} de prejuízo, e isso já contando {ativos} em estoque e adiantamentos." | `ultimo.resultado/.ativos_nao_consumidos/.resultado_sem_ativos` |
| Explicação (13,5/18) | "A conta começa pelo crédito do que foi executado e soma o que foi pago mas ainda não virou obra; depois desconta as medições a pagar e tudo o que a obra desembolsou. Em junho, dos sete itens que somam, só dois têm valor — e um deles é o estoque. Sem ele, a obra fecharia o mês no vermelho." | 1.ª frase fixa; 2.ª: contagem em palavras dos itens 01–07 com valor ≠ 0; 3.ª: "Sem ele(s), a obra fecharia o mês no vermelho" se `resultado_sem_ativos < 0`, senão "Mesmo sem eles o resultado seguiria positivo" | `composicao[].valor`, `ultimo.resultado_sem_ativos` |
| Destaques | `R$ 5,44 mi` crédito pelos 24,1% executados: o que a obra podia ter gasto · `R$ 6,06 mi` já desembolsados desde o início, 26,9% do orçamento · `−R$ 721 mil` resultado sem estoque e adiantamentos: o consumo real | 1: `credito` + `exec_acum`; 2: `composicao[desembolsado].valor` + `.pct_orcamento`; 3: `resultado_sem_ativos` | `ultimo.credito/.exec_acum`, `composicao[]`, `ultimo.resultado_sem_ativos` |
| O que explica (coluna esq.) | "Saldo de contrato e adiantamentos nunca entraram na conta desta obra; equipamentos e receita de personalizações estão em zero. O resultado vive de três números — crédito, estoque e desembolso — e o estoque subiu em três dos cinco meses do período." | lista dos itens em zero e dos com valor (em palavras); "subiu em {n} dos {m} meses" = comparação mês a mês de `serie[].estoque` | `composicao[]`, `serie[].estoque` |
| Detalhe (coluna dir.) | barras do estoque jan–jun **sem rótulo de valor** (passado preto 18 %, junho preto); legenda "estoque de materiais, mês a mês · R$ 365 mil em janeiro; a barra preta é junho" | primeiro valor da série como âncora; mês sem aba sem barra | `serie[].estoque` |
| Como ler (coluna esq.) | "Os dez itens seguem a ordem do bloco A132:J157: os sete primeiros somam, contas a pagar e desembolso descontam, a dívida soma de volta. O mouse num item mostra o que ele é e as linhas anexadas." | fixo (abas NOV24–JAN26 têm o bloco em A133:J158) | — |

**Animação:** R$ 90 mil e R$ 811 mil do achado contam; os três destaques contam em sequência (esquerda → direita,
150 ms); as barras do detalhe correm jan → jun. Sem linha.

### 3.2 `Leitura · T2 · Como o resultado se forma` (`316:11925`, 515 × 358)
| Bloco | Texto | Modelo e variações | Campos |
|---|---|---|---|
| Achado (20/24) | "A obra já desembolsou R$ 6,06 mi contra um crédito de R$ 5,44 mi pelo executado; só o estoque segura o resultado no positivo." | `desembolsado > credito`: "A obra já desembolsou {desembolsado} contra um crédito de {crédito} pelo executado; {só o estoque segura o resultado no positivo / e nem o estoque cobre a diferença}" · `≤` (DUNAS): "A obra desembolsou {desembolsado} e tem crédito de {crédito}: o resultado é positivo antes mesmo do estoque." | `composicao[desembolsado]`, `ultimo.credito`, `.resultado` |
| Explicação (13/17, 2 linhas) | "O desembolso corre à frente do físico: a obra gastou mais de um quarto do orçamento e executou menos de um quarto; a diferença é coberta pelo estoque." | frações em palavras de `pct_orcamento` do desembolsado × `exec_acum`; "corre à frente" / "anda junto" / "fica atrás" | `composicao[desembolsado].pct_orcamento`, `ultimo.exec_acum` |
| Destaques | `26,9%` do orçamento já desembolsado desde o início · `24,1%` executado: a base do crédito do orçamento · `R$ 93 mil` de medições a pagar, descontadas antes do resultado | 1: `pct_orcamento` do desembolsado; 2: `exec_acum`; 3: `composicao[contas a pagar].valor` | `composicao[]`, `ultimo.exec_acum` |
| O que explica (3 linhas) | "Crédito e desembolso crescem todo mês, mas o desembolso cresce mais rápido — a distância entre os dois aumenta desde março. O que decide o resultado é o estoque: a parcela ainda não testada pela medição." | "crescem todo mês" = séries monotônicas; "aumenta desde {mês}" = diferença desembolsado − crédito crescente; obra estável: "o desembolso anda junto do crédito" | `serie[].credito/.desembolsado_acum` |
| Fora (não coube) | `DETALHE` (pares crédito × desembolsado por mês; legenda "em janeiro, R$ 2,71 mi × R$ 2,74 mi") e `COMO LER` ("Cada degrau soma ou desconta do anterior…; degrau cheio soma, hachurado desconta; o mouse num degrau mostra seus itens") | ficam disponíveis no tooltip de degrau e no guia | — |

**Animação:** R$ 6,06 mi e R$ 5,44 mi do achado contam (desembolsado primeiro); os três destaques contam em sequência.
Sem barras, sem linha.

### 3.3 `Leitura · T2 · Resultado da obra, mês a mês` (`316:11966`, 515 × 376)
| Bloco | Texto | Modelo e variações | Campos |
|---|---|---|---|
| Sobretítulo | `LEITURA · RESULTADO DA OBRA, MÊS A MÊS · REDINHA · JAN–JUN/26` | primeiro e último mês da série da obra (TIROL: MAR–JUN/26) | `serie[0/−1].mes` |
| Achado (20/24) | "O resultado caiu em quatro dos cinco meses: de R$ 222 mil em janeiro a R$ 90 mil em junho." | `O resultado {caiu/subiu} em {n} dos {m} meses: de {R$ 1.º} em {mês} a {R$ último} em {mês}.`; série de 1 mês: "Primeiro mês no histórico: resultado de {R$}." | `serie[].resultado` |
| Explicação (2 linhas) | "A barra preta desce enquanto a hachura — o resultado sem estoque e adiantamentos — afunda mais: negativa nos {n} meses, piorou em três deles." | "negativa nos {m} meses" / "negativa desde {mês}" / "positiva em todos"; "piorou em {n} deles" = quedas de `resultado_sem_ativos` | `serie[].resultado_sem_ativos` |
| Destaques | `−0,32 p.p.` variação do resultado em junho, a maior queda do período · `+1,00%` resultado de janeiro sobre o orçamento; em junho, +0,40% · `R$ 811 mil` em estoque em junho; eram R$ 365 mil em janeiro | 1: variação do mês + "a maior queda / alta do período" se extremo; 2: `resultado_pct` do 1.º mês × do mês; 3: `estoque` do mês × do 1.º mês | `serie[].indicadores.variacao_resultado_pp/.resultado_pct/.estoque` |
| O que explica (2 linhas) | "O que separa as barras é o estoque de cada mês; como a obra seguiu comprando à frente da aplicação, a distância cresceu de janeiro a junho." | "cresceu / diminuiu de {1.º mês} a {mês}" por `ativos` do primeiro × último | `serie[].ativos_nao_consumidos` |
| Como ler (2 linhas) | "Preto: resultado mensal (linha 155). Hachura: o mesmo sem estoque, adiantamentos e saldo de contrato. Passe o mouse num mês para ver a conta." | fixo | — |
| Fora (não coube) | `DETALHE` (tabela desembolso × previsto por mês com marca do desvio e justificativa: jan ▨ +18% · fev ▨ +16% · mar ▨ +23% · abr ■ +26% · mai ■ +27% · jun ■ +36%) | o tooltip de mês traz o desembolso do mês com justificativa | `serie[].desembolsado_mes_rs/.previsto_mes_rs/.indicadores.desvio_desembolso` |

**Animação:** R$ 222 mil e R$ 90 mil do achado contam (janeiro primeiro); os três destaques contam em sequência. Sem
barras, sem linha.

### 3.4 `Leitura · T2 · Sinais do mês` (`316:12026`, 361 × 436)
| Bloco | Texto | Modelo e variações | Campos |
|---|---|---|---|
| Sobretítulo | `LEITURA · SINAIS DO MÊS · REDINHA · JUN/26` | — | — |
| Achado (20/24) | "Dois sinais de ritmo em crítico levam a REDINHA a 72,5 pontos: físico −3,9 p.p. e desembolso +36%." | `{n} sinal(is) {de ritmo / de resultado} em crítico levam a {OBRA} a {score} pontos: {sinal 1 com valor} e {sinal 2 com valor}.`; sem crítico (JANGADA, CAJUEIRO): "Nenhum sinal crítico, mas {n} em atenção levam a {OBRA} a {score} pontos: …"; estável (DUNAS): "{OBRA} está estável: cinco sinais na faixa e {score} pontos."; mobilização (TIROL): "{OBRA} em mobilização: pela régua somaria {score_bruto}, mas fica em {score} até passar de 10% executado." | `ultimo.sinais`, `.score`, `.score_bruto`, `.mobilizacao` |
| Explicação (2 linhas) | "Nenhum sinal está estável; o físico virou crítico e a variação do resultado entrou em atenção." | 1.ª oração: contagem em palavras dos estáveis; depois uma oração por item de `mudancas_desde_mes_anterior` (`virou {para}` / `entrou em {para}` / `voltou a {para}`); sem mudança: "nenhum sinal mudou de faixa desde {mês}" | `ultimo.indicadores_status`, `.mudancas_desde_mes_anterior` |
| Destaques | `−2,9 p.p.` desvio físico em maio · `+0,72%` resultado de maio · `2` sinais mudaram desde maio | 1: valor no mês anterior do sinal que mais mudou; 2: `resultado_pct_mes_anterior`; 3: contagem de `mudancas_desde_mes_anterior` (0 → "nenhum mudou") | `serie[m−1].indicadores`, `ultimo.resultado_pct_mes_anterior`, `.mudancas_desde_mes_anterior` |
| Detalhe | matriz 5 sinais × n meses (janela) só com marcas (creme · hachura · preto), rótulos curtos (Desvio físico · Desembolso × previsto · Resultado da obra · Variação no mês · Sem estoque) e a linha "Obra" (estável · atenção · atenção · crítico · crítico · crítico) | mês sem aba: célula vazia; mobilização: marca tracejada na linha "Obra" | `serie[].indicadores_status`, `serie[].status/.mobilizacao` |
| Fora (não coube) | `O QUE EXPLICA` ("O resultado da obra é o sinal de maior peso, mas está em atenção; são os dois sinais de ritmo que empurram a obra para o crítico…") e `COMO LER` (a régua: pesos 35/25/20/10/10, crítico = peso inteiro, atenção = metade, 0–100, crítico de 50, atenção 25–49) | a régua está no guia da página e no tooltip de sinal | `meta` |

**Animação:** 72,5, −3,9 p.p. e +36 % do achado contam; os três destaques contam em sequência; as marcas da matriz
aparecem coluna a coluna (jan → jun, 100 ms), a linha "Obra" por último. Sem barras, sem linha.

---

## 4. `Guia · T2` (`319:7536`, 760 × 921) — "?" `273:1071` (`Ajuda · Guia da página`)
Único painel que **cobre a tela inteira**, com véu 55 % e marcadores numerados; painel em x 400 (y = 12 + (1056 −
921) / 2 = 80), raio 20 (ficou como estava). Texto fixo (muda só obra e mês): sobretítulo `GUIA DA PÁGINA · FOLHA 02 ·
ANÁLISE CRÍTICA`; título "Como ler esta tela"; introdução "Os cartões dizem como a obra fechou o mês; o quadradinho
reproduz a conta da planilha; os painéis da direita mostram de onde vem o resultado, como ele mudou e quais sinais
pesam."
1. **Cartões da obra** — Cinco números do mês; o escuro é o resultado da obra, a resposta da pergunta. Passe o mouse: o cartão vira e mostra como é calculado e de onde vem.
2. **O quadradinho** — Os dez itens do bloco de resultado da planilha, na ordem da conta, com valor e fração do orçamento. Passe o mouse num item para ver o que ele significa e as linhas da tabela anexada que o compõem.
3. **Desembolso do mês** — Previsto × desembolsado no mês, a diferença e o desvio, com a justificativa exigida acima de ±10%.
4. **Como o resultado se forma** — Os degraus da conta: crédito pelo executado, mais o pago e não aplicado, menos contas a pagar, menos desembolsado. Passe o mouse num degrau para ver os itens que o compõem.
5. **Resultado da obra, mês a mês** — Resultado oficial (preto) e sem estoque e adiantamentos (hachura) mês a mês. Passe o mouse num mês para ver como o resultado se formou e o que mudou.
6. **Sinais do mês** — Os cinco indicadores da régua com status, valor, faixa e peso. Passe o mouse num sinal para ver a faixa completa e a trajetória do período.
7. **Com e sem estoque** — A síntese escrita da obra no mês; muda com a obra e o mês escolhidos.
8. **Filtro e ajuda** — O topo mostra a obra e o mês em uso. O funil abre os filtros; o "?" redondo abre este guia; o "?" de cada painel abre a leitura daquele gráfico.
9. **Navegação** — Visão geral · Análise crítica · Avanço físico · Resultado no tempo. A obra e o mês escolhidos valem para todas as folhas.
Régua: ■ crítico · 50 pontos ou mais ▨ atenção · 25 a 49 □ estável · abaixo de 25 ⬚ mobilização · menos de 10%
executado: a obra fica, no máximo, em atenção.
Marcadores (canvas 1920): 1 (338, 130) cartões · 2 (338, 278) quadradinho · 3 (338, 844) desembolso · 4 (1436, 278)
como se forma · 5 (1436, 636) mês a mês · 6 (1800, 278) sinais · 7 (1498, 720) com e sem estoque · 8 (1412, 44)
filtro/ajuda · 9 (14, 218) navegação. Os marcadores 4, 5 e 6 ficam à esquerda do "?" do próprio painel porque o guia
cobre o canto esquerdo da coluna do meio.

**Animação:** os marcadores aparecem em sequência 1 → 9 (80 ms); nenhum número conta.

---

## 5. Exemplos montados (fileira 1)
`Exemplo · T2 · Cartão virando` `318:5182` (frame `flip · meio do gesto` `318:5520` sobre o cartão escuro: clone da
frente `318:5521` em −66 px, instância do verso `318:5529` em +54 px, dobra, cursor) · `Exemplo · T2 · Tooltip
apontando` `318:5546` (cursor na linha 05 "Estoque de materiais"; `Tooltip · T2 · Item` em cursor + 16 px, x 576 ·
y 590, fecha em y 971) · `Exemplo · T2 · Leitura aberta` `318:5929` (**sem véu**: `Leitura · T2 · O quadradinho` em
352 · 282, exatamente sobre o painel; o resto da tela visível) · `Exemplo · T2 · Guia aberto` `320:7536` (véu + 9
marcadores + `Guia · T2` em 400 · 80).

---

## 6. Números: origem e o que falta no JSON

**Conferidos** contra `obras[REDINHA]`: `ultimo.*` (90.212,41 · +0,40 % · 160.727,67 · +0,72 % · 811.496,56 ·
−721.284,15 · 5.435.297,10 · 24,1/28,0 % · 2,30/3,33 % · 638.070,92/469.169,80 · +36 % · −3,9 p.p. · −0,3151 → "−0,32"
· 72,5 · pontos 25/20/17,5/5/5 · mudanças físico e variação); `composicao[]` (26,88 % → "26,9 %", 3,60 %);
`itens_ultimo_mes` (5 linhas de estoque); `serie[]` (estoque 365/590/560/775/752/811 mil; ativos abr 815 mil; crédito
2,71 → 5,44 mi; desembolsado acumulado 2,74 → 6,06 mi; contas 115/93 mil; resultado 222 → 90 mil e +1,00 % → +0,40 %;
sem ativos −143 … −721; desembolso do mês 298×252 (+18 %) e 638×469 (+36 %); desvio físico −0,6 … −3,9; variação
—/−0,09/+0,02/−0,19/−0,03/−0,32; exec/prev jan 12,2/12,8 e mai 21,8/24,7; estoque maio 752 mil; status por sinal e por
mês; justificativas); `obras[TIROL].serie[0]` (mar/26: resultado −62.584 → "−R$ 63 mil", ativos 0; abr/mai/jun
39/44/37 mil); `obras[DUNAS]` (resultado_pct +1,80 … +2,30 %, maio R$ 587 mil, 0 pontos); `meta.regras_criticidade` e
`meta.limites`. Contagens em palavras ("quatro dos cinco meses", "três dos cinco", "piorou em três", "sete itens que
somam, só dois têm valor", "dois sinais mudaram") saem dessas séries.

**Derivados (comparações de sinal, não contas — convém campo `tendencia` para a DAX não varrer a série):** "cresce
todo mês" (desvio físico), "subiu em três dos cinco meses" (estoque), "caiu em quatro dos cinco meses" (resultado),
"piorou em três deles" (sem ativos), "a distância aumenta desde março" (desembolsado − crédito), "a maior queda do
período" (variação mínima), "sobe desde janeiro" (DUNAS), "cresceu de janeiro a junho" (ativos).

**Faltam no JSON (acrescentar em `montar_dados_mockup.py`):**
- `serie[].itens[]` (linhas das tabelas anexadas por mês) — o tooltip de item só tem `itens_ultimo_mes`; em outro
  mês do filtro a lista ficaria vazia.
- `serie[].composicao[]` (os 10 itens por mês) — hoje só há `estoque`, `ativos_nao_consumidos`, `contas_pagar`,
  `credito`, `desembolsado_acum`; os itens 02/03/04/06/07/10 não têm série (o tooltip `· vazio` do item omite o
  bloco "mês a mês" por isso).
- `degraus[]` por obra/mês: `{nome, sinal, valor, pct_orcamento, itens[]}` — o "3,60 % do orçamento" do degrau é o
  `pct_orcamento` do estoque porque os outros cinco itens estão em zero; no caso geral é a soma dos itens 02–07.
  Também evita a DAX decidir quando a dívida (item 10) vira 5.º degrau.
- `justificativa_ausente` por mês da série (hoje só no último) para o rodapé do tooltip de mês.
- `score_bruto` dos meses em mobilização na linha "Obra" da matriz (usei só `status`).

**Não calculei:** somas de pontos ("45 dos 72,5"), razões ("nove vezes o resultado", "mais que dobrou") e cenários
("se o físico voltasse a atenção a obra ficaria em 60") — ficaram fora dos textos por serem contas.

---

## 7. O que fica diferente no Power BI
- Igual à §8 da spec da T01 (flip por hover/foco; tooltip de página 480 × 420 ancorado pelo Power BI; textos =
  medidas DAX com as variações das §2–3), com a mudança da L065: **a leitura é um marcador de exibição que liga só o
  cartão HTML do tamanho do painel** (sem véu); o "?" do painel e o × do cartão são botões com ação de marcador; o ×
  é um botão transparente no canto superior direito do cartão e o clique fora (botão transparente do tamanho da
  página, atrás do cartão) também volta ao estado normal. O guia continua com véu na página inteira.
- Os quatro tooltips da T02 têm a **obra do filtro** no sobretítulo; o de item e o de degrau lêem a linha/degrau
  sob o mouse (campo `item` / `degrau` da tabela de composição), o de mês lê `mes`, o de sinal lê `indicador`.
- Mini gráficos dos tooltips: uma série, sem eixo; rótulo só no mês do ponto e no extremo (medida DAX que devolve
  `BLANK()` nos outros meses); cores pelo status; série toda negativa em módulo; valor nulo some; zero real "0".
- Animação (contador nos números, barras em *racing*, marcas da matriz coluna a coluna) é implementação do Alisson
  no HTML Content; a ordem de cada peça está nas linhas "Animação".
- A matriz da leitura "Sinais do mês" é uma tabela de 5 × n marcas (n = meses da janela): HTML Content com uma célula por
  `indicador × mês` lendo `indicadores_status`.
- Justificativas longas nos tooltips de mês: truncar com reticências em uma linha (o mockup abreviou "aditivo de
  serviço não previsto (contenção)").
- "Faixa · peso" dos sinais no painel: o "p.p." saiu das duas linhas em p.p. (unidade já no valor); manter assim no
  HTML da tela para caber nos 361 px da coluna.

---

## 8. Janela de até 12 meses (06/10/2026, Opus 5.5)

Decisão do Alisson: as séries mês a mês têm **janela de 1 a 12 meses**, escolhida no drawer (`dJanela`: 12, 9, 6 ou
3; padrão 12), sempre terminando no mês de referência e nunca antes de jan/26 (`[Série · primeiro mês]`). Com os
dados reais (ago/26, janela 12) a REDINHA mostra 8 meses — o painel desenhado para 6 cortava a ponta e encavalava os
rótulos. Figma: seção `Interações · Tela 02` › `Fileira · Leituras e guia` › **`Janela · T2 · séries de 1 a 12 meses`
(`350:15701`)** — painéis de 12 (ilustrativo), 8, 6, 3 e 8 com meses sem aba, a cascata com resultado negativo e a
**nota com as regras (`350:16889`)**; `Fileira · Tooltips` › **`Janela · T2 · série dos tooltips (1 a 12 meses)`
(`350:16265`)**. A Casca · T2 não cita semestre: não precisou de reexportação.

**Painel "Resultado da obra, mês a mês"** (área 480 × 296; `T2 · Mês a mês · HTML coluna`)
- Eixo da janela: n = `[Série · meses até a referência]`, x = `[Série · posição na janela]`; o mesmo eixo para todas as
  obras — mês da janela sem aba fica com o rótulo a 35 %, sem barra (TIROL com janela 12: jan–mai apagados).
- Coluna = 480 ÷ n (entradas `flex: 1 1 0`). Par no centro da coluna: barra = mín(26, (coluna − 12) ÷ 2), 4 px entre a
  preta e a hachura; zero contínuo. Escala de y 40 a 230.
- Rótulos: caixa de 80 px no centro da coluna, presa a x −8…419 do painel, além da ponta do par (preto junto da barra;
  a hachura empilha por fora quando está do mesmo lado do zero); halo branco. **n ≤ 6**: todos. **n ≥ 7**: só o mês de
  referência (os dois, encostados à direita), a maior e a menor barra do gráfico (de qualquer série; contas
  `T2 · Mês a mês · mês/série/resultado/sem estoque do maior|menor valor`). Colisão: referência > menor > maior; o
  rótulo que toca outro desliza até encostar e sai se o centro deixar a própria coluna.
- Eixo: n ≤ 8 "jan/26"; n ≥ 9 "jan", com o ano no primeiro mês da janela e em janeiro.

**Série dos tooltips** (item, degrau, indicador; área 444): coluna = 444 ÷ n; barra = mín(40, coluna − 12); rótulo só no
ponto e no extremo (regra de 06/10), caixa de 80 presa a x −18…382, o extremo desliza ou sai; com sinais mistos a
série cresce (zero + parte negativa + 42) para o rótulo negativo não tocar os meses.

**Cascata**: escala de y 30 a 214 — o rótulo do resultado negativo (fundo da barra + 4) termina antes do nome do
degrau (y 238).

**Contas e leituras**: tudo o que descreve a série olha só a janela (`dMes[Mes] >= [Série · primeiro mês]`): meses com
valor, com alta e queda (do segundo mês da janela em diante), meses com aba, primeiro mês com aba e os valores nele,
meses com sem estoque negativo, menor variação do período e a escala do mês a mês. As de mês anterior não mudam.
Minissérie do quadradinho: colunas de até 28 px que encolhem; matriz dos sinais: com n ≥ 9 (minissérie) e n ≥ 8
(matriz) o rótulo do mês alterna (fica o de referência e os de dois em dois para trás). Leitura de Sinais do mês
estreita (achado 18/22, destaques com rótulo curto) para caber nos 361 × 436 sem rolagem; o destaque do mês anterior
não repete o resultado (L058).

