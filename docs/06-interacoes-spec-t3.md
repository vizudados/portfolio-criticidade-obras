# Interações · especificação · Tela 03 · Avanço físico (fase 2)

Escrito pelo Fable 5.1 em 06/10/2026, seguindo a linguagem comum da §1 de `docs/06-interacoes-spec.md`, com as duas
correções do Alisson do mesmo dia: **L065** (a leitura do "?" cobre só o painel que explica, sem véu) e os três ajustes
dos tooltips (cantos quadrados · mini gráfico objetivo · rodapé em uma linha). Tudo o que está aqui existe no Figma,
arquivo `FjBWDk5odF9HaZ2pwhGosl`, página `03 · Mockup · Painel Criticidade de Obras` (`269:685`), seção **`Interações · Tela 03`**
(`306:3530`, x 0 · y 9340 · 10180 × 3240): `Fileira · Tela atualizada e exemplos` `306:3531` · `Fileira · Versos`
`306:3534` · `Fileira · Tooltips` `306:3537` · `Fileira · Leituras e guia` `306:3540` (leituras em x 0 · 1068 · 1569 ·
2070, guia em 3138, y 80).

Números: **só** de `mockup/data/criticidade-obras.json` (caminho de cada um na §7). Formatação pt-BR. Tratamento de dados
citado = Power Query. Obra em foco = **REDINHA** (`obras[0]`, a mais crítica); mês de referência jun/26.

**Animação** (o Alisson implementa no Power BI; aqui só a anotação, uma linha por peça): números contam do zero até o
valor (contador ~600 ms, ease-out); barras crescem do zero **em sequência** (racing: uma de cada vez, ~120 ms de
intervalo, da esquerda para a direita / de cima para baixo); linhas se desenham da esquerda para a direita (~900 ms).
Texto corrido, chips, marcas e selos não animam. Com "reduzir movimento" do sistema, tudo aparece pronto.

---

## 0. Ajustes na Tela 03 (`281:722`)

### 0.1 Piso tipográfico (70 nós; rótulos ≥ 13, valores ≥ 14; versaletes 9–11 ficaram)
| Grupo | Nós | De → para |
|---|---|---|
| Sublinhas dos cartões | `277:1100` `277:1103` `277:1107` `277:1112` `277:1116` | Segoe 12,5 → **13** |
| Subtítulos dos painéis | `277:1119` `277:1160` `277:1187` `277:1243` | Segoe 12,5 → **13** |
| Legenda da curva S | `277:1120` `277:1122` `277:1124` | Segoe 12 → **13** (a última termina em x 987, antes do "?" em 1006) |
| Eixo Y da curva S | `277:1127` `277:1129` `277:1131` `277:1133` | Segoe 11 → **13** |
| Meses da curva S | `277:1149` … `277:1154` | Segoe 11,5 → **13** |
| Meses do ritmo | `277:1165` `277:1169` `277:1173` `277:1177` `277:1181` `277:1185` | Segoe 11 → **13** |
| Rótulos de valor do ritmo | `277:1164` `277:1168` `277:1172` `277:1176` `277:1180` `277:1184` | Barlow Medium 11 → **Barlow SemiBold 14** |
| "24,1% × 28,0%" do avanço | `278:718` `278:725` `278:733` `278:742` `278:751` `278:758` `278:765` | Segoe 12 → **13** (sublinha da linha; a maior, PONTA NEGRA, fecha em x 367 < marca em 382) |
| Desvio p.p. do avanço | `278:720` `278:728` `278:736` `278:745` `278:753` `278:760` `278:767` | Barlow SemiBold 13,5 → **14** |
| Rótulos finais da curva S | `277:1155` (13 → **14**) `277:1156` (13,5 → **14**) `277:1158` (13 → **14**; fundo `280:720` alargado para 62) | |
| Anos da linha do tempo | `277:1245` … `277:1257` | Barlow Medium 11 → **13** |
| Nomes das obras na linha do tempo | `277:1261` … `277:1297` | Barlow 12,5 → **13** |
| Nota "Tracejado: obras a entrar…" | `277:1299` | Segoe 11,5 → **13** |

Ficaram como estavam (terciário): versaletes 10–10,5 (`FOLHA 03…`, rótulos dos cartões, `OBRA`/`MÊS`, `VIZU DADOS`,
selo de origem), chip `JUN/26` (10), selo `ILUSTR.` (9), rodapé "Fonte e tratamento" (11), "?" dos painéis (12,5),
linha de contexto da sidebar (12 — peça compartilhada entre as telas, não mexi). A instância da tela na proposta e as
instâncias da seção acompanham sozinhas.

### 0.2 Nada mais foi alterado na tela
Cartões (`289:7408` … `289:7412`), painéis (`289:7413` `289:7417` `289:7421` `289:7425`) e os "?" (`289:7414` `289:7418`
`289:7422` `289:7426`) já estavam nomeados pela fase 1.

---

## 1. Decisões de design desta tela (além da §1 comum)

- **L065 · leitura na geometria do painel.** Cada leitura ocupa exatamente o retângulo do `Painel · <nome>` da tela
  (título + gráfico), em coordenadas do canvas 1920 × 1080; o resto da tela segue visível, **sem véu**. Superfície:
  offwhite, **raio 0** (canto reto, como os tooltips), borda 1 px `#0B0B0C` cheia, sombra (0, 12, 32, 22 %) — padrão
  acertado entre as quatro telas; a sombra marca o painel aberto. O **×** (32 px,
  contorno 30 %) fica fixo no canto superior direito da área, sobre o lugar do "?" do painel; **não há pílula
  "Fechar"** (o × basta e clicar fora também fecha). O conteúdo cabe sem rolagem (L034): painel grande (Curva S
  1028 × 402, Linha do tempo 1028 × 340) recebe a leitura completa em **duas colunas** (esquerda 540, direita 412,
  margens 24); painel pequeno (Ritmo 461 × 268, Avanço 461 × 468) recebe a **versão condensada** (margens 18): achado
  e destaques sempre, explicação mais curta, "o que explica" / "detalhe" / "como ler" só se couberem. Achado desce
  de 30 para 22 (grandes) ou 20 (pequenos); explicação 14 / 19 ou 13,5 / 18; destaques com número 22 ou 20 e rótulo
  13 / 17; piso 13 em tudo. Só o **Guia** (`Guia · T3`, "?" redondo do cabeçalho) continua cobrindo a tela com véu.
- **Tooltips com cantos quadrados** (raio 0 só no cartão e no cabeçalho preto; chips e selos mantêm o raio da tela,
  4 e 3, como na §1.6 da linguagem comum), **mini gráfico
  objetivo** (uma série, sem eixo, grade ou legenda; rótulo de valor só no mês do ponto e no primeiro mês da série,
  para dar o "de → até"; altura só a que a leitura pede) e **rodapé em uma linha de até ~70 caracteres** — ou
  nenhum, quando repetiria o que está acima. As alturas caíram para 185–322.
