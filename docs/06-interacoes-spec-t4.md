# Interações · especificação · Tela 04 · Resultado no tempo

Escrito pelo Fable 5.1 em 06/10/2026 (fase 2; revisado no mesmo dia com as correções do Alisson: leitura sobre o
painel — L065 — e tooltips mais objetivos), seguindo a linguagem comum da §1 de `docs/06-interacoes-spec.md`.
Tudo o que está aqui existe no Figma, arquivo `FjBWDk5odF9HaZ2pwhGosl`, página `03 · Mockup · Painel Criticidade de Obras`
(`269:685`), seção **`Interações · Tela 04`** (`304:3105`, x 0 · y 12780 · 10180 × 3240), com as quatro fileiras da
Tela 01: `Fileira · Tela atualizada e exemplos` `304:3106` · `Fileira · Versos` `304:3109` · `Fileira · Tooltips`
`304:3112` · `Fileira · Leituras e guia` `304:3115`. Instância da tela atualizada: `304:3118`.

Números: **só** de `mockup/data/criticidade-obras.json` (caminho de cada um na §7). Formatação pt-BR. Tratamento de dados
citado = Power Query. Versos, tooltips e guia são **cópias dos componentes-base** da Tela 01 (`Base · Verso`
`291:1149`, `Base · Tooltip` `292:1483`, `Base · Guia` `294:1315`) preenchidas por código com os mesmos helpers
(§1.2–1.4 da spec comum); as leituras partiram de `Base · Leitura` `294:1293` e foram redesenhadas na geometria do
painel (§4).

**Animação (anotada para o Power BI; o Alisson implementa):** contador nos números (sobem do zero até o valor,
~600 ms), barras entrando no estilo *racing* (crescem do zero em sequência, da esquerda para a direita ou de cima
para baixo, ~120 ms de defasagem) e linhas que se desenham da esquerda para a direita. Cada peça traz a sua linha
"Animação" abaixo.

---

## 0. O que mudou na Tela 04 (`281:723`)

### 0.1 Piso tipográfico (59 nós; o desenho não mudou)
- Segoe UI 12,5 → **13**: sublinhas dos cinco cartões (`279:1105/1109/1113/1118/1123`), subtítulos dos quatro painéis
  (`279:1126/1165/1238/1265`), textos de justificativa e "não exigida" da tabela (`279:1276/1284/1291/1299/1314/1321`).
- Segoe UI 12 e 11,5 → **13**: rótulos de mês dos dois gráficos (`279:1133…1163` e `279:1243…1263`).
- Barlow SemiBold 12,5 / Medium 12 → **14**: rótulos de valor das barras do resultado (`279:1131…1161`) e da hachura
  (`279:1132…1162`), rótulos de desvio do desembolso (`279:1242…1262`).
- Barlow 13,5 → **14**: coluna "variação" do Resultado por obra (`279:1177/1187/1197/1207/1217/1226/1235`) e coluna
  "× previsto" da tabela (`279:1275/1283/1290/1298/1305/1313/1320`).
