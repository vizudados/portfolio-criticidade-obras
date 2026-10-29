# Capa v2 · notas para o passo do PBIP

Protótipo: `capa-v2.html` (5,6 MB, autocontido), gerado por `montar_capa_v2.py`. **Nada disto foi para o PBIP.**
O passo do PBIP só começa com o aval do Alisson ("quando tiver pronto não exporta, me mostra primeiro").

```
python -I montar_capa_v2.py                      # regrava o HTML
python -I montar_capa_v2.py --capturas --medir   # capturas em pbi\qa\capa\prototipo\ e quadros/s no Edge
# versão com o filme em MP4 (capa-v2-video.html, 458 KB, nada embutido) e a prova dela em pbi\qa\capa\prototipo-video\
python -I -X utf8 montar_capa_v2.py --video ../video/renders/capa-filme-2560x854-60fps.mp4 --capturas --medir
```

## 1. Forma no Power BI (a mesma do painel de referência)

Página nova `Capa`, 1920×1080, com:
- um **HTML Content Regular** de 1920×1080 em (0, 0);
- os **botões nativos invisíveis** do §5 por cima, com z acima do HTML (no painel de referência, 1020).

O modelo não tem grupo de cálculo, então o teto de 32.760 caracteres por medida (L048) não trava. Mesmo assim, siga
duas regras:
- **Cada lote fica abaixo de 29.000 caracteres**, a regra do painel de referência.
- **Nenhuma cadeia de `&` passa de ~900 termos.** Acima disso o motor recusa com "query is too complex" (testado na
  sessão do tour em 08/10: 900 passa, 1.000 não). Agrupe os termos entre parênteses, como faz `tour_lib._dax`
  (`DAX_ITENS_MAX` e `DAX_GRUPO`).

Tamanhos medidos no protótipo:

| Parte | Caracteres | Vai para |
|---|---:|---|
| CSS do palco (sem fontes, sem filme) | 10.000 | folha de estilo |
| CSS da linha do tempo (régua, recorte, números) | 8.100 | folha de estilo |
| Barlow 400/600/700 em woff2 base64 | 90.800 | medida de fontes própria (plano B no §6) |
| HTML fixo (identidade, régua, base, cartões, logo) | 7.800 + 3.800 | lote 1 |
| 5 números com os 25 quadros do odômetro | 776 / 2.178 / 1.348 / 2.102 / 2.155 | lote 2 |
| JS (sincronia, erro do vídeo) | ~3.600, ou menos se tirar o JSON | lote 3 |
| Panorâmica em traço (SVG limpo) | 330.000 | fora da medida (§4) |
| Filme em SVG (33 mil traços) | 5,2 MB | **não cabe: vira MP4** |

Sem dimensão de lote (o painel de referência usa `dLote`), o caminho é uma medida só, com os termos agrupados. Se precisar de lotes,
é preciso criar uma tabela `dLote` no modelo, o que é mudança de modelo.

## 2. Os lotes de DAX

- **`CO Capa HTML`** = base fixa + números + JS. A base fixa pode ir para `templates.bodyTemplate` do HTML Content
  2.0 (`pbip_lib`, `modelo_corpo`), que fica fora do limite da medida.
- **`CO Capa CSS`**, a folha de estilo do visual, ligada por formatação condicional: palco e linha do tempo.
- **`CO Capa CSS fontes`**, ou o reaproveitamento de `[Comum · CSS fontes]`.
- **`ALT CO Capa`**: "Capa do Criticidade de Obras, ago/26: 6 obras (1 crítica…), resultado −R$ 231 mil…" (≤ 250).