- **Mês dos tooltips de exemplo ≠ jun/26.** Os pontos de jun/26 já têm rótulo na tela (28,0 % previsto · 24,1 %
  executado · −3,9 p.p.; 2,30 % no ritmo). Para o tooltip "nunca repetir o número visível", o estado completo da curva S
  é **mai/26** e o do ritmo é **mar/26**; o exemplo montado aponta o ponto de maio. A página de tooltip é a mesma para
  qualquer mês.
- **Dois tooltips de mês com focos diferentes.** Curva S = acumulado em destaque + o mês como detalhe + crédito ×
  desembolsado até o mês (físico contra financeiro acumulado). Ritmo = o mês em destaque (previsto × executado), o
  acumulado em uma linha, **dinheiro do mês** (previsto × desembolsado, com a faixa) e a **justificativa da planilha**
  (texto da G140) — é onde o leitor descobre por que gastou mais e produziu menos.
- **Dois tooltips de obra com focos diferentes.** Linha do tempo = ficha de prazo (início · término · orçamento com o
  tipo), físico × financeiro até o mês e o status da obra; Avanço das sete = o mês e a **série do desvio acumulado**
  (barras a partir de uma linha-base invisível, status na cor) + o que mudou desde o mês anterior em uma linha.
- **Série do desvio (tooltip do avanço).** Toda negativa: meses no alto, barras pendem da linha-base (19 px abaixo
  dos meses), rótulo embaixo da barra. Mista ou toda positiva: linha-base a 57 px, positivos sobem (teto 40), negativos
  descem (teto 16), meses no pé. Escala 10 px por p.p., teto 40 px (POTENGI em jan/26, +8,06, bateria no teto — o rótulo
  continua certo). Meses sem aba aparecem só como rótulo a 35 %.
- **Obras a iniciar (cronograma).** Não têm `fonte` no JSON; levam o selo tracejado `cronograma` no cabeçalho do tooltip (mesma
  peça do `ILUSTR.`, texto diferente). O selo de origem da tela não as menciona; registrado na §7.
- **Leituras da carteira sem conta nova.** "Cinco das sete atrás", "três quartos executados", "entre R$ 20 mi e
  R$ 26 mi", "atrás desde fevereiro" são contagens, arredondamentos e comparações de sinal sobre campos existentes;
  nada de subtração ou soma que não esteja no JSON (o que faltou está na §7).
- **Trajetória em vez de números no detalhe das sete obras** (L058): sete linhas "obra · desde quando está atrás /
  à frente e quando mudou de faixa" — tudo por `obras[].serie[].indicadores.desvio_fisico_pp` (sinal) e
  `indicadores_status.desvio_fisico_pp`.
- **Guia com a régua do desvio físico** (não a de pontos): é a régua que a tela usa; a nota do fim remete a
  pontuação completa à Visão geral.
- **Avisos de qualidade da planilha não entram** em nenhuma peça (regra do projeto), mesmo onde explicariam um
  salto (CAJUEIRO +4,1 p.p. em maio vem de um previsto que regrediu).

---

## 2. Versos · Tela 03 (`Fileira · Versos`, cópias de `Base · Verso` `291:1149`)

Gatilho: hover (ou foco) no cartão. Texto fixo; só a régua lê `meta.regras_criticidade.desvio_fisico_pp`.

| Componente · id | Cartão (id) | Regra (`COMO É CALCULADO`) | `DE ONDE VEM` | Régua | Campos JSON |
|---|---|---|---|---|---|
| `Verso · T3 · Desvio físico acumulado` `306:10682` | `289:7408` | Executado acumulado menos previsto acumulado da obra, em pontos percentuais. | F37 − F35 da aba do mês | ■ < −3,0 · ▨ −3,0 a −1,0 · □ ≥ −1,0 p.p. | `ultimo.indicadores.desvio_fisico_pp`, `indicadores_status.desvio_fisico_pp`; régua `meta.regras_criticidade.desvio_fisico_pp` |
| `Verso · T3 · Executado acumulado` `306:10695` | `289:7409` | Quanto da obra já foi feito até o mês, em % do orçamento, pela medição do planejamento. | F37 da aba do mês | — | `ultimo.exec_acum` |
| `Verso · T3 · Previsto acumulado` `306:10700` | `289:7410` | Quanto o cronograma previa ter feito até o mês, em % do orçamento: é a curva S planejada. | F35 da aba do mês | — | `ultimo.prev_acum` |
| `Verso · T3 · No mês` `306:10705` | `289:7411` | Fatia da obra executada só neste mês, ao lado do que o cronograma previa para ele. | F33 e F31 da aba do mês | — | `ultimo.exec_mes`, `ultimo.prev_mes` |
| `Verso · T3 · Término previsto` `306:10710` | `289:7412` | Término do cronograma vigente; início e orçamento (com o tipo) vêm do cadastro da obra na cronograma. | cronograma · J28 e J29 da aba | — | `termino_previsto`, `inicio`, `orcamento`, `tipo_orcamento` |

Anatomia como na §1.5: regra de 2 linhas + régua (y 96) no primeiro; 3 linhas (ou 2) com origem em y 91 nos outros.
Início/término vêm do cadastro (`pipeline/montar_dados_mockup.py`, lista `CADASTRO`, âncora cronograma/Fluxo de Caixa) — não
há célula da Análise Crítica para eles; o tipo do orçamento é J29 e o valor J28.

**Animação (os 5 versos):** nenhum número conta — o verso explica, não repete; o único movimento é o flip (frente
sobe e verso entra, ~220 ms). Na **frente** dos cartões, ao abrir a página: os cinco valores contam do zero
(−3,9 p.p. · 24,1% · 28,0% · 2,30% com o 3,33% da sublinha · nada no "ago/28", que é data); sem barras nem linhas.

---

## 3. Tooltips · Tela 03 (`Fileira · Tooltips`, componentes 480 de largura, raio 0, borda 1 px preta, sombra 0/8/24/18 %)

Cabeçalho preto 54 px (raio 0) com sobretítulo, título, código, selo (raio 3, como na tela) e contexto à direita;
chips com raio 4; corpo offwhite;
margem 18; larguras úteis conferidas (≤ 444 px por linha); **alturas 185–322**; o último bloco é sempre **uma linha de
até ~70 caracteres** ou não existe.

### 3.1 `Tooltip · T3 · Mês da curva` (`313:3804`, 480 × 289) — estado `· primeiro mês` (`313:3842`, 480 × 237)
**Gatilho:** hover num ponto (ou na coluna) de "Curva S" (`289:7413`). **Ponto:** o mês. Obra = a em foco.