- Ficaram como estavam (terciário ou igual à Tela 01): versaletes 9,5–10,5 (cabeçalhos de coluna, chip "EM BRANCO ·
  EXIGIDA", rótulos de filtro), "?" 12,5, linha de contexto da sidebar (12, igual à T01), rodapé 11.

### 0.2 Cartões e painéis da tela (ids da §0.2 da spec comum) e geometria no canvas 1920 × 1080
Cartões `289:7875…7879`. Painéis (x, y, w, h no canvas = prancheta em 300, 12 + posição interna):

| Painel | id · "?" | Geometria no canvas |
|---|---|---|
| Resultado da carteira, mês a mês | `289:7880` · `289:7881` | x 352 · y 282 · **998 × 416** |
| Resultado por obra | `289:7884` · `289:7885` | x 1360 · y 282 · **501 × 390** |
| Desembolso da carteira | `289:7888` · `289:7889` | x 352 · y 698 · **593 × 320** |
| Desembolso de jun/26 por obra | `289:7892` · `289:7893` | x 950 · y 698 · **911 × 320** |

Guia da página: `279:1085`.

### 0.3 Selo de origem ao lado do nome da obra (o selo do rodapé saiu das telas)
Como a tela ficou sem marca de origem do dado, cada obra das duas tabelas por obra ganhou o selo da lista da T01
(52 × 15, raio 3; `ILUSTR.` tracejado grafite 50 % com texto Barlow SemiBold 9 grafite 80 %; `REAL` cheio grafite com
texto branco), a **8 px** do fim do nome, 1 px abaixo do topo do nome. Contêineres dos painéis intactos (as leituras
os cobrem).

| Tabela | Selos (ids, REDINHA → PONTA NEGRA) | Coluna do nome | O que mudou dentro do painel |
|---|---|---|---|
| Resultado por obra (`289:7884`, 501 × 390) | `340:7853` · `340:7855` · `340:7857` · `340:7859` · `340:7861` (REAL) · `340:7863` · `340:7865` | nome em x 12 (Barlow SemiBold 14) + selo; a coluna vai de x 12 a **142** (PONTA NEGRA + ILUSTR. é o caso mais largo: 12 + 70 + 8 + 52) | as linhas de tendência e a linha pontilhada do zero começam em **x 148** e têm **138 px** (eram x 116 · 170 px; TIROL, que abre em março, começa em 203,2 · 82,8 px); o ponto final (x 283), as marcas (312) e os valores (326 / 416) não mudaram |
| Desembolso de jun/26 por obra (`289:7892`, 911 × 320) | `340:7867` · `340:7869` · `340:7871` · `340:7873` · `340:7875` (REAL) · `340:7877` · `340:7879` | nome em x 10 (Barlow SemiBold 13,5) + selo; a coluna vai de x 10 a **138** | colunas deslocadas: PREVISTO 114 → **146** · DESEMBOLSADO 214 → **246** · × PREVISTO 328 → **356** (marca) e 342 → **370** (valor) · JUSTIFICATIVA 420 → **440**, textos de 490 → **470 px** (terminam em 910); cabeçalhos de coluna acompanharam |

---

## 1. Decisões desta tela dentro da linguagem comum

- **Leitura (L065):** ocupa exatamente o retângulo do painel que explica (título + gráfico), sem véu na página; o
  resto da tela segue visível. Superfície offwhite, contorno 1 px `#0B0B0C`, **canto reto (raio 0, como os
  tooltips — acerto de padrão entre as quatro telas)**, sombra (0, 12, 32, 22 %) marcando o painel aberto. `×` de 28 px fixo no canto superior direito da própria área (no Power BI, botão transparente nessa
  posição); sem pílula "Fechar" (o × basta; clicar fora também fecha). Margens 24 (painel grande) ou 20 (pequeno).
  Achado em Barlow SemiBold 22/27 (grande) ou 20/25 (pequeno); explicação Segoe 14/20 ou 13,5/18; destaques em faixa
  creme (número Barlow 22, rótulo 13/17); "o que explica" e "como ler" 13,5/18 ou 13/17; piso 13 px. Conteúdo cabe
  sem rolagem (L034): painel grande recebe a leitura completa em duas colunas; painel pequeno recebe a versão
  condensada (achado e destaques sempre; explicação mais curta; "o que explica", "detalhe" e "como ler" só se
  couberem). Só o Guia continua cobrindo a tela inteira (véu 55 %).
- **Tooltips (pedido do Alisson):** bordas quadradas só no cartão e no cabeçalho preto (raio 0); chips (`EM BRANCO ·
  EXIGIDA`, raio 4) e selos (`REAL` / `ILUSTR.`, raio 3) mantêm o raio que têm na tela, como na §1.6 da linguagem
  comum — vale também dentro das leituras; um mini gráfico por tooltip, com uma série só, **sem eixo, grade ou legenda**, rótulo direto apenas no mês do
  ponto e no extremo oposto; altura só a que a leitura pede. O texto corrido do fim virou **uma linha de dados**
  (versalete + valor + detalhe curto) e **um rodapé de uma linha (≤ 70 caracteres)**, ou nenhum quando repetiria
  o que está acima. Alturas finais na §3.
- Selo `REAL` só na CAJUEIRO nas listas (as fictícias não levam `ILUSTR.` linha a linha — o rodapé da tela já diz; o
  `ILUSTR.` aparece quando a obra é o **título** do tooltip). Marcas de status sobre offwhite com contorno 35 %.
  Barras de contribuição e de desvio são pretas dos dois lados do zero (direção = lado; a faixa fica na marca da
  linha); barras de série por mês usam a cor da faixa (creme / hachura / preto).

---

## 2. Versos · Tela 04 (`Fileira · Versos`)

Gatilho: hover (ou foco) no cartão. Sem estados — o texto é fixo; só a régua lê `meta.regras_criticidade`.
**Animação:** nenhum contador (o verso não tem número); o gesto é o flip — a frente sobe e o verso entra (~220 ms).

| Componente · id | Cartão (id) | Regra (`COMO É CALCULADO`) | `DE ONDE VEM` | Régua | Campos JSON |
|---|---|---|---|---|---|
| `Verso · T4 · Resultado da carteira` `305:3416` | `289:7875` | Soma do resultado das 7 obras: crédito do executado + pago não aplicado − gasto. | D155 e E155 da aba do mês | ■ < 0 · ▨ 0 a +1,0% · □ ≥ +1,0% | `carteira.resultado`, `.resultado_pct`, `.obras_em_andamento`, `.orcamento`; régua `meta.regras_criticidade.resultado_pct` |
| `Verso · T4 · Mês anterior` `305:3429` | `289:7876` | A mesma soma, lida na aba do mês anterior. A linha de baixo é a diferença para o mês atual, em R$ e em p.p. do orçamento. | D155 e E155 da aba anterior | — | `carteira.resultado_mes_anterior`, `.resultado_pct_mes_anterior`, `.variacao_resultado`, `.variacao_resultado_pp` |
| `Verso · T4 · Sem estoque e adiantamentos` `305:3434` | `289:7877` | Resultado menos o que foi pago e ainda não virou obra: estoque e adiantamentos. | D155 − D146 a D150 da aba | ▨ < 0 atenção · □ ≥ 0 estável | `carteira.resultado_sem_ativos`, `.ativos_nao_consumidos`; régua `…resultado_sem_ativos` |
| `Verso · T4 · Desembolso do mês` `305:3445` | `289:7878` | Desembolsado e previsto do mês somados; desvio = desembolsado ÷ previsto − 1. | J136 e J137 da aba do mês | ■ > +25% · ▨ +10% a +25% · □ ≤ +10% | `carteira.desembolsado_mes_rs`, `.previsto_mes_rs`, `.desvio_desembolso`; régua `…desvio_desembolso` |
| `Verso · T4 · Justificativas do mês` `305:3458` | `289:7879` | Conta as obras com desvio acima de ±10% no mês (justificativa exigida) e quantas preencheram o campo da planilha. | G140 de cada aba · Power Query | — | `carteira.justificativas_exigidas`, `.justificativas_preenchidas`, `.justificativas_ausentes`; por obra `ultimo.justificativa_exigida/.justificativa_ausente` |

Os dois cartões repetidos da Tela 01 (Resultado da carteira, Desembolso do mês) usam a mesma regra e a mesma origem.
Em "Mês anterior", a aba citada muda com o filtro (`MAI26` para jun/26): a DAX monta "da aba anterior (MAI26)" a
partir de `obras[].serie[−2].aba` se quiser a aba explícita. Os cartões da frente animam: os cinco números contam
do zero (R$ 731 mil, R$ 1,09 mi, −R$ 2,19 mi, R$ 6,21 mi, 4), em sequência da esquerda para a direita.

---

## 3. Tooltips · Tela 04 (`Fileira · Tooltips`, 480 de largura, bordas quadradas)

### 3.1 `Tooltip · T4 · Mês` (`306:3416`, 480 × **330**) — estado `· primeiro mês` (`306:3478`, 480 × **281**)
**Gatilho:** hover numa coluna de "Resultado da carteira, mês a mês" (`289:7880`). **Ponto:** o mês.
Não repete o resultado nem o resultado sem estoque do mês (estão nos rótulos das barras).

| Bloco | Modelo (junho) | Variações | Campos |
|---|---|---|---|
| Cabeçalho | `RESULTADO DA CARTEIRA, MÊS A MÊS · JUN/26` · "junho de 2026" · `7 OBRAS COM ABA` | primeiro mês: `RESULTADO MÊS A MÊS · JAN/26 · PRIMEIRO MÊS DO HISTÓRICO` e `6 OBRAS COM ABA · TIROL SEM PLANILHA` (obras sem `serie[mes]`) | `carteira.serie[].mes/.obras` |
| `CONTRIBUIÇÃO DE CADA OBRA · R$ NO MÊS` · `% DO ORÇ.` | 7 linhas do maior ao menor resultado: marca de status da obra no mês (tracejada se em mobilização) · obra (+ `REAL`) · barra divergente preta (zero comum, sem linha de eixo; maior valor = 80 px) · valor em R$ · % do orçamento em grafite | linha some quando a obra não tem aba no mês | `obras[].serie[mes].resultado/.resultado_pct/.status/.mobilizacao`, `obras[].fonte` |
| Linha de dados `PAGOS E AINDA NÃO APLICADOS` | **R$ 2,92 mi** · maio R$ 2,62 mi | primeiro mês: **R$ 1,60 mi** · sem mês anterior | `carteira.serie[m].ativos_nao_consumidos`, `serie[m−1].ativos_nao_consumidos` |
| Rodapé (1 linha) | "Caiu em cinco das sete obras desde maio; só DUNAS e PONTA NEGRA subiram." | `Caiu em {n} das {m} obras desde {mês}; só {lista} subiram.` / `Subiu em {n} das {m}…; só {lista} caíram.` / `Nenhuma subiu.`; primeiro mês: rodapé some | sinal de `obras[].serie[m].resultado − serie[m−1].resultado` |

Linhas montadas (jun): `□ DUNAS R$ 600 mil +2,30%` · `▨ CAJUEIRO REAL R$ 293 mil +1,19%` · `□ PONTA NEGRA R$ 287 mil +1,40%` ·
`■ REDINHA R$ 90 mil +0,40%` · `▨ JANGADA R$ 45 mil +0,20%` · `⬚ TIROL −R$ 231 mil −0,90%` · `■ POTENGI −R$ 354 mil −1,60%`.
Jan: `DUNAS R$ 461 mil +1,80%` · `CAJUEIRO R$ 381 mil +1,57%` · `PONTA NEGRA R$ 259 mil +1,28%` · `REDINHA R$ 222 mil +1,00%` ·
`▨ POTENGI R$ 159 mil +0,73%` · `⬚ JANGADA R$ 99 mil +0,45%`. O que saiu na revisão: a frase "a maior queda na CAJUEIRO, que
tinha R$ 412 mil em maio" (o R$ 412 mil mora na leitura 4.2) e "é a distância entre as duas barras" (o subtítulo do
painel já diz). Para jun/26 a linha de dados repete o cartão da tela; existe pelos outros meses. A coluna "% do orç."
repete, em jun/26, o painel "Resultado por obra" — se o Alisson preferir, a medida a esvazia quando mês do tooltip =
mês do filtro.
**Animação:** os sete valores em R$ contam do zero; as sete barras correm do zero na ordem das linhas (de cima para
baixo), as negativas crescendo para a esquerda; o "R$ 2,92 mi" conta por último.