O bloco JSON no topo do protótipo mostra o que a DAX injeta. Cada campo vem de uma medida que já existe (todas em
`pbi\dax\base\referencia\`, salvo indicação):

| Campo do JSON | Medida | Texto em ago/26 |
|---|---|---|
| `mes` | `[Mês de referência · longo]` (`base\mes\`) | agosto de 2026 |
| obras · valor | `[Obras com análise · ref]` | 6 |
| obras · status | `[Carteira · obras críticas · ref]`, `[… em atenção · ref]`, `[… estáveis · ref]` (BLANK → 0; chip só se > 0; plural "1 crítica" / "2 críticas", "1 estável") | 1 / 2 / 3 |
| obras · apoio | `[Orçamento · ref]` | R$ 148,4 mi em orçamento |
| resultado · valor | `[Resultado da obra · ref]` (negativo em `#C43737`, sinal U+2212) | −R$ 231 mil |
| resultado · apoio | `[Resultado % · ref]` (vermelho se < 0), `[Resultado · variação no mês · ref]`, `[Mês anterior à referência · nome]` | −0,16% do orçamento · +R$ 168 mil sobre julho |
| físico · valor | `[Físico · executado acumulado · com previsto · ref]` (a mesma do cartão T1) | 48,9% |
| físico · apoio | `[Físico · previsto acumulado · ref]`, `[Físico · desvio acumulado p.p. · ref]` (já em p.p.) | 47,0% previsto · +1,9 p.p. |
| desembolso · valor | `[Desembolso · realizado no mês · ref]` | R$ 5,10 mi |
| desembolso · apoio | `[Desembolso · previsto no mês · ref]` | R$ 5,12 mi previsto |
| sem estoque · valor | `[Resultado sem ativos · ref]` | −R$ 3,65 mi |
| sem estoque · apoio | `[Ativos não consumidos · ref]` | R$ 3,42 mi pagos e ainda não aplicados |

**Cuidados nos lotes:**
- **Formatação.** Hoje a regra de R$ mil/mi, do sinal e do p.p. mora dentro de `T1 · Cartão … · HTML`, gerado por
  `scripts\desenho_t1.py`.
  - Para a capa e o cartão dizerem o mesmo número, separe o texto em medidas de conta, por exemplo `… · texto` em
    `\Contas` (skill `dax-conta-desenho`).
  - A capa só lê essas medidas.
- **Odômetro: a técnica do painel** (`contador.py`: `<o-d><o-v>` final, tira `<o-t aria-hidden>`). Duas diferenças:
  - **cada quadro é o valor inteiro** com prefixo e sufixo em spans de 36 px (`−R$ 208 mil`), alinhado à esquerda,
    para a tira não pisar no "R$";
  - os quadros 0–22 têm algarismos tabulares e os 23–24 vêm proporcionais (`<span class='pr'>`), como o Figma.
  - A conta continua inteira: quadro k = ROUND(T·f_k/1000), com f_k a tabela de 25 milésimos.
  - Custo: cerca de 25 × (len + 40) caracteres por número.
- **Escape.** Os rótulos fixos não precisam. Os textos de medida passam pelo escape padrão (`&` primeiro).

## 3. Linha do tempo e sincronia (o `--tm` do painel de referência)

**A linha do tempo.** Tudo o que é HTML por cima do filme roda num laço de 33 s, com `animation-delay: var(--tm)`.
São quatro camadas: a régua, a largura do recorte da identidade, os blocos dos números e as tiras do odômetro.
- Take k (0–4): o número entra em 5k + 3 s. Sobe 8 px em 0,5 s, conta em 1,0 s com 24 passos e sai com o take, em 5k + 5.
- Final: os 5 números entram em 26,0 / 26,5 / 27,0 / 27,5 / 28,0 s (o último termina de contar em 29 s) e ficam
  até 33 s.

**Sincronia em produção: use a da versão MP4** (`capa-v2-video.html`, `--video`; JS `JS_SINC_VIDEO` do
`montar_capa_v2.py`). O filme é `<video class="filme" muted autoplay loop playsinline preload="auto" poster>`,
2560×854 mostrado em 1920×640 (`object-fit: cover`, topo preso), MP4 e pôster por caminho relativo.
- A cada `playing` e `seeked` (a volta do laço dispara os dois), o JS espera o quadro na tela
  (`requestVideoFrameCallback`) e **crava cada animação da capa no `mediaTime`** (`animation.currentTime`), uma a uma.
  No quadro seguinte confere todas; a cada `timeupdate` corrige se alguma passar de meio quadro.
- **Não use `--tm` único nem `animation-play-state` para sincronizar.** Medido no Edge 154: toda vez que as
  animações começam ou voltam de pausa, as que o compositor roda (opacidade e transform: números, odômetro, rótulos
  da régua) ganham o relógio um quadro depois das outras (largura do recorte, tracinhos da régua). Com `--tm` e
  pausa, o número ficava 4–7 ms atrás do vídeo e aparecia no papel branco do corte. `--tm` fica só como plano sem JS
  (0) e para segurar a linha do tempo no zero enquanto o vídeo não toca (`--tm: 1000s`, sem pausar).
- Estados no `<html>`: `uo-espera` (até o 1º quadro: vídeo invisível, faixa no papel branco = quadro 0), `uo-parado`
  (pôster como fundo da faixa + os 5 números: erro do vídeo, autoplay recusado, 5 s sem tocar, movimento reduzido;
  impressão pela mesma folha).
- Portado do painel de referência: autoplay recusado (`NotAllowedError` → parado) e continuidade (`window.__uoT` =
  [currentTime, relógio]; o HTML recriado retoma onde o filme estaria, linha do tempo já no ponto).
- Prova em `pbi\qa\capa\prototipo-video\` (`medicoes.json`, Edge headless, vídeo tocando, servidor com Range):
  defasagem máxima de 4,3 ms (1 quadro da página a 240 Hz), número entra em 3,000 s e sai em 5,000 s de cada take,
  vídeo a 60 q/s sem quadro perdido; fora da faixa do filme, as capturas são idênticas às do protótipo SVG.

**Falta:** decidir com o Alisson o botão "Pausar filme" (WCAG 2.2.2, o painel de referência tem; o Figma v2 não). Se entrar, a
pausa congela a linha do tempo cravando as animações no `mediaTime` do quadro parado (sem `animation-play-state`).

**Movimento reduzido e impressão.** Sem vídeo e sem animação: fica o pôster da cena final desenhada, com os 5
números em HTML. É o repouso de toda a folha.

## 4. Onde o MP4 e a panorâmica vão morar (pendente de aval)

**Gravação, só com o aval.** Grave a partir do próprio `.filme` do protótipo, em quadros congelados (`paused` +
`animation-delay` negativo, como em `congela_css`).
- 1920×640, 30 q/s, 990 quadros, laço de 33 s.
- Codificação: H.264 High, CRF ~23, `+faststart`, sem áudio.
- Pôster: a cena final desenhada. O primeiro quadro é papel em branco e não serve.
- O mesmo pôster com os números vira o fundo da página, para o PDF.

**Hospedagem, como no painel de referência.** GitHub Pages da Vizu, num repositório próprio, por exemplo
`vizudados/criticidade-obras-capa`.
- Nome do arquivo: arquivo + 12 hex do SHA-256.
- Antes de integrar, conferir GET com Range → 206 e o SHA servido igual ao local.
- O filme não tem dado nem marca do cliente, só desenho. Ainda assim é URL pública: perguntar ao Alisson.

**Alternativas:**
- Blob ou CDN da Vizu com Range.
- SharePoint e pastas sincronizadas não servem: pedem login e não dão 206 anônimo.
- Data URI só se o MP4 ficar abaixo de ~1 MB (a skill mediu 834 mil caracteres de vídeo renderizando).

**Panorâmica (330 KB em SVG):**
- publicar ao lado do MP4 (o painel de referência fez assim com o papel de parede SVG);
- ou rasterizar em WebP a 1920×440 e embutir (estimativa de 60 a 120 KB) na base fixa ou no `bodyTemplate`.

## 5. Botões nativos invisíveis (página 1920×1080, px)

| Botão | x | y | w | h | Destino |
|---|---:|---:|---:|---:|---|
| CTA "Entrar no painel" (raio 30) | 1556 | 681 | 268 | 60 | T1 · Visão geral |
| Cartão Visão geral (raio 16) | 96 | 836 | 414 | 168 | T1 · Visão geral |
| Cartão Análise crítica | 534 | 836 | 414 | 168 | T2 · Análise crítica |
| Cartão Avanço físico | 972 | 836 | 414 | 168 | T3 · Avanço físico |
| Cartão Resultado no tempo | 1410 | 836 | 414 | 168 | T4 · Resultado no tempo |

- **Pílulas "Abrir"**, se preferirem só a pílula: x = 394 / 832 / 1270 / 1708, y 952, 92 × 34, raio 17.
- Fundo e borda 0 %, sem texto.
- Texto alternativo: "Abrir Visão geral" etc.
- Ordem de tabulação: CTA e depois os cartões da esquerda para a direita.
- No HTML, o CTA e as pílulas são só desenho (`aria-hidden`).

## 6. O que o HTML Content Regular pode impedir, e o plano B

| Risco | Plano B |
|---|---|
| `display` animado em `@keyframes` (troca dos takes) exige Chromium ≥ 116 | Só o filme em CSS usa isso, e ele vira MP4. Sem MP4: a cena final parada (a folha do movimento reduzido) |
| 33 mil traços animados: 5,2 MB não cabem em DAX; no navegador o desenho roda a 2–74 q/s (§7) | MP4. Sem aval do MP4: pôster parado e só os números animados |
| Tamanho da string e cadeia de `&` (> ~900 termos) | Termos agrupados entre parênteses; fontes numa medida própria; base fixa no `bodyTemplate` |
| Barlow 400/600/700 em base64 (90,8 mil caracteres); fonte do Google é bloqueada no sandbox | Subconjunto só com os caracteres da capa (pyftsubset, ~10–15 KB por peso), ou as faces 500/600 do painel (`'Barlow U'`) com o título em 600 |
| Vídeo remoto: rede ou tenant bloqueia, host sem 206 | Erro → `uo-parado` (quadro final com os números); pôster como fundo da página |
| PDF/PPT do Regular pode omitir o visual | Fundo da página = pôster com os números (como a V4I-01 do painel de referência) |
| `mix-blend-mode: multiply` e `mask-image` na panorâmica | Suportados no Chromium. Plano B: rasterizar a panorâmica já com a máscara e a opacidade aplicadas |
| JS falha | O CSS roda sozinho com `--tm` 0; o número pode descolar do vídeo, mas nunca some (o repouso é o valor final) |
| Elementos `o-d`/`o-v`/`o-w`/`o-t` | Já usados no painel |
| Escala: o iframe do visual não tem 1920 px no notebook | Toda medida já é `calc(var(--u)*N)`, como no painel de referência; prova no Desktop e no Service |

## 7. Medição de quadros por segundo (protótipo, Edge 154 headless, RTX 5070 Ti, com o Power BI Desktop aberto em outra sessão)

**Por fase:**
- Partes paradas (números contando, cenas prontas): ~105 q/s.
- Desenhando:
  - take 1: 15 / 15 / 74 q/s nos segundos 0–2;
  - takes 3–5: 2 a 12 q/s no segundo do meio;
  - cena final: 30 / 6 / 32 q/s em 25–27 s.
- Os números da final começam a contar enquanto o desenho termina, então os dois primeiros sobem aos trancos no
  protótipo. No MP4 isso some.

**Comparação com a referência.** O `preview-sequencia.html` anterior, medido igual, dava 7–9 q/s na cena final
inteira, até parada, e 10–33 q/s nos takes.

**O que mudou para isso:**
- cada classe de tempo virou um grupo `<g>` com o `stroke-dashoffset` herdado (183–224 animações por cena, em vez de
  4–8 mil);
- cada grupo anima uma vez e para (`iteration-count: 1`);
- tracejado só enquanto o traço cresce; traço que ainda não começou fica `visibility: hidden`.

**O gargalo que sobra** é o recálculo de estilo dos milhares de traços herdeiros: ~2 s de 3 s no trace. Só o MP4
resolve.