| Bloco | Modelo (REDINHA, mai/26) | Variações | Campos |
|---|---|---|---|
| Sobretítulo | `CURVA S · {OBRA} · ABA {aba}` | `+ · PRIMEIRO MÊS DO HISTÓRICO` no 1.º mês da `serie` | `serie[m].aba` |
| Título · contexto | "maio de 2026" · `INÍCIO ABR/25 · TÉRMINO AGO/28` | mês por extenso | `serie[m].mes`, `inicio`, `termino_previsto` |
| Três colunas | `PREVISTO ACUMULADO` 24,7% · `EXECUTADO ACUMULADO` 21,8% · `DESVIO · ATENÇÃO` ▨ −2,9 p.p. | versalete da 3.ª coluna = faixa do físico no mês (`ESTÁVEL`/`ATENÇÃO`/`CRÍTICO`); marca pela régua | `serie[m].prev_acum`, `.exec_acum`, `.indicadores.desvio_fisico_pp`, `.indicadores_status.desvio_fisico_pp` |
| `NO MÊS` | `Previsto` 3,20% · `Executado` 2,09% · "o mês mais fraco do semestre" | detalhe = posição do mês na série: "o mês mais fraco / o melhor mês do semestre", "o maior / menor previsto do semestre"; sem destaque: some | `serie[m].prev_mes`, `.exec_mes` (mín/máx da `serie`) |
| `CRÉDITO × DESEMBOLSO ATÉ {MÊS}` | `Crédito do executado` R$ 4,90 mi · `Desembolsado` R$ 5,43 mi | só os dois números (a frase interpretativa saiu: repetia a comparação) | `serie[m].credito`, `.desembolsado_acum` |
| `DESDE {MÊS ANTERIOR}` (uma linha) | "Era −1,8 p.p. em abril; terceiro mês seguido em atenção." | `Era {desvio m−1} em {mês}; {n}.º mês seguido em {faixa}.` / `…; passou de {faixa} a {faixa}.`; **1.º mês: bloco some** | `serie[m−1].indicadores.desvio_fisico_pp`, `indicadores_status` |