### 3.2 `Tooltip · T4 · Obra` (`307:3713`, 480 × **249**) — estado `· mobilização` (`307:3757`, 480 × **251**)
**Gatilho:** hover numa linha de "Resultado por obra" (`289:7884`). **Ponto:** a obra. Não repete o % de junho nem a
variação (estão na linha).

| Bloco | Modelo (REDINHA) | Variações | Campos |
|---|---|---|---|
| Cabeçalho | `RESULTADO POR OBRA · JAN–JUN/26 · ABA JUN26` · `REDINHA` `AT` `ILUSTR.` · `INÍCIO ABR/25 · TÉRMINO AGO/28` | `+ · EM MOBILIZAÇÃO` quando `ultimo.mobilizacao`; selo `REAL` quando `fonte = "real"` | `obra`, `codigo`, `fonte`, `inicio`, `termino_previsto`, `ultimo.aba/.mobilizacao`, `carteira.serie[0/−1].mes` |
| `RESULTADO, MÊS A MÊS · R$` | 6 barras (44 px para o maior |valor|), cor = faixa do resultado naquele mês, sem eixo; **rótulo só no mês do filtro e no extremo oposto** (REDINHA: jan R$ 222 mil, o melhor, e jun R$ 90 mil); negativos pendem abaixo da base com o rótulo embaixo; mês do filtro em Semibold | mês sem aba: sem barra, rótulo do mês a 35 % (TIROL jan/fev); extremo = máx. se o mês do filtro é o mín. (e vice-versa) | `serie[].resultado`, `serie[].indicadores_status.resultado_pct` |
| Linha de dados `SEM ESTOQUE` | **−R$ 721 mil** · R$ 811 mil pagos e não aplicados | TIROL: **−R$ 268 mil** · R$ 37 mil pagos e não aplicados | `ultimo.resultado_sem_ativos`, `ultimo.ativos_nao_consumidos` |
| Rodapé (1 linha) | "Melhor mês: janeiro. Cai desde abril; sem estoque, negativo nos seis meses." | `Melhor mês: {mês}.` (máx. de `resultado_pct`; se for o atual: "Melhor mês: o atual.") + tendência `cai/sobe desde {mês}` (1 mês só: `cai em {mês}`) + `sem estoque, negativo nos {n} meses / desde {mês} / positivo…`; mobilização: "Cai desde abril; com 3,6% executado, o canteiro vem antes do crédito." | `serie[].resultado_pct`, `serie[].resultado_sem_ativos`, `ultimo.exec_acum` |

Séries: REDINHA `R$ 222 mil · 202 · 207 · 166 · 161 · 90 mil` (jan estável, fev–jun atenção); TIROL `— · — · −R$ 63 mil ·
−107 · −166 · −231 mil` (todas críticas; rótulos em mar e jun). O que saiu: os blocos "melhor e pior mês" (virou
rodapé) e "mobilização" (virou rodapé no estado), o versalete-legenda "cor da barra: faixa da régua", o eixo e os
rótulos dos meses intermediários.
**Animação:** as seis barras correm do zero da esquerda para a direita (jan → jun); os dois rótulos e o "−R$ 721 mil"
contam do zero.

### 3.3 `Tooltip · T4 · Mês do desembolso` (`308:3713`, 480 × **330**) — estado `· primeiro mês` (`308:3787`, 480 × **281**)
**Gatilho:** hover num par de barras de "Desembolso da carteira" (`289:7888`). **Ponto:** o mês. Não repete o desvio
da carteira (rótulo da barra).

| Bloco | Modelo (junho) | Variações | Campos |
|---|---|---|---|
| Cabeçalho | `DESEMBOLSO DA CARTEIRA · JUN/26` · "junho de 2026" · `7 OBRAS COM ABA` | primeiro mês: `· PRIMEIRO MÊS DO HISTÓRICO` e `6 OBRAS COM ABA · TIROL SEM PLANILHA` | `carteira.serie[].mes/.obras` |
| `PREVISTO × DESEMBOLSADO, POR OBRA` · `DESVIO` | 7 linhas do maior ao menor desvio: marca = faixa do desembolso no mês · obra (+ `REAL`) · previsto (grafite) × desembolsado (Barlow) · barra preta do desvio (zero comum, sem linha; maior desvio = 60 px) · desvio | obra sem aba some | `obras[].serie[mes].previsto_mes_rs/.desembolsado_mes_rs/.indicadores.desvio_desembolso/.indicadores_status.desvio_desembolso` |
| Linha de dados `JUSTIFICATIVAS` | **4 de 5** · exigidas preenchidas · CAJUEIRO em branco | `{preenchidas} de {exigidas}` · `{lista} em branco` / `todas preenchidas`; jan: **3 de 4** · … · CAJUEIRO em branco | `obras[].serie[mes].justificativa` × desvio > ±10 % (ver §7) |
| Rodapé (1 linha) | "JANGADA saiu da faixa crítica (era +53% em maio); três seguem nela." | `{obra} saiu/entrou na faixa crítica (era {desvio} em {mês}); {n} seguem nela.` / `Nenhuma mudança de faixa desde {mês}.`; primeiro mês: rodapé some | `obras[].serie[m−1].indicadores.desvio_desembolso/.indicadores_status.desvio_desembolso` |

Linhas (jun): `■ CAJUEIRO REAL R$ 863 mil × R$ 1,36 mi +58%` · `■ TIROL R$ 333 mil × R$ 463 mil +39%` · `■ REDINHA R$ 469 mil ×
R$ 638 mil +36%` · `▨ POTENGI R$ 978 mil × R$ 1,15 mi +18%` · `▨ JANGADA R$ 666 mil × R$ 766 mil +15%` · `□ PONTA NEGRA R$ 153 mil ×
R$ 160 mil +5%` · `□ DUNAS R$ 1,73 mi × R$ 1,67 mi −4%`. Jan: `■ JANGADA R$ 190 mil × R$ 262 mil +38%` · `■ CAJUEIRO R$ 740 mil ×
R$ 931 mil +26%` · `▨ REDINHA R$ 252 mil × R$ 298 mil +18%` · `▨ POTENGI R$ 1,32 mi × R$ 1,46 mi +11%` · `□ DUNAS R$ 1,43 mi ×
R$ 1,52 mi +6%` · `□ PONTA NEGRA R$ 540 mil × R$ 528 mil −2%`. O que saiu: "CAJUEIRO, TIROL e REDINHA seguem acima de +25%;
DUNAS e PONTA NEGRA, dentro da faixa" (as marcas das linhas já dizem). Para jun/26 a tabela repete o painel "Desembolso
de jun/26 por obra"; existe pelos outros meses.
**Animação:** os sete desembolsados e os sete desvios contam do zero; as barras de desvio correm de cima para baixo;
o "4 de 5" conta por último.

### 3.4 `Tooltip · T4 · Obra do desembolso` (`309:3713`, 480 × **364**) — estados `· em branco` (`309:3766`, 480 × **387**) e `· não exigida` (`309:3823`, 480 × **272**)
**Gatilho:** hover numa linha de "Desembolso de jun/26 por obra" (`289:7892`). **Ponto:** a obra.

| Bloco | Modelo (REDINHA) | Variações | Campos |
|---|---|---|---|
| Cabeçalho | `DESEMBOLSO · JAN–JUN/26 · ABA JUN26` · `REDINHA` `AT` `ILUSTR.` · `INÍCIO ABR/25 · TÉRMINO AGO/28` | `REAL` (CAJUEIRO, selo creme sobre o cabeçalho) | `obra`, `codigo`, `fonte`, `inicio`, `termino_previsto` |
| `DESVIO SOBRE O PREVISTO, MÊS A MÊS` | 6 barras de desvio (%), cor = faixa do desembolso no mês, sem eixo; rótulo só no mês do filtro e no extremo oposto (REDINHA: fev +16% e jun +36%; CAJUEIRO: fev −5% e jun +58%; DUNAS: jan +6% e jun −4%); negativos abaixo da base | mês sem aba: rótulo do mês a 35 % | `serie[].indicadores.desvio_desembolso`, `serie[].indicadores_status.desvio_desembolso` |
| `JUSTIFICATIVA NA PLANILHA, MÊS A MÊS` · `EXIGIDA ACIMA DE ±10%` | 6 linhas `mês · texto da planilha` (é o histórico pedido no brief, não texto corrido) | texto vazio com desvio > ±10 %: chip tracejado `EM BRANCO · EXIGIDA` (raio 4, como na tela); dentro de ±10 %: "não exigida (dentro de ±10%)" em grafite 60 %; **vazio** (nenhum mês exigido): a lista some | `serie[].justificativa`, `serie[].indicadores.desvio_desembolso` |
| Rodapé (1 linha, grafite) | "Exigida e preenchida nos seis meses; na faixa crítica desde abril." | CAJUEIRO: "Quatro meses exigidos, nenhum preenchido; em branco há três meses."; DUNAS (vazio): "Dentro de ±10% nos seis meses: nenhuma justificativa exigida."; modelo: `Exigida em {n} meses, {m} preenchidas; {na faixa crítica desde {mês} / em branco há {k} meses / abaixo do previsto desde {mês}}` | idem |

Séries: REDINHA `+18 · +16 · +23 · +26 · +27 · +36 %` (jan–mar atenção, abr–jun crítico); CAJUEIRO `+26 · −5 · +8 · +20 · +38 ·
+58 %`, quatro meses exigidos (jan, abr, mai, jun), todos em branco; DUNAS `+6 · +2 · −3 · −3 · −2 · −4 %`, nada exigido.
O que saiu: "o desvio sobe desde março" (o gráfico mostra), o versalete-legenda e os rótulos intermediários.
**Animação:** as seis barras correm da esquerda para a direita; os dois rótulos contam do zero; as linhas da lista
entram de cima para baixo (fade curto), o rodapé por último.

---

## 4. Leituras · Tela 04 (`Fileira · Leituras e guia`; recorte: carteira, jun/26) — geometria do painel (L065)

Cada leitura ocupa o retângulo do seu painel (§0.2) e cobre título + gráfico; o resto da tela fica visível. Os textos
e variações abaixo valem para a DAX; a tabela diz o que foi **condensado** em relação à primeira versão (painel de
760 centrado).

### 4.1 `Leitura · T4 · Resultado da carteira, mês a mês` (`310:4276`) — "?" `289:7881`
**Geometria:** x 352 · y 282 · **998 × 416** (painel grande → leitura completa em duas colunas: esquerda 590 px com
achado, explicação, destaques e "o que explica"; direita 330 px com detalhe e "como ler"). Nada saiu.