Estado `· primeiro mês` (jan/26): 12,8% · 12,2% · □ −0,6 p.p. estável · 2,49% × 2,18% ("o menor previsto do
semestre") · R$ 2,71 mi × R$ 2,74 mi; termina aí (o sobretítulo já diz que é o primeiro mês).
Mês sem aba (obra que abriu a planilha depois): o ponto não existe na curva, logo não há tooltip. Mês sem previsto
(F35 vazio): coluna `PREVISTO ACUMULADO` e `DESVIO` somem, a linha `NO MÊS` mostra só o executado.
**Animação:** contam os três números das colunas (previsto, executado, desvio) e os quatro valores das linhas
(previsto/executado do mês, crédito, desembolsado); sem barras nem linhas.

### 3.2 `Tooltip · T3 · Mês do ritmo` (`313:3876`, 480 × 293) — estado `· mobilização` (`313:3913`, 480 × 293)
**Gatilho:** hover num par de colunas de "Ritmo do mês" (`289:7421`). **Ponto:** o mês.

| Bloco | Modelo (REDINHA, mar/26) | Variações | Campos |
|---|---|---|---|
| Sobretítulo · contexto | `RITMO DO MÊS · REDINHA · ABA MAR26` · `ORÇAMENTO DO MÊS R$ 22,32 MI` | `+ · EM MOBILIZAÇÃO`; o orçamento é o da aba do mês (muda com o INCC) | `serie[m].aba`, `.orcamento`, `.mobilizacao` |
| Três colunas | `PREVISTO PARA O MÊS` 2,89% · `EXECUTADO NO MÊS` 2,24% · `AO FIM DO MÊS · ATENÇÃO` ▨ −1,4 p.p. | faixa do físico ao fim do mês | `serie[m].prev_mes`, `.exec_mes`, `.indicadores.desvio_fisico_pp` |
| Linha do acumulado (uma linha) | "Acumulado ao fim de março: 18,4% previsto × 17,0% executado." | — | `serie[m].prev_acum`, `.exec_acum` |
| `DINHEIRO DO MÊS` | `Previsto` R$ 384 mil · `Desembolsado` R$ 473 mil · ▨ +23% atenção | marca e rótulo pela faixa do desembolso | `serie[m].previsto_mes_rs`, `.desembolsado_mes_rs`, `.indicadores.desvio_desembolso`, `.indicadores_status.desvio_desembolso` |
| `JUSTIFICATIVA NA PLANILHA` (uma linha, itálico) | *Aditivo de serviço não previsto no orçamento (contenção).* | vazia e não exigida: "Nenhuma — não exigida (desvio dentro de ±10%)."; vazia e exigida: "Em branco — exigida acima de ±10%." | `serie[m].justificativa`, `ultimo.justificativa_exigida` (só há no último mês; ver §7) |
| `DESDE {MÊS ANTERIOR}` (uma linha) | "Era 2,57% em fevereiro: o executado caiu e o previsto subiu." | `Era {exec m−1} em {mês}: o executado {caiu/subiu} e o previsto {subiu/caiu}.`; 1.º mês: bloco some | `serie[m−1].exec_mes`, `.prev_mes` |

Estado `· mobilização` (TIROL, jun/26): 2,13% · 1,52% · ▨ −1,4 p.p. · "Acumulado ao fim de junho: 5,0% previsto ×
3,6% executado." · R$ 333 mil × R$ 463 mil · ■ +39% crítico · *Aumento de efetivo para recuperar o cronograma.* ·
`DESDE MAIO · E A TRAVA DA MOBILIZAÇÃO`: "Era −0,8 p.p. em maio; em mobilização, o status trava em atenção (49)."
**Animação:** contam os três números das colunas e os três do dinheiro (previsto, desembolsado, +23%); sem barras.

### 3.3 `Tooltip · T3 · Obra na linha do tempo` (`313:3949`, 480 × 286) — estados `· a iniciar` (`313:3989`, 480 × 185) e `· mobilização` (`313:4013`, 480 × 286)
**Gatilho:** hover numa barra de "Linha do tempo das obras" (`289:7417`). **Ponto:** a obra (em andamento ou a iniciar).

| Bloco | Modelo (REDINHA) | Variações | Campos |
|---|---|---|---|
| Sobretítulo | `LINHA DO TEMPO · OBRA EM ANDAMENTO · ABA JUN26` | a iniciar: `LINHA DO TEMPO · OBRA A INICIAR · cronograma ABR/26`; `+ · EM MOBILIZAÇÃO` | `ultimo.aba`, `ultimo.mobilizacao`; `proximas[]` |
| Título · selo · contexto | `REDINHA` `AT` `ILUSTR.` · `CONSTRUTORA-05 SPE · 7.190 M² NBR` | selo `REAL` quando `fonte = "real"`; a iniciar: selo `cronograma` e só `{m2} M² NBR`; SPE abreviada (prefixo `CONSTRUTORA-xx`) | `obra`, `codigo`, `fonte`, `spe`, `m2_nbr` |
| Três colunas | `INÍCIO` abr/25 · `TÉRMINO PREVISTO` ago/28 · `ORÇAMENTO · PRELIMINAR` R$ 19,84 mi | a iniciar: `INÍCIO PREVISTO` jul/26 · ago/29 · `ORÇAMENTO · LEGAL` R$ 41,70 mi | `inicio`, `termino_previsto`, `orcamento`, `tipo_orcamento` / `proximas[].inicio_previsto`, `.termino_previsto`, `.orcamento_crono`, `.tipo_orcamento` |
| `FÍSICO × FINANCEIRO ATÉ JUN/26` | `Executado` 24,1% · `Previsto` 28,0% · ■ −3,9 p.p. crítico / `Crédito do executado` R$ 5,44 mi · `Desembolsado` R$ 6,06 mi | a iniciar: bloco vira `AINDA SEM PLANILHA ANÁLISE CRÍTICA` + uma linha "Previsto, executado e status chegam com a primeira aba da obra." | `ultimo.exec_acum`, `.prev_acum`, `.indicadores.desvio_fisico_pp`, `.credito`, `serie[-1].desembolsado_acum` |
| `STATUS DA OBRA EM JUN/26` | chip `CRÍTICO` · 72,5 pontos · "crítica desde abril" + uma linha "Físico crítico em junho; desembolso crítico desde abril." | "{status} desde {mês}" = 1.º mês da sequência atual de `serie[].status`; a linha = sinais críticos e desde quando; mobilização: marca tracejada antes dos pontos, "em mobilização desde {aba}" e "Em mobilização o status trava em atenção; pela régua somaria {score_bruto}."; estável: chip `ESTÁVEL` · 0 pontos · "estável desde {mês}", sem linha | `ultimo.status`, `.score`, `.score_bruto`, `serie[].status`, `serie[].indicadores_status` |

Estado `· mobilização` (TIROL): fev/26 · jan/29 · `ORÇAMENTO · LEGAL` R$ 25,62 mi · 3,6% × 5,0% ▨ −1,4 p.p. atenção ·
R$ 922 mil × R$ 1,12 mi · chip `ATENÇÃO` ⬚ 49 pontos "em mobilização desde mar/26" · "Em mobilização o status trava em
atenção; pela régua somaria 77,5."
**Animação:** contam o orçamento (R$ 22,55 mi), os dois percentuais, o desvio, crédito, desembolsado e os pontos;
datas não contam; sem barras.

### 3.4 `Tooltip · T3 · Obra no avanço` (`313:4056`, 480 × 291) — estados `· adiantada` (`313:4103`, 480 × 322) e `· mobilização` (`313:4149`, 480 × 266)
**Gatilho:** hover numa linha de "Avanço das sete obras" (`289:7425`). **Ponto:** a obra.

| Bloco | Modelo (REDINHA) | Variações | Campos |
|---|---|---|---|
| Cabeçalho | `AVANÇO FÍSICO · JUN/26 · ABA JUN26` · `REDINHA` `AT` `ILUSTR.` · `INÍCIO ABR/25 · TÉRMINO AGO/28` | `+ · EM MOBILIZAÇÃO`; selo `REAL` | `ultimo.aba`, `obra`, `codigo`, `fonte`, `inicio`, `termino_previsto` |
| `NO MÊS · JUN/26` | `Previsto` 3,33% · `Executado` 2,30% · "o maior previsto do semestre" | detalhe: extremo da série ("o maior previsto / o mês mais fraco…"), "acima do previsto" quando exec > prev, "abaixo do previsto desde {aba}" quando foi assim em toda a série; senão some | `ultimo.prev_mes`, `.exec_mes`, `serie[]` |
| `DESVIO ACUMULADO, MÊS A MÊS · P.P.` | 6 barras jan–jun (creme · creme · hachura · hachura · hachura · preto), **sem eixo nem legenda**; rótulo Barlow 14 só em **jun** (o mês do ponto, Semibold) e em **jan** (o primeiro da série, Medium grafite): −0,6 e −3,9 | sentido e linha-base pela §1; mês sem aba = rótulo a 35 % sem barra; o primeiro mês rotulado é o primeiro **com aba** | `serie[].indicadores.desvio_fisico_pp`, `.indicadores_status.desvio_fisico_pp`, `serie[].aba` |
| `O QUE MUDOU DESDE {MÊS ANTERIOR}` (uma linha) | "Passou de atenção a crítico; o atraso cresce todo mês desde janeiro." | "Passou de {faixa} a {faixa}" (de `mudancas_desde_mes_anterior`) ou "Nada mudou: {faixa} nos {n} meses"; "; o atraso cresce todo mês desde {mês}" / "; à frente desde {mês}"; mobilização: título `DESDE {MÊS} · E A TRAVA DA MOBILIZAÇÃO` + "De {faixa} a {faixa}; em mobilização, o status trava em atenção."; 1.º mês: bloco some | `ultimo.mudancas_desde_mes_anterior`, `serie[]` |

Estado `· adiantada` (CAJUEIRO, `REAL`): 3,09% × 3,31% "acima do previsto"; série −0,2 · +0,9 · +0,1 · +0,1 · +4,1 · +4,3
(toda creme; linha-base a 57 px, rótulos em jan e jun); "Nada mudou: estável nos seis meses; à frente desde fevereiro."
Estado `· mobilização` (TIROL): 2,13% × 1,52% "abaixo do previsto desde mar/26"; jan e fev sem barra; −0,1 · −0,5 ·
−0,8 · −1,4 (a última hachura; rótulos em mar e jun); "De estável a atenção; em mobilização, o status trava em atenção."
**Animação:** contam os dois números do mês e os dois rótulos do gráfico; as seis barras **correm** em sequência de
jan a jun (cada uma cresce do zero a partir da linha-base, ~120 ms entre elas), a de jun por último com o rótulo
entrando junto; sem linhas.

---

## 4. Leituras · Tela 03 (`Fileira · Leituras e guia`; L065: cada uma na geometria do seu painel)

Gramática da §1.7; cada número aparece uma vez por leitura (L058) — conferido bloco a bloco depois da condensação.
Curva S e Ritmo leem a obra em foco; Avanço e Linha do tempo leem a carteira (não mudam com a obra, só com o mês).
Geometria = retângulo do `Painel · <nome>` no canvas 1920 × 1080 (prancheta em 300, 12 + painel na prancheta).

| Leitura · id | Painel (id) | **x · y · w · h (canvas)** | Tamanho | O que ficou | O que saiu / encolheu |
|---|---|---|---|---|---|
| `Leitura · T3 · Curva S` `317:5115` | `289:7413` | **352 · 282 · 1028 × 402** | grande, 2 colunas | sobretítulo · achado (22/28) · explicação (14/19) · destaques (22 + 13/17) · como ler (13/17) na coluna esquerda; o que explica (13/17) + detalhe (barras penduradas, 16 px/p.p., limites −1,0 e −3,0) na direita | pílula "Fechar"; como ler mais curto (3 linhas); rótulos dos destaques encurtados para 2 linhas |
| `Leitura · T3 · Ritmo do mês` `317:5158` | `289:7421` | **1400 · 282 · 461 × 268** | pequeno, condensado | sobretítulo · achado (20/26, 2 linhas) · explicação curta (13,5/18, 3 linhas) · destaques (20 + 13/17) | o que explica, detalhe (desembolso × justificativa mês a mês), como ler e pílula — o detalhe e o como-ler sobrevivem no tooltip do ritmo e no guia |
| `Leitura · T3 · Avanço das sete obras` `317:5214` | `289:7425` | **1400 · 550 · 461 × 468** | pequeno, condensado | sobretítulo · achado (20/26, 3 linhas) · explicação curta (13,5/18, 3 linhas) · destaques (20 + 13/17) · detalhe "trajetória do físico" (7 linhas, 13/18) | o que explica (o peso proporcional e a fase viraram meia frase da explicação), como ler, pílula; frases da trajetória encurtadas (meses abreviados) |
| `Leitura · T3 · Linha do tempo das obras` `317:5261` | `289:7417` | **352 · 688 · 1028 × 340** | grande, 2 colunas | sobretítulo · achado (22/28) · explicação (14/19, 4 linhas) · destaques (22 + 13/17) na esquerda; o que explica (13/17) + detalhe (tabela das quatro a iniciar, 4 × 20) na direita | como ler (não coube: 2 linhas estouravam o limite) e pílula; explicação sem a última frase ("É a fase da obra…"); rótulos dos destaques encurtados |

Na seção, as leituras estão em x 0 · 1068 · 1569 · 2070 (y 80); `Guia · T3` em 3138. No Power BI: marcador de
exibição que liga o HTML Content **exatamente sobre o painel** (mesmo x, y, w, h do visual do gráfico + título) e um
botão transparente de 32 × 32 no canto superior direito com a ação de fechar; clicar fora = o mesmo marcador "normal".

### 4.1 `Leitura · T3 · Curva S` (`317:5115`, 352 · 282 · 1028 × 402) — "?" `289:7414`
| Bloco | Texto (REDINHA, jun/26) | Modelo e variações | Campos |
|---|---|---|---|
| Sobretítulo | `LEITURA · CURVA S · REDINHA · JUNHO DE 2026` | obra em foco + mês por extenso | `obra`, `carteira.mes_ref` |
| Achado | "A REDINHA fecha junho 3,9 p.p. atrás do cronograma, e a distância cresce todo mês desde janeiro." | `{obra} fecha {mês} {|desvio|} p.p. {atrás do / à frente do} cronograma` + `, e a distância {cresce todo mês desde {mês} / vem caindo desde {mês} / oscila desde {mês}}` (sequência de sinal da diferença entre desvios consecutivos); desvio na faixa estável: "…fecha {mês} no ritmo do cronograma ({desvio} p.p.)." | `ultimo.indicadores.desvio_fisico_pp`, `serie[].indicadores.desvio_fisico_pp` |
| Explicação | "A obra executa menos do que o previsto desde o primeiro mês do histórico. O cronograma pede um ritmo que acelera a cada mês e a execução não acompanhou: nem no melhor mês do semestre, abril, ela alcançou o previsto. O físico saiu da faixa estável em março, ficou três meses em atenção e em junho virou crítico — o sinal de maior peso entre os que levaram a obra à faixa crítica." | 1.ª frase: "executa menos/mais do que o previsto desde {mês}" (sinal de `exec_mes − prev_mes` — só o sinal, sem o número); 2.ª: "o cronograma pede um ritmo que {acelera / é constante / desacelera}" (`prev_mes` crescente?) + "nem no melhor mês, {mês}, alcançou o previsto" quando nenhum `exec_mes ≥ prev_mes`; 3.ª: trajetória da faixa (`indicadores_status.desvio_fisico_pp` por mês) + "o sinal de maior peso entre os que levaram a obra à faixa {status}" quando o físico é o sinal crítico de maior peso em `sinais`; obra estável: "O físico nunca saiu da faixa estável no semestre." | `serie[]`, `ultimo.sinais` |
| Destaques | `−0,6 p.p.` desvio em janeiro, ainda na faixa estável · `2,09%` executado em maio, o mês mais fraco · `R$ 6,06 mi` pagos até junho; R$ 5,44 mi de obra executada | 1: desvio do 1.º mês da série + faixa; 2: mín. de `exec_mes` e o mês; 3: `desembolsado_acum` × `credito` do último mês | `serie[0].indicadores.desvio_fisico_pp`, `serie[].exec_mes`, `serie[-1].desembolsado_acum`, `ultimo.credito` |
| O que explica | "Pela planilha, o gasto acima do previsto foi justificado em três meses como aumento de efetivo para recuperar o cronograma e em dois como aditivo de contenção não previsto no orçamento: a obra está pagando para correr atrás do prazo, e o executado ainda não reflete isso. A diferença entre o desembolsado e o que a obra credita pelo executado é o custo desse atraso." | contagem das `justificativa` iguais na série (em palavras); sem justificativas: "A planilha não traz justificativa para o desembolso acima do previsto em nenhum mês."; desembolso dentro do previsto: "O desembolso acompanhou o previsto; o atraso não veio de falta de dinheiro." | `serie[].justificativa`, `serie[].indicadores.desvio_desembolso` |
| Detalhe | "desvio acumulado do físico, mês a mês · p.p." — 6 barras penduradas (16 px por p.p., 30 de largura), status na cor, linhas tracejadas em −1,0 ("−1,0 · atenção") e −3,0 ("−3,0 · crítico"); **sem rótulo de valor** | obra adiantada: barras sobem; mês sem aba: coluna vazia | `serie[].indicadores.desvio_fisico_pp`, `.indicadores_status` |
| Como ler | "Tracejado = previsto acumulado; sólido = executado; a área entre eles é o atraso, em % do orçamento. Régua do físico: até −1,0 p.p. estável; de −1,0 a −3,0, atenção; abaixo de −3,0, crítico (25 dos 100 pontos). Mouse num mês: acumulado, ritmo e dinheiro do mês." | fixo; lê `meta` | `meta.regras_criticidade.desvio_fisico_pp` |

**Animação:** conta o 3,9 do achado e os três destaques (−0,6 · 2,09% · R$ 6,06 mi com o R$ 5,44 mi); as seis
barras do detalhe correm de jan a jun; no painel por baixo, ao abrir a página, a curva do executado e a tracejada do
previsto se desenham da esquerda para a direita (previsto primeiro) e os rótulos finais contam.

### 4.2 `Leitura · T3 · Ritmo do mês` (`317:5158`, 1400 · 282 · 461 × 268) — "?" `289:7422`
| Bloco | Texto | Modelo e variações | Campos |
|---|---|---|---|
| Achado | "Em junho a REDINHA executou 2,30% da obra; o cronograma pedia 3,33%, o maior do semestre." | `Em {mês} a {obra} executou {exec_mes} da obra; o cronograma pedia {prev_mes}` + `, o maior/menor do semestre` só se for extremo; executou acima: "…e o cronograma pedia só {prev_mes}." | `ultimo.exec_mes`, `.prev_mes`, `serie[].prev_mes` |
| Explicação (curta) | "Nenhum mês alcançou o previsto: o cronograma acelera a cada mês e o executado oscila no mesmo patamar — o descompasso que levou o físico à faixa crítica." | "Nenhum mês alcançou o previsto" / "{n} dos {m} meses alcançaram o previsto"; "o cronograma acelera" (monótono) / "é estável"; "o executado oscila" (sinal alternado) / "cresce"; fecho com a faixa do físico no mês | `serie[].prev_mes`, `.exec_mes`, `ultimo.indicadores_status.desvio_fisico_pp` |
| Destaques | `2,68%` executado em abril, melhor mês · `2,49%` o previsto de janeiro · `R$ 638 mil` pagos em junho; R$ 469 mil previstos | 1: máx. de `exec_mes`; 2: `prev_mes` do 1.º mês; 3: `desembolsado_mes_rs` × `previsto_mes_rs` do mês | `serie[]`, `ultimo.desembolsado_mes_rs`, `.previsto_mes_rs` |
| (saíram) | o que explica · detalhe (desembolso × previsto e justificativa, mês a mês) · como ler | o detalhe vive no tooltip do ritmo (§3.2) e no guia; se a tela crescer, voltam na ordem: como ler → detalhe → o que explica | — |

**Animação:** contam 2,30% e 3,33% no achado e os três destaques; no painel por baixo, as doze colunas correm em
pares (previsto creme, depois executado preto) de jan a jun.

### 4.3 `Leitura · T3 · Avanço das sete obras` (`317:5214`, 1400 · 550 · 461 × 468) — "?" `289:7426`
| Bloco | Texto (carteira, jun/26) | Modelo e variações | Campos |
|---|---|---|---|
| Achado | "Cinco das sete obras estão atrás do cronograma, quatro fora da faixa estável; a carteira fecha junho 0,5 p.p. abaixo do previsto." | `{n} das {total} obras estão atrás do cronograma` (desvio < 0) `, {k} fora da faixa estável` (status ≥ 1) `; a carteira fecha {mês} {|desvio|} p.p. {abaixo/acima} do previsto.` · nenhuma atrás: "Nenhuma obra está atrás do cronograma…" | `obras[].ultimo.indicadores.desvio_fisico_pp`, `.indicadores_status.desvio_fisico_pp`, `carteira.desvio_fisico_pp`, `carteira.obras_em_andamento` |
| Explicação (curta) | "O atraso que pesa está em REDINHA, crítica, e POTENGI, que atrasa perto do fim; TIROL e JANGADA, no começo, estão pouco atrás. CAJUEIRO e DUNAS, à frente, seguram a carteira na faixa estável." | obras com status ≥ 1 ordenadas pelo desvio, com a fase em palavras ("perto do fim" ≥ 70 % executado, "no começo" < 25 %); obras com desvio ≥ 0 como contrapeso; fecho pela faixa de `carteira.desvio_fisico_pp` | `obras[].ultimo.exec_acum`, `.status`, `.indicadores`, `carteira.desvio_fisico_pp` |
| Destaques | `45,2%` executado × 45,7% previsto · `+4,3 p.p.` CAJUEIRO, a obra mais adiantada · `3,6%` TIROL, em mobilização | 1: `carteira.exec_acum_ponderado` × `prev_acum_ponderado`; 2: máx. do desvio e a obra; 3: obra em mobilização (se nenhuma: mín. de `exec_acum`, "a obra mais no começo") | `carteira.*`, `obras[].ultimo.*` |
| Detalhe `TRAJETÓRIA DO FÍSICO NO SEMESTRE` | marca · obra · frase: REDINHA "atrás desde jan; atenção em mar, crítica em jun" · POTENGI "atrás desde fev; atenção desde abr" · TIROL "atrás desde a 1.ª aba, mar; atenção em jun" · JANGADA "atrás desde jan; atenção desde mai" · CAJUEIRO "atrás em jan; à frente desde fev" · DUNAS "à frente nos seis meses" · PONTA NEGRA "pouco atrás, sempre estável; termina em jun" | frases por sinal do desvio ("atrás"/"à frente") e por mudança de `indicadores_status.desvio_fisico_pp`; "termina em {mês}" quando `termino_previsto` = mês de referência; "desde a 1.ª aba, {mês}" quando a série começa depois do 1.º mês; meses abreviados (3 letras) | `obras[].serie[].indicadores.desvio_fisico_pp`, `.indicadores_status`, `.mobilizacao`, `termino_previsto` |
| (saíram) | o que explica (o peso proporcional ao orçamento e a leitura por fase) · como ler (régua e "clique para colocar em foco") | voltam se a tela crescer; o como-ler está no guia (item 4) | — |

**Animação:** conta o 0,5 do achado e os três destaques; as sete linhas do detalhe entram de cima para baixo (fade,
~80 ms entre elas); no painel por baixo, as sete barras de executado correm de cima para baixo e os sete desvios
contam.

### 4.4 `Leitura · T3 · Linha do tempo das obras` (`317:5261`, 352 · 688 · 1028 × 340) — "?" `289:7418`
| Bloco | Texto | Modelo e variações | Campos |
|---|---|---|---|
| Achado | "Sete obras em andamento e quatro a entrar ainda em 2026; a PONTA NEGRA, a mais antiga, termina agora em junho." | `{n} obras em andamento e {k} a entrar {ainda em {ano} / até {mês/ano}}` + `; a {obra}, a mais antiga, termina agora em {mês}` só quando alguma `termino_previsto` = mês de referência (senão: "; a próxima a terminar é a {obra}, em {mês/ano}.") | `carteira.obras_em_andamento`, `proximas[]`, `obras[].inicio`, `.termino_previsto` |
| Explicação | "O canteiro está em transição: a obra mais antiga chega ao fim no mês de referência e as mais novas mal começaram — JANGADA, TIROL e, em seguida, as quatro da cronograma. A POTENGI se aproxima do término, no começo de 2027, com atraso; REDINHA, JANGADA e TIROL só terminam em 2028 e 2029 e já acumulam atraso cedo." | obras ordenadas por `inicio`; "mal começaram" = `exec_acum` < 25 %; "se aproxima do término … com atraso" = `exec_acum` ≥ 70 % e desvio < 0; "já acumulam atraso cedo" = desvio < 0 com término a 2+ anos | `obras[].inicio`, `.termino_previsto`, `.ultimo.exec_acum`, `.ultimo.indicadores.desvio_fisico_pp` |
| Destaques | `set/23` início da PONTA NEGRA, a mais antiga · `jan/29` TIROL, o término mais distante · `R$ 26,10 mi` DUNAS, o maior orçamento das sete | 1: mín. de `inicio`; 2: máx. de `termino_previsto`; 3: máx. de `orcamento` | `obras[]` |
| O que explica | "As obras a iniciar entram com o orçamento legal da cronograma e só ganham previsto, executado e desembolso na primeira aba da Análise Crítica — por isso aparecem tracejadas, sem avanço. Entre as sete em andamento, o tipo de orçamento acompanha a fase: executivo nas mais maduras (PONTA NEGRA e DUNAS), preliminar na maioria, legal na TIROL, que acabou de começar." | agrupa `tipo_orcamento` (executivo / preliminar / legal / alvo) e nomeia as obras de cada grupo | `obras[].tipo_orcamento`, `proximas[].tipo_orcamento` |
| Detalhe `AS QUATRO A INICIAR · cronograma ABR/26` | ⬚ uma linha por obra a iniciar: nome, código, início → término, orçamento legal e m² (ex.: "CANDELÁRIA · jul/26 → ago/29", nome ilustrativo) | código "—" vira "sem código"; sem obras a iniciar: "Nenhuma obra a iniciar na cronograma de {mês}." | `proximas[]` |
| (saiu) | como ler ("barra do início ao término; preenchido = executado, traço = previsto, cor pela régua; tracejado = a iniciar") | está no guia (item 5); volta se a tela crescer | — |

**Animação:** conta o R$ 26,10 mi dos destaques (datas não contam) e os quatro orçamentos da tabela; as quatro linhas
da tabela entram de cima para baixo; no painel por baixo, as onze barras de prazo se desenham da esquerda para a
direita (do início ao término, de cima para baixo) e, nas sete em andamento, o preenchimento do executado corre em
seguida.

---

## 5. `Guia · T3` (`317:5308`, 760 × 934) — "?" `277:1078` (`Ajuda · Guia da página`)
Como está: véu 55 % na tela inteira + marcadores + painel em x 400 (centrado na vertical, y 73). Introdução: "A tela
responde em dois planos: em cima, a obra em foco — os cartões e a curva S dizem se ela está no ritmo e desde quando
não está; embaixo e à direita, a carteira — quem está à frente, quem está atrás e o que entra no canteiro."
1. **Cartões da obra** — Cinco números da obra em foco; o escuro, o desvio físico acumulado, é a resposta da pergunta. Passe o mouse: o cartão vira e mostra como é calculado e de onde vem.
2. **Curva S** — Previsto (tracejado) e executado (sólido) acumulados, mês a mês; a área entre as linhas é o atraso. Passe o mouse num mês para ver o acumulado, o ritmo e o dinheiro daquele mês.
3. **Ritmo do mês** — O que o cronograma pedia e o que a obra fez em cada mês, em % do orçamento. Passe o mouse para ver o previsto do mês, o acumulado e a justificativa da planilha.
4. **Avanço das sete obras** — Executado e previsto de cada obra, com o desvio e a marca da régua; a obra em foco vem destacada. Passe o mouse para ver o desvio mês a mês; clique numa obra para trocar o foco.
5. **Linha do tempo das obras** — Início e término previsto das sete obras e das quatro a entrar, tracejadas, com orçamento legal da cronograma; a linha vertical é o mês de referência. Passe o mouse numa obra para ver prazo, orçamento e físico contra financeiro.
6. **Filtro e ajuda** — O topo mostra a obra e o mês em uso. O funil abre os filtros; o "?" redondo abre este guia; o "?" de cada painel abre a leitura daquele gráfico.
7. **Navegação** — Visão geral · Análise crítica · Avanço físico · Resultado no tempo. A obra e o mês escolhidos valem para todas as folhas.
`A RÉGUA DO DESVIO FÍSICO`: ■ crítico · abaixo de −3,0 p.p. ▨ atenção · −3,0 a −1,0 p.p. □ estável · −1,0 p.p. ou mais ⬚
mobilização · menos de 10% executado: a obra fica, no máximo, em atenção. Nota: "O desvio físico vale 25 dos 100 pontos
da criticidade da obra; a pontuação completa e os outros quatro sinais estão na Visão geral."
Marcadores (canvas 1920): 1 (338, 130) cartões · 2 (338, 268) curva S · 3 (1386, 268) ritmo · 4 (1386, 536) avanço ·
5 (338, 674) linha do tempo · 6 (1452, 44) filtro/ajuda · 7 (14, 218) navegação.

O item 4 assume o **clique na linha do avanço como troca da obra em foco** (cross-filter nativo do Power BI sobre a
obra); se a obra for só pelo filtro da gaveta, tirar "clique numa obra para trocar o foco" do guia.
**Animação:** nenhuma no guia (texto); os marcadores numerados entram em sequência 1 → 7 (~100 ms).

---

## 6. Exemplos montados (fileira 1)
`Exemplo · T3 · Cartão virando` `318:6304` (frame `flip · meio do gesto` `318:6603` na coluna 1: clone da frente do cartão
escuro a −66 px + instância do verso a +54 px + dobra 35 % + cursor) · `Exemplo · T3 · Tooltip apontando` `318:6627`
(cursor no ponto executado de mai/26 da curva S, em (1090, 464); tooltip em cursor + 16) · `Exemplo · T3 · Leitura
aberta` `318:6959` (**sem véu**: `Leitura · T3 · Curva S` em (352, 282), o resto da tela visível) · `Exemplo · T3 · Guia
aberto` `318:7302` (véu + 7 marcadores + `Guia · T3` em (400, 73)). Instância da tela atualizada: `306:3543`.

---

## 7. Números: origem e o que falta no JSON

**Conferidos (caminho no JSON):** `obras[REDINHA].ultimo` (24,1 / 28,0 %, −3,9 p.p., 3,33 / 2,30 %, R$ 22,55 mi, abr/25,
ago/28, 72,5, crédito 5.435.297 → R$ 5,44 mi, justificativa) e `serie[]` (prev/exec do mês e acumulados, desvios −0,6 ·
−0,73 · −1,37 · −1,76 · −2,87 · −3,9, status 0·0·1·1·1·2, `credito`, `desembolsado_acum` 6.063.352 → R$ 6,06 mi,
`previsto_mes_rs` / `desembolsado_mes_rs`, `desvio_desembolso` 0,18 · 0,164 · 0,231 · 0,261 · 0,267 · 0,36 com status
1·1·1·2·2·2, `orcamento` de mar/26 22.323.058 → R$ 22,32 mi, abas JAN26 / MAR26 / MAIO26); `obras[TIROL]` (fev/26 → jan/29,
legal, R$ 27,15 mi, 9.120 m², série mar–jun −0,08 · −0,31 · −0,66 · −1,1, mobilização, 49 / 77,5, aba MAR26, crédito
922.334, desembolsado 1.120.050); `obras[CAJUEIRO]` (real, out/24 → fev/28, 3,09 / 3,31 %, série −0,19 · +0,89 · +0,11 ·
+0,11 · +4,09 · +4,32); `obras[]` início/término/tipo/orçamento (DUNAS 26.104.300 máx., PONTA NEGRA 20.487.600 mín., set/23
mín. de início, jan/29 máx. de término); `proximas[]` (as obras a iniciar: códigos, m², orçamento legal, prazos);
`carteira` (45,16 / 45,70 %, −0,547 → "−0,5 p.p.", 7 obras); `meta.regras_criticidade.desvio_fisico_pp`, `meta.limites`.

**Comparações, contagens e arredondamentos feitos na escrita (sem conta nova):** "cinco das sete atrás" (desvio < 0),
"quatro fora da faixa" (status ≥ 1), "três quartos" (74,0 %), "cresce todo mês desde janeiro" (sequência de sinal),
"nenhum mês alcançou o previsto" (`exec_mes < prev_mes` nos seis), "o cronograma acelera" (monótono), "três meses
como aumento de efetivo, dois como aditivo" (textos iguais da `justificativa`), "terceiro mês seguido em atenção"
(contagem de status iguais).

**Faltam no JSON (acrescentar em `montar_dados_mockup.py` para a DAX não varrer a série nem calcular):**
- `serie[].desvio_mes_pp` = `exec_mes − prev_mes` (o "quanto faltou no mês"). Não foi usado: o tooltip do ritmo mostra
  previsto e executado lado a lado sem a diferença.
- `serie[].diferenca_credito_desembolso` = `desembolsado_acum − credito` ("o custo do atraso" citado em palavras na
  leitura da curva S, sem número).
- Datas derivadas por obra: `meses_decorridos`, `meses_restantes`, `duracao_meses`, `pct_prazo_decorrido`. Sem elas,
  nenhuma peça fala de "metade do prazo"; a linha do tempo só usa início e término.
- `proximas[].fonte` (cronograma real ou fictício) e `proximas[].spe` — o tooltip usa o selo `cronograma`; o selo de origem das telas
  não cita as obras a iniciar.
- `proximas_orcamento_total` (docs/04 cita R$ 147 mi; não há campo, não foi usado).
- `serie[].justificativa_exigida` / `justificativa_ausente` por mês (só existem em `ultimo`): o estado "em branco —
  exigida" do tooltip do ritmo depende disso para os meses anteriores.
- `serie[].tendencia_fisico` ("atrás desde {mês}", "cresce todo mês desde {mês}", "{n}.º mês seguido em {faixa}") e
  `obras[].fase` ("começo / meio / perto do fim") — hoje são comparações feitas à mão; um campo evita a DAX de janela.
- `carteira.serie[].obras_atrasadas` / `.obras_fora_da_faixa_fisico` (as contagens do achado da §4.3).
- `justificativa_tipo` (classificação dos textos de justificativa) para as contagens "três como aumento de efetivo".

**Número que não é do JSON e por isso não entrou:** nenhum.

---

## 8. O que fica diferente no Power BI
- **Leituras (L065):** um marcador de exibição por painel liga um HTML Content do tamanho exato do painel (x, y, w, h da
  §4) por cima do gráfico; sem retângulo de véu. O × é um botão transparente 32 × 32 no canto superior direito do
  HTML, com a ação do marcador "normal"; um botão transparente sobre o resto da página fecha também ("clicar fora").
  Não há pílula "Fechar". O "?" do painel (`Ajuda · <painel>`) continua sendo o botão que abre.
- **Tooltips:** páginas de tooltip 480 × (185–322) com fundo offwhite e **cantos retos** (sem raio no retângulo de
  fundo nem no cabeçalho); chips (raio 4) e selos (raio 3) como na tela. As leituras também são retas: HTML Content
  com fundo offwhite, raio 0, borda 1 px `#0B0B0C` e sombra (0, 12, 32, 22 %). O mini gráfico do avanço é um HTML
  Content de uma série só (barras a
  partir de uma linha-base invisível, sem eixo; rótulos só no mês do ponto e no primeiro mês com aba) — em visual
  nativo, colunas com eixo oculto e rótulos de dados filtrados por medida (`BLANK()` fora dos dois meses).
- Tooltip do mês na curva S: o Power BI aciona pela série (linha/ponto); o exemplo mostra o cursor no ponto de maio.
  Nos meses em que o previsto vier vazio a página de tooltip esvazia as medidas da coluna e do desvio (`BLANK()`).
- Tooltip do ritmo: o visual de colunas agrupadas aciona um tooltip por mês (as duas colunas apontam o mesmo mês).
- O detalhe da leitura da curva S (barras penduradas com as linhas de −1,0 e −3,0) é HTML Content dentro do painel da
  leitura; sem rótulos de valor por regra (L058).
- **Animação:** contadores e racing são do HTML Content (CSS/JS: `transition` em `height`/`width` com `transition-delay`
  escalonado por índice; linhas por `stroke-dasharray`/`stroke-dashoffset`; contador por `requestAnimationFrame`) e
  disparam ao renderizar — o Power BI re-renderiza ao mudar o filtro, então cada troca de obra ou mês re-anima.
  Visuais nativos não animam; onde a tela usar nativo (curva S, ritmo), a animação fica só no HTML das peças.
- O clique na linha do avanço para trocar a obra em foco é cross-filter do visual sobre a tabela de obras (editar
  interações: só a obra; o mês continua do filtro). Se não for desejado, ver a nota da §5.
- O selo `cronograma` das obras a iniciar é a mesma peça do `ILUSTR.`/`REAL` com texto por medida (`fonte` ausente → "cronograma").
- Fontes e hachura como na §8 da spec da Tela 01.

---

## 9. Janela de até 12 meses e obra sem previsto (06/10/2026, Opus 5.5)

Contexto: o modelo lê as planilhas reais (6 obras; histórico jan/26–set/26; referência automática ago/26). Figma: seção
`Interações · Tela 03` (`306:3530`, alargada para a direita), **`Fileira · Janela de até 12 meses e sem previsto`**
(`350:15561`), com a **Nota** de regras (`352:8103`). Títulos neutros: "Avanço das obras" na Tela 03 (`277:1186`), na
casca (`340:15372`, reexportada para `pbi/spec/casca/_fonte/T3.svg` → `wp-t3.svg`), na leitura e no guia.

| Peça | Figma | Regra |
|---|---|---|
| Curva S · 12 meses | `350:15565` | passo = 850 ÷ (n − 1); eixo em mês/ano (passo ≥ 56 px em todas as janelas); só rótulos finais |
| Ritmo · 12 meses / · 3 meses | `350:15633` · `350:15679` | coluna = 448 ÷ n; barras mín(22, (coluna − 10) ÷ 2); rótulos todos quando coluna ≥ 44 px, senão referência, máximo e mínimo (vizinhos: referência > máximo > mínimo); eixo em três letras, janeiro com o ano na virada |
| Tooltip avanço · 12 meses | `350:16136` | coluna = 444 ÷ n; barra mín(40, coluna − 10); rótulos todos quando coluna ≥ 40 px |
| Tooltip curva · 12 meses | `350:16235` | "o melhor mês em doze meses"; "desde" com mês/ano quando bate no começo da janela ou cai em outro ano |
| Sem previsto (JANGADA, ago/26) | cartões `351:8116`, Curva S `351:8140`, Ritmo `351:8175`, linha do avanço `351:8207`, tooltips `350:16636` · `350:16725` · `350:16783` · `350:16851`, leituras `352:7993` · `352:8037` · `352:8054` | vazio não é zero: sem tracejado, área, traço do previsto, chave nem marca; "sem previsto na planilha"; o tooltip do avanço troca o desvio pelo executado acumulado mês a mês; a carteira compara executado e previsto do mesmo grupo (obras com previsto) |

No Power BI: x = `[Série · posição na janela]`; mês da janela sem aba da obra fica vazio (rótulo apagado; no ritmo, margem
antes da coluna). Contas da série olham só a janela (`dMes[Mes] >= [Série · primeiro mês]`): extremos, tendências,
sequências, "desde", mudanças de faixa, meses que alcançaram o previsto, justificativas. Não mudam: mês anterior, valor
da referência, status de hoje. Sinal do desvio em três estados (atrás, no previsto, à frente), pela casa decimal que a
tela mostra. Previsto do mês de 31,83% da REDINHA em jun/26 é dado real (achata o ritmo) e fica.