| Bloco | Texto (jun/26) | Modelo e variações | Campos |
|---|---|---|---|
| Sobretítulo | `LEITURA · RESULTADO DA CARTEIRA, MÊS A MÊS · JANEIRO A JUNHO DE 2026` | primeiro e último mês da série | `carteira.serie[0/−1].mes` |
| Achado (22/27) | "Cai todo mês desde janeiro; sem estoque e adiantamentos, junho fecha em −R$ 2,19 mi." | piora: `Cai todo mês desde {mês}` (queda em todas as transições) / `Cai desde {mês}` / `Caiu em {n} dos {m} meses`; melhora: `Sobe desde {mês}; sem estoque e adiantamentos, {mês} fecha em {R$}` — número-chave = `resultado_sem_ativos` do mês (se ≥ 0: "…fecha em {R$}, positivo mesmo sem estoque") | `carteira.serie[].resultado`, `serie[−1].resultado_sem_ativos` |
| Explicação (14/20) | "A queda não vem de uma obra só: cinco das sete fecharam junho abaixo de maio, e as duas negativas, POTENGI e TIROL, pesam cada vez mais. Enquanto isso, o dinheiro pago e ainda não aplicado quase dobrou no semestre — é ele que sustenta o resultado oficial acima de zero, e a distância entre as duas barras cresce todo mês." | `{n} das {m} fecharam {mês} abaixo de {mês anterior}` (em palavras); `as {n} negativas, {lista}, pesam cada vez mais` só se o resultado delas caiu; "quase dobrou / dobrou / subiu" (`ativos` último ÷ primeiro); melhora: "…a distância entre as barras encolhe desde {mês}"; sem obra negativa: "nenhuma obra fecha o mês no negativo" | `obras[].serie[m/m−1].resultado`, `carteira.serie[].ativos_nao_consumidos` |
| Destaques | `+1,16%` resultado sobre o orçamento em janeiro; +0,45% em junho · `R$ 600 mil` resultado da DUNAS em junho, a maior contribuição positiva · `2` obras no negativo em junho; nenhuma em janeiro | 1: `serie[0].resultado_pct` × `serie[−1].resultado_pct`; 2: maior `obras[].serie[−1].resultado` ("a maior contribuição positiva" / se todos negativos: "a menor perda"); 3: contagem de resultados negativos no mês × no primeiro mês | `carteira.serie[]`, `obras[].serie[]` |
| O que explica (13,5/18) | "O resultado oficial soma o que foi pago e ainda não virou obra — estoque, adiantamentos e saldos de contrato — como se fosse ganho. Esse valor subiu todo mês, puxado por CAJUEIRO e REDINHA, e o resultado sem ele ficou negativo nos seis meses: a barra hachurada desce porque o gasto cresce mais rápido do que a obra medida." | "subiu todo mês" / "subiu em {n} dos {m} meses" / "caiu desde {mês}"; "puxado por {as duas obras com maior alta de `ativos`}"; "negativo nos {m} meses" / "negativo desde {mês}" / "positivo desde {mês}"; "desce / sobe porque o gasto cresce mais rápido / mais devagar do que a obra medida" | `obras[].serie[].ativos_nao_consumidos`, `carteira.serie[].resultado_sem_ativos` |
| Detalhe (coluna direita) | barras creme dos "pagos e ainda não aplicados" por mês (jan → jun), **rótulo só no primeiro e no último**: R$ 1,60 mi … R$ 2,92 mi; mês do filtro em Semibold | é a terceira série, que o gráfico só mostra como distância | `carteira.serie[].ativos_nao_consumidos` |
| Como ler (13/17) | "A barra preta é o resultado do mês: crédito do executado mais o pago e ainda não aplicado, menos o gasto. A hachurada tira esse pago e não aplicado — é o resultado "de verdade" até aqui. Quanto mais as duas se afastam, mais a carteira depende de estoque e adiantamentos. Passe o mouse num mês para ver a contribuição de cada obra." | fixo | — |

**Animação:** os três destaques contam do zero (+1,16 %, R$ 600 mil, 2) e o "−R$ 2,19 mi" do achado também; as seis
barras do detalhe correm de jan a jun, com os dois rótulos contando.

### 4.2 `Leitura · T4 · Resultado por obra` (`310:7994`) — "?" `289:7885`
**Geometria:** x 1360 · y 282 · **501 × 390** (painel pequeno → versão condensada, uma coluna, margens 20).
**O que saiu:** a tabela "janeiro × tendência" (detalhe) e o "como ler" (régua do resultado e da variação). A
explicação perdeu a primeira frase ("A piora é espalhada, mas tem duas naturezas"); "o que explica" ficou em uma
frase. As tendências por obra (`cai desde abril`, `sobe desde março`…) continuam no modelo da §4.2 da primeira
versão e no tooltip 3.2.

| Bloco | Texto | Modelo e variações | Campos |
|---|---|---|---|
| Sobretítulo | `LEITURA · RESULTADO POR OBRA · JUNHO DE 2026` | mês por extenso | `carteira.mes_ref` |
| Achado (20/25) | "5 das 7 obras pioraram em junho: POTENGI e TIROL seguem negativas; a CAJUEIRO caiu mais." | `{n} das {m} obras pioraram em {mês}` (variação < 0); `{lista} seguem negativas` / `{obra} virou negativa` / "nenhuma está no negativo"; `a {obra} caiu mais` (menor `variacao_resultado_pp`); melhora: `{n} das {m} obras melhoraram em {mês}: … a {obra} subiu mais` | `obras[].ultimo.indicadores.variacao_resultado_pp`, `.resultado` |
| Explicação (13,5/18) | "POTENGI e TIROL perdem dinheiro de fato — uma com três quartos da obra executados, a outra em mobilização, quando o custo de canteiro vem antes do crédito. As demais ainda ganham, mas cada vez menos: só DUNAS e PONTA NEGRA terminam o semestre acima de onde começaram." | frase por obra negativa com `exec_acum` em fração ou "em mobilização"; fecho: "só {lista} terminam o semestre acima de onde começaram" (`serie[−1].resultado_pct > serie[0].resultado_pct`) / "todas terminam abaixo…" / "a maioria termina acima…" | `obras[].ultimo.exec_acum/.mobilizacao`, `obras[].serie[0/−1].resultado_pct` |
| Destaques | `R$ 412 mil` CAJUEIRO em maio, antes da maior queda · `−R$ 231 mil` TIROL em junho, 3,6% executado · `4` obras estáveis em janeiro; três em junho | 1: `serie[−2].resultado` da obra com maior queda; 2: `ultimo.resultado` da obra em mobilização (ou da 2.ª negativa); 3: contagem de `indicadores_status.resultado_pct = 0` no primeiro mês × no último | `obras[].serie[]`, `obras[].ultimo` |
| O que explica (13/17) | "O resultado cai quando o gasto corre à frente da medição: na REDINHA e na POTENGI o físico atrasado segura o crédito; na CAJUEIRO o desembolso acima do previsto consumiu parte do ganho. Quatro obras perdem pontos pela variação do mês." | obras com `desvio_fisico_pp` fora da faixa → "o físico atrasado segura o crédito"; físico adiantado + desembolso crítico → "o desembolso acima do previsto consumiu parte do ganho"; fecho com `carteira.indicadores[variacao_resultado_pp].atencao + criticas` em palavras | `obras[].ultimo.indicadores_status`, `carteira.indicadores[]` |

**Animação:** os três destaques contam do zero; o "5 das 7" do achado conta. (As linhas de tendência do painel por
trás se desenham da esquerda para a direita quando a página abre, obra por obra de cima para baixo.)

### 4.3 `Leitura · T4 · Desembolso da carteira` (`312:3713`) — "?" `289:7889`
**Geometria:** x 352 · y 698 · **593 × 320** (painel pequeno → condensada, margens 20).
**O que saiu:** a linha do tempo "obras na faixa crítica, mês a mês" (detalhe) e o "como ler" (régua do desembolso e
a tolerância de ±10 %). A explicação perdeu "Não é um mês fora da curva" e a frase "Só DUNAS e PONTA NEGRA ficaram dentro
da faixa estável"; "o que explica" ficou em uma frase.

| Bloco | Texto | Modelo e variações | Campos |
|---|---|---|---|
| Sobretítulo | `LEITURA · DESEMBOLSO DA CARTEIRA · JANEIRO A JUNHO DE 2026` | | `carteira.serie[0/−1].mes` |
| Achado (20/25) | "Acima do previsto nos 6 meses do semestre, e piorando: o desvio da carteira sobe desde março." | `Acima do previsto em {n} dos {m} meses`; "e piorando: o desvio sobe desde {mês}" / "mas melhorando: o desvio cai desde {mês}" / "e estável"; nunca acima: "Dentro do previsto nos {m} meses" | `carteira.serie[].desvio_desembolso` |
| Explicação (13,5/18) | "A carteira gasta mais do que planeja desde janeiro, e a distância entre as barras cresce desde março. Em junho, três obras estão na faixa crítica — REDINHA, TIROL e a CAJUEIRO, com o maior excesso em reais e sem justificativa." | "desde {primeiro mês acima}"; `{n} obras estão na faixa crítica — {lista}` (status 2), com "a {obra}, com o maior excesso em reais" (máx. `diferenca_desembolso_rs`) e "e sem justificativa" se `justificativa_ausente` | `carteira.indicadores[desvio_desembolso]`, `obras[].ultimo.diferenca_desembolso_rs/.justificativa_ausente` |
| Destaques | `R$ 496 mil` maior excesso sobre o previsto em junho: a CAJUEIRO · `R$ 5,00 mi` desembolsados em janeiro; previstos R$ 4,47 mi · `+68%` desvio do JANGADA em abril, o pico do semestre | 1: máx. `ultimo.diferenca_desembolso_rs`; 2: `serie[0].desembolsado_mes_rs` × `.previsto_mes_rs`; 3: máx. de `obras[].serie[].indicadores.desvio_desembolso` | `obras[].ultimo`, `carteira.serie[0]`, `obras[].serie[]` |
| O que explica (13/17) | "As justificativas repetem três causas — efetivo, aditivos e medições concentradas; só a CAJUEIRO não explicou nenhum dos quatro meses exigidos." | as causas mais frequentes de `serie[].justificativa`; fecho com a obra com mais meses exigidos em branco ("todas as justificativas exigidas foram preenchidas" se nenhuma) | `obras[].serie[].justificativa`, `.indicadores.desvio_desembolso` |

**Animação:** os três destaques contam do zero (R$ 496 mil, R$ 5,00 mi, +68 %); o "6 meses" do achado conta.

### 4.4 `Leitura · T4 · Desembolso de jun/26 por obra` (`312:3768`) — "?" `289:7893`
**Geometria:** x 950 · y 698 · **911 × 320** (painel largo e baixo → duas colunas: esquerda 520 px com achado,
explicação, destaques e "o que explica"; direita 291 px com a grade das justificativas e "como ler").
**O que saiu:** a explicação ficou mais curta (sem "contam uma história coerente", sem "na planilha" repetido);
"o que explica" perdeu a frase sobre a diretoria e o fecho "a CAJUEIRO é a única em branco" (o achado já diz); "como
ler" ficou só com a tolerância e o gesto do mouse (a régua do desembolso mora no tooltip 3.4 e na 4.3).

| Bloco | Texto | Modelo e variações | Campos |
|---|---|---|---|
| Sobretítulo | `LEITURA · DESEMBOLSO POR OBRA · JUNHO DE 2026` | | `carteira.mes_ref` |
| Achado (20/25) | "5 obras passaram da tolerância em junho; só a CAJUEIRO, a de maior desvio, não justificou." | `{n} obras passaram da tolerância em {mês}; {todas justificaram / só {obra}[, a de maior desvio,] não justificou / {lista} não justificaram}`; n = 0: "Nenhuma obra passou da tolerância em {mês}: nada a justificar." | `carteira.justificativas_exigidas/.justificativas_ausentes`, `obras[].ultimo.desvio_desembolso` |
| Explicação (13,5/18) | "Efetivo reforçado na TIROL e no JANGADA, aditivo na REDINHA, compra antecipada na POTENGI — gastos que recuperam atraso ou viram estoque. O silêncio da CAJUEIRO preocupa: maior excesso do mês, terceiro mês seguido sem explicação." | resumo das `ultimo.justificativa` preenchidas por obra; obra ausente: "{maior excesso do mês, se for}, {n.º} mês seguido sem explicação" (`serie[]` com texto vazio e desvio > ±10 %, contados do fim); sem ausente: "Nenhuma ficou em branco." | `obras[].ultimo.justificativa/.justificativa_ausente/.diferenca_desembolso_rs`, `serie[].justificativa` |
| Destaques | `R$ 1,17 mi` pagos e não aplicados na CAJUEIRO em junho · `0 de 4` preenchidas pela CAJUEIRO entre as exigidas · `R$ 176 mil` excesso da POTENGI, maior entre as justificadas | 1: `ultimo.ativos_nao_consumidos` da obra ausente (ou da de maior desvio); 2: preenchidas ÷ exigidas no semestre dessa obra; 3: máx. `diferenca_desembolso_rs` entre as obras com justificativa | `obras[].ultimo`, `obras[].serie[]` |
| O que explica (13/17) | "Acima de ±10% a planilha tem um campo próprio para a explicação. DUNAS (abaixo do previsto) e PONTA NEGRA (fase final) não precisavam justificar." | `{obra} ({"abaixo do previsto" se desvio < 0 / "fase final" se exec_acum > 95 %})` para as obras dentro da faixa; nenhuma: "Todas as obras passaram da tolerância." | `obras[].ultimo.desvio_desembolso/.exec_acum/.justificativa_exigida` |
| Detalhe (coluna direita) | `DETALHE · JUSTIFICATIVAS NO SEMESTRE`: grade 7 obras × 6 meses (■ exigida e preenchida · □ contorno = exigida e em branco · creme = não exigida · vazio = sem aba) + `DE EXIGIDAS`: REDINHA 6 de 6 · POTENGI 4 de 4 · TIROL 4 de 4 · JANGADA 6 de 6 · CAJUEIRO 0 de 4 · DUNAS — · PONTA NEGRA 4 de 4; legenda em uma linha | exigida = |`desvio_desembolso`| > 0,10; preenchida = `justificativa` não vazia; "—" quando nada exigido | `obras[].serie[].justificativa/.indicadores.desvio_desembolso` |
| Como ler (13/17) | "Acima de ±10%, para mais ou para menos, a justificativa é exigida; passe o mouse numa obra para ver o histórico." | fixo | — |

**Animação:** os três destaques contam do zero; as marcas da grade entram linha a linha (de cima para baixo) e, dentro
da linha, de jan a jun; os "6 de 6 / 4 de 4" contam por último.

---

## 5. `Guia · T4` (`313:3713`, 760 × 916) — "?" `279:1085` (`Ajuda · Guia da página`) — sem mudança
Véu 55 % + marcadores numerados + painel em x 400 (y 82, centrado na vertical); único painel que cobre a tela inteira.
Introdução: "A tela responde em dois tempos. Em cima, o resultado: como a carteira chegou ao número do mês e qual
obra puxa para cada lado. Embaixo, o gasto: se a carteira desembolsou além do previsto e se cada obra explicou."
1. **Cartões do mês** — Resultado da carteira (o escuro é a resposta), mês anterior, sem estoque e adiantamentos, desembolso e justificativas. Passe o mouse: o cartão vira e mostra como é calculado e de onde vem.
2. **Resultado da carteira, mês a mês** — Barra preta: o resultado; barra hachurada: o resultado sem estoque e adiantamentos. Passe o mouse num mês para ver a contribuição de cada obra e o que foi pago e ainda não aplicado.
3. **Resultado por obra** — Resultado em % do orçamento no mês, tendência do semestre e variação sobre o mês anterior. Passe o mouse numa obra para ver os seis meses em reais e o melhor e o pior mês.
4. **Desembolso da carteira** — Previsto (creme) × desembolsado (preto), mês a mês, com o desvio em cima. Passe o mouse num mês para ver previsto × desembolsado obra por obra.
5. **Desembolso do mês por obra** — Previsto, desembolsado, desvio e a justificativa escrita na planilha; "em branco" é o campo vazio. Passe o mouse numa obra para ver o histórico do desvio e das justificativas.
6. **Filtro e ajuda** — O topo mostra o recorte em uso. O funil abre os filtros de mês e obra; o "?" redondo abre este guia; o "?" de cada painel abre a leitura daquele gráfico.
7. **Navegação** — Visão geral · Análise crítica · Avanço físico · Resultado no tempo. A obra e o mês escolhidos valem para todas as folhas.
`AS FAIXAS DESTA TELA`: **Resultado da obra** ■ crítico · abaixo de 0 ▨ atenção · 0 a +1,0% □ estável · +1,0% ou mais ·
**Desembolso × previsto** ■ crítico · acima de +25% ▨ atenção · +10% a +25% □ estável · até +10%. Nota: "A pontuação de
0 a 100 que ordena as obras está na Visão geral; aqui cada marca segue a faixa do próprio indicador, e o desvio do
desembolso acima de ±10% exige justificativa na planilha."
Marcadores (canvas 1920): 1 (338, 130) cartões · 2 (338, 268) mês a mês · 3 (1346, 268) por obra · 4 (338, 684)
desembolso da carteira · 5 (1300, 684) desembolso por obra · 6 (1452, 44) filtro/ajuda · 7 (14, 218) navegação.
**Animação:** os sete marcadores aparecem em sequência (1 → 7); o painel não anima.

---

## 6. Exemplos montados (fileira 1)
`Exemplo · T4 · Cartão virando` `315:3713` (frame `flip · meio do gesto` `315:4026` sobre o cartão "Justificativas do
mês": fundo branco da prancheta + clone da frente a −66 px + instância do verso a +54 px + linha de dobra + cursor) ·
`Exemplo · T4 · Tooltip apontando` `315:4042` (cursor na coluna de jun/26 do resultado da carteira; instância de
`Tooltip · T4 · Mês` em cursor + 16 px) · `Exemplo · T4 · Leitura aberta` `315:4410` (**sem véu**: instância de
`Leitura · T4 · Resultado da carteira, mês a mês` exatamente sobre o painel, em 352, 282; o resto da tela segue
visível) · `Exemplo · T4 · Guia aberto` `315:4766` (véu + 7 marcadores + `Guia · T4` em x 400, y 82).

---

## 7. Números: origem e o que falta no JSON

**Conferidos (caminho no JSON):** `carteira.serie[]` (resultado 1,58 · 1,52 · 1,35 · 1,10 · 1,09 mi · 731 mil; resultado_pct
jan +1,16 %; ativos 1,60 · 1,60 · 1,62 · 2,11 · 2,62 · 2,92 mi; resultado_sem_ativos −15 mil … −2,19 mi; previsto/desembolsado
jan 4,47 / 5,00 mi; desvio 12 · 5 · 6 · 11 · 17 · 19 %; obras 6 · 6 · 7 · 7 · 7 · 7); `obras[].serie[]` de cada obra
(resultado em R$ e %, status, mobilização, previsto/desembolsado, desvio, justificativa, ativos, resultado_sem_ativos,
indicadores_status); `obras[].ultimo` (diferenca_desembolso_rs 169 · 176 · 130 · 100 · 496 · −69 · 8 mil; exec_acum
TIROL 3,6 %, POTENGI 74,0 %; justificativa_exigida/ausente; inicio/termino); `carteira.justificativas_*`; `meta`.
Arredondamentos: JANGADA fev `resultado_sem_ativos` −436 → citado só em texto ("negativo nos seis meses"), nunca como
"−R$ 0 mil"; TIROL mar `ativos_nao_consumidos` = 0 é zero real (apareceria como "R$ 0", não some).

**Derivados por comparação/contagem de campos existentes (não são contas novas, mas convém campo para a DAX não varrer a série):**
- tendência `cai/sobe desde {mês}` de `resultado_pct` e de `desvio_desembolso` por obra e da carteira (sinal de
  transições consecutivas) — sugestão `serie[].tendencia_resultado` / `tendencia_desembolso` = `{sinal, desde}`;
- "caiu em cinco das sete obras" (sinal de `serie[m].resultado − serie[m−1].resultado`) e "caiu mais" (mín. de
  `variacao_resultado_pp`);
- justificativa **exigida** por mês = |`desvio_desembolso`| > 0,10 e **preenchida** = texto não vazio — hoje só existe
  em `ultimo` (`justificativa_exigida/ausente`). Sugestão: `serie[].justificativa_exigida` e `serie[].justificativa_ausente`
  por obra, e `carteira.serie[].justificativas_exigidas/preenchidas` por mês (tooltip 3.3 em meses passados, grade da
  leitura 4.4, "terceiro mês seguido em branco");
- "pico do semestre" (+68 % JANGADA abr) = máx. de `obras[].serie[].desvio_desembolso`; extremo oposto ao mês do
  filtro nos gráficos dos tooltips 3.2 e 3.4 (máx./mín. da série da obra);
- obras na faixa crítica por mês (modelo da 4.3) = contagem de `indicadores_status.desvio_desembolso = 2`.

**Não usados por falta de campo:** desvio do desembolso da carteira em R$ por mês (só há % em `carteira.serie`; a
diferença em R$ por obra só existe em `ultimo.diferenca_desembolso_rs`, não em `serie[]`) — por isso "excesso em reais"
só é dito para jun/26; `ativos_nao_consumidos` por obra no mês anterior ficou de fora para não repetir número.

---

## 8. O que fica diferente no Power BI (além da §8 da spec comum)
- **Leitura = marcador de exibição** que liga um HTML Content **do tamanho exato do painel** (geometria da §0.2) por
  cima do visual; sem retângulo de véu. O `×` é um botão transparente de 28 px no canto superior direito do painel;
  um botão transparente sobre o resto da página também fecha ("clicar fora"). O guia continua com véu.
- **Tooltips:** página de tooltip 480 × altura da §3 (281–387), fundo offwhite com borda 1 px e cantos retos;
  cabeçalho = retângulo preto; chips e selos com o raio da tela (4 e 3). A leitura também tem cantos retos. As barras (contribuição, desvio e séries por mês) são um visual de barras nativo sem
  eixo, grade ou legenda, ou HTML Content; a cor por faixa vem de uma medida de status por mês; os rótulos de valor
  aparecem só no mês do filtro e no extremo (medida que devolve `BLANK()` nos outros). Linha de dados e rodapé são
  medidas de texto (rodapé = `BLANK()` no primeiro mês).
- **Animação:** contador e *racing* via HTML Content (transição CSS / `requestAnimationFrame` nas barras e nos
  números; `stroke-dashoffset` nas linhas de tendência do painel "Resultado por obra"); nos visuais nativos, a
  animação de entrada do Power BI. Em modo apresentação e em exportação não há animação (estado final).
- O chip `EM BRANCO · EXIGIDA` e a grade da leitura 4.4 são HTML Content (tabela com marcas em CSS); o "—" do DUNAS é
  texto, não zero.
- O exemplo do tooltip mostra uma posição possível; perto da borda inferior o Power BI inverte o tooltip para cima
  (caso das linhas de baixo da tabela de desembolso).

---

## 9. Séries de 1 a 12 meses (janela do drawer) — 06/10/2026, Opus 5.5

Figma: seção `Interações · Tela 04`, fileira **`Fileira · Janela de até 12 meses`** (`350:7993`), com a nota de regras
`Nota · Regras da janela · T4` (`350:7996`), os painéis de exemplo com 12, 8 e 3 meses (`350:15391`, `350:15466`,
`350:15531`), Desembolso e Resultado por obra com 12 meses (`350:15977`, `350:16034`), os tooltips de obra e de obra do
desembolso com 12 meses (`350:16383`, `350:16499`), quatro variantes do cartão Justificativas do mês (`350:16911…16929`)
e os detalhes das leituras com 12 meses (`351:7994`, `351:8086`). Em 12 meses, set–dez/25 são valores de exemplo.

- **Janela:** `dJanela` (12, 9, 6 ou 3 meses; padrão 12) define o primeiro mês da série (`[Série · primeiro mês]`,
  nunca antes de jan/26). n = meses mostrados (`[Série · meses até a referência]`, 8 em ago/26); x de cada mês =
  `[Série · posição na janela]`.
- **Coluna = área ÷ n.** Resultado mês a mês: 960 ÷ n, barra = mín(40; 0,36 × coluna), 4 px entre as barras.
  Desembolso: 560 ÷ n, barra = mín(28; 0,40 × coluna), 3 px. Tooltips: 447 ÷ n, barra = mín(40; 0,55 × coluna).
- **Rótulos:** Resultado mês a mês até 8 meses em todo mês ("R$ 340 mil"); de 9 a 12, só referência, máximo e mínimo
  de cada série, compactos ("−3,65 mi"). Desembolso: desvio em todo mês (13 px a partir de 10). Tooltips: referência e
  extremo oposto; em R$, sem "R$" de 7 meses em diante.
- **Margens laterais:** rótulo centrado na própria barra e preso na coluna (CSS `clamp`); nos tooltips, preso à área e o
  do extremo recua para a esquerda quando encostaria no da referência.
- **Mesmo lado do zero:** o rótulo da barra mais curta vai para o outro lado do zero, junto da base.
- **Eixo:** "jan/26" até 8 meses; de 9 a 12, "jan" com o ano só no primeiro mês e em janeiro. Desembolso: "jan", com o
  ano no primeiro mês e em janeiro quando a janela cruza a virada.
- **Tendência por obra:** x = 138 × (posição − 1) ÷ (n − 1); subtítulo "tendência {primeiro mês da janela} a {ref}".
- **Tooltip da obra do desembolso:** os 6 meses mais recentes, um por linha, e uma linha de resumo dos anteriores da
  janela ("jan–fev · 1 exigida, nenhuma preenchida (1 dentro de ±10%)"); página de 407 px.
- **Grade da leitura 4.4:** nome 64 px, mês = mín(22; 174 ÷ n), cabeçalho "JAN" até 8 meses e a inicial acima disso;
  "DE EXIG." quando "DE EXIGIDAS" não cabe.
- **Cartão Justificativas do mês:** uma linha só (até 39 caracteres): "4 em branco: JANGADA, POTENGI e mais 2" (do maior
  para o menor desvio), "todas as exigidas preenchidas", "nenhuma exigida: tudo dentro de ±10%".
- **Contas:** tudo o que descreve a série olha só a janela (sequências, "em x de y meses", "desde", melhor mês, pico,
  meses acima do previsto, justificativas no período). Comparações mês a mês da carteira só entre dois meses da janela;
  a variação da obra (aba × aba anterior, conta de mês anterior) entra também no primeiro mês da janela, como na T1.
  Período nos textos: 3 meses "trimestre", 6 "semestre", os demais "período" (só quando o recorte tem aba em todos).
