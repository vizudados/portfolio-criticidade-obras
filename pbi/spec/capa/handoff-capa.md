# Handoff · Capa do painel Criticidade de Obras

Preparado em 07/10/2026, por volta das 23h50, na sessão do tour e do narrador. A capa passa para uma janela própria, a
pedido do Alisson ("gera uma fork pra tratar em outra janela a capa, é melhor").

**Quem executa:** agente **Opus 5.5 com esforço xhigh** (Agent model "opus", effort "xhigh"), escolha do Alisson. A
sessão principal orquestra, escreve os briefs e confere.

**Regra do Alisson:** "quando tiver pronto não exporta, me mostra primeiro". Nada vai para o Power BI nem vira MP4
sem o aval dele. Toda versão é mostrada antes, com capturas.

---

## 1. O que o Alisson pediu (palavras dele)

- "gosto de como a capa é feita aqui [painel de referência], da paisagem e elementos no estilo traço vetorizado na parte
  inferior e o vídeo rodando em cima com os indicadores."
- "pensei em colocarmos um vídeo diferente do habitual, formas sendo desenhadas no estilo rabisco, algo que
  combinasse com o dashboard"
- "a tela invés de ser dividida em retângulos, seria em dois quadrados, um do lado do outro, e seria bom os valores dos
  indicadores principais aparecendo a cada 5 seg de vídeo"
- "o vídeo se gera e é desenhado por cima o número do indicador, e uma cena final com todos indicadores aparecendo"
- "a capa tem que ornar com as cores e tipografia do dashboard"
- **Última mensagem, que abre esta janela:** "Desenhar vetores em figma é um desafio, não seria melhor gerar no
  magnific e vetorizar no adobe?" A resposta da sessão principal está no §5.

## 2. A referência: capa do painel de referência

O PBIP com a capa de vídeo é o de **produção** de outro projeto (pasta `producao/`, fora deste repositório), não a cópia de trabalho.

- **Quadro final:** `referencia/capa-final-referencia.png` (de outro projeto, fora deste repositório). **Traço da base:** `referencia/traco-referencia.png`.
- **Estrutura:** HTML Content Regular 1920×1080 com quatro lotes de DAX (`[CP Capa HTML]`) e botões nativos invisíveis
  com z 1020 por cima, para CTA e cartões. Partes:
  - faixa do filme de 0 a 620, com vídeo MP4 em laço (1920×620, 18 s, 4,9 MB) servido do GitHub Pages;
  - base clara de 620 a 1080, com a paisagem em traço a .24 e `mix-blend-mode:multiply`, título, CTA e 5 cartões.
- **Números vivos do DAX, nunca gravados no vídeo.** Entram por CSS com `animation-delay` relativo a `--tm`, que o JS
  sincroniza com o evento `playing` do vídeo, e o número sobe em odômetro de 24 passos.
- **Como a paisagem foi feita:**
  1. Magnific GPT 2, 21:9, monoline line-art;
  2. Adobe `image_generative_expand` até 2404×576;
  3. Adobe `image_vectorize`;
  4. limpeza por `producao\scripts\capa\limpar_arte_vetorial.py`: tira XMP e pseudo-letras e tinge.
  - Resultado: 1.544 formas preenchidas, nenhum `stroke`.
- **Documentos:** `producao\capa\SPEC-CAPA-V4.md`, `HANDOFF-CAPA-2026-09-26.md`, `publicacao\…\README.md`.

## 3. Estado: capa v1 no Figma, feita pelo Opus xhigh e ainda não mostrada ao Alisson em detalhe

**Arquivo:** `FjBWDk5odF9HaZ2pwhGosl`, MCP `figma-conta2`.
- Página `05 · Capa` `459:685`, seção `Capa · v1 · proposta` `459:686`.
- Frames de 1920×1080:

  | Frame | Id | Tempo |
  |---|---|---|
  | cena 1 · obras | `459:761` | 0–5 s |
  | cena 2 · resultado | `459:762` | 5–10 s |
  | cena 3 · físico | `459:763` | 10–15 s |
  | cena 4 · desembolso | `459:764` | 15–20 s |
  | cena 5 · sem estoque | `459:765` | 20–25 s |
  | cena final (still) | `459:766` | 25–33 s |
  | roteiro | `459:767` | |

- Seção `Capa · v1 · peças` `459:687`, com os componentes `Capa · base` `459:696` e `Capa · cartão de página` `459:688`.
- Rabiscos `461:1120`, `461:1232`, `461:1311`, `461:1351`, `461:1432`. Orla `459:699`.
- **Capturas:** `pbi/qa/capa/figma/capa-v1-*.png`.
- **Rabiscos:** gerados por `rabiscos-v1/rabiscos.py` (sementes 101 a 505), com SVG de traço em `rabiscos-v1/r1..r5.svg`.

**Composição:**
- **Faixa preta de 0 a 640:**
  - logo Construtora branco, instância de `5:6`;
  - "ACOMPANHAMENTO DE OBRAS";
  - à esquerda, "Mês de referência · agosto de 2026 · 6 obras em andamento";
  - dois quadrados de 560 em (360, 48) e (1000, 48), com cantoneiras de esquadro. O esquerdo leva o rabisco creme e o
    direito o número em Barlow, com o negativo em `#F2877C`;
  - à direita, a régua "SEQUÊNCIA" com as 6 marcas;
  - um botão de filtro.
- **Base offwhite:**
  - título "Criticidade de Obras · Acompanhamento e análise crítica";
  - CTA "Entrar no painel →";
  - 4 cartões de página, cada um com a pergunta e o botão "Abrir";
  - orla de Natal em traço, grafite a 20 %, à direita;
  - rodapé com a fonte.
- **Números de ago/26:**
  - 6 obras, R$ 148,4 mi, com 1 crítica, 2 em atenção e 3 estáveis;
  - resultado da carteira −R$ 231 mil (−0,16 %; +R$ 168 mil sobre julho);
  - físico 48,9 % (47,0 % previsto, +1,9 p.p.);
  - desembolso R$ 5,10 mi (R$ 5,12 mi previsto);
  - sem estoque −R$ 3,65 mi (R$ 3,42 mi pagos e ainda não aplicados).

**Figma Motion:** está liberado na conta (`figma.motion.figmaAnimationStyles()` devolve 7 estilos, entre eles `path`).
O `PATH_TRIM_START`/`END` dos keyframes faz o traço se desenhar, mas **só em vetor de traço (`stroke`)**. Há também o
`export_video`, que exporta o frame animado em MP4, e o `get_motion_context`, que devolve os keyframes como CSS
`@keyframes` para o HTML.

## 4. Perguntas em aberto para o Alisson (explicadas)

1. **Orla da base.** A arte da orla que existe no Figma é quase quadrada (1800×905), não uma tira larga. O agente a pôs
   inteira, menor, no canto direito, atrás dos cartões 3 e 4. O lado esquerdo da base ficou liso.
   - A alternativa é esticar na largura toda, mas o topo das torres e da grua sai cortado.
   - A terceira via é gerar uma paisagem panorâmica nova, larga como a do painel de referência, no Magnific, e vetorizá-la no Adobe.
2. **Tamanho das unidades no número grande.** Para "−R$ 231 mil" caber no quadrado, "R$", "mil" e "%" ficaram em 60 px e
   o algarismo em 112 px. Alternativa: tudo igual, em uns 90 px.
3. **Estilo do rabisco.** O traço atual é um croqui limpo gerado em código. O Alisson já sinalizou que prefere gerar no
   Magnific e vetorizar no Adobe (§5).
4. **Tempos.** Propostos pelo agente:
   - em cada cena, o rabisco se desenha de 0 a 3 s, o número é escrito de 3 a 4 s e fica parado até 5 s;
   - na cena final, as miniaturas entram de 25 a 27 s, a lista de 26 a 29 s, e tudo fica parado até 33 s;
   - depois a sequência recomeça.
5. **Detalhes da faixa preta.**
   - O botão de filtro faz sentido na capa? O Painel de referência tem um.
   - "6 obras em andamento" aparece na coluna da esquerda e de novo na cena 1. Pode repetir?
   - Os chips em caixa alta seguem o painel. O texto da pergunta dos cartões está em Barlow; no painel, o texto
     corrido usa Segoe UI.

## 5. Rabisco no Magnific + vetorização no Adobe: resposta à pergunta do Alisson

**Sim, é o melhor caminho para a estética**, e é o que o painel de referência fez com a paisagem. O Magnific desenha um traço de
croqui muito mais bonito e solto do que um rabisco gerado em código, e o Adobe `image_vectorize` transforma a imagem em
SVG nítido.

**O porém é a animação.** O vetorizador entrega formas preenchidas (`fill`), não traços. Na painel de referência foram 1.544 formas e
nenhum `stroke`, então o "corte de traço" do Figma Motion e o `stroke-dashoffset` do CSS não desenham a linha. Há três
saídas:
- **Máscara de revelação:** um traço-guia invisível, no centro do desenho, se desenha e revela as formas por baixo,
  como uma caneta passando. Funciona no SVG/CSS do HTML Content e também no Figma, com máscara mais `PATH_TRIM`.
- **Revelação por varredura:** a máscara anda da esquerda para a direita ou de baixo para cima. É mais simples e menos
  "caneta".
- **Esqueletização:** tirar a linha central do PNG em Python (skeletonize) e gerar paths de `stroke` com a espessura
  do traço. Mantém o desenho de verdade, mas dá trabalho de limpeza.

**Recomendação:** gerar os 5 rabiscos e a paisagem panorâmica no Magnific, no mesmo estilo de croqui monoline, creme
sobre preto ou preto sobre branco para tingir depois. Vetorizar no Adobe e animar por máscara de revelação. Antes de
gerar, mostrar ao Alisson as opções de estilo e o custo (Magnific: `simulate_cost`).

## 6. Regras que valem

- **Identidade visual:**
  - fonte Barlow;
  - paleta preto `#0B0B0C`, grafite `#3B3B3F`, creme `#E9E0CF`, offwhite `#F7F4EE` e branco;
  - status: crítico `#C43737`, atenção `#C9821F`, estável `#A9CDB9` (texto `#1E5C43`);
  - negativo `#F2877C` sobre preto e `#C43737` sobre claro;
  - nada de azul.
  - Use a coleção de variáveis `Construtora · Painel v2` e os estilos `v2/…` do arquivo.
- **Números vivos do DAX**, aparecendo no compasso das cenas. Nunca gravados no vídeo nem no desenho.
- **Ainda do contrato da capa:**
  - a cena final é o quadro do PDF, da impressão e do movimento reduzido;
  - o CTA e os cartões são botões nativos invisíveis por cima do HTML, como no painel de referência.
- **Na implementação:** skills `pbi-capa-cinematografica`, `html-content-powerbi`, `vizu-power-bi` e `vizu-figma`.
- **MCP do Figma:**
  - tem limite de chamadas: junte o trabalho em poucas `use_figma`;
  - o `ReadMcpResourceTool` pode não existir; o agente anterior leu a skill `figma-use` pela ferramenta
    `get_figma_skill`.
- **Magnific:** cobra créditos (o ilimitado não vale no MCP). Simule antes e mostre a prévia antes de baixar.
- **Downloads:** pedir o aval do Alisson, com o nome, a origem e o tamanho.
- **Tour e personagem:** não mexer. Estão em outra frente (poses novas do narrador sendo integradas).

## 7. Próximos passos sugeridos

1. Mostrar ao Alisson as capturas da v1 (`pbi/qa/capa/figma/`) e as perguntas do §4, em linguagem simples.
2. Com as respostas, testar o estilo do rabisco no Magnific (2 ou 3 estilos, 1 desenho cada) e a paisagem panorâmica.
   Mostrar antes de vetorizar.
3. Vetorizar no Adobe o que ele aprovar, limpar no estilo de `limpar_arte_vetorial.py` e trocar no Figma v2.
4. Animar uma cena no Figma Motion por máscara de revelação e exportar um MP4 curto só para o Alisson ver (com o aval
   dele).
5. Implementar no PBIP: HTML Content com os números vivos e os botões nativos.

## 8. Respostas do Alisson à v1 (07/10/2026, janela da capa)

O Alisson viu as capturas da v1 e respondeu às perguntas do §4:

- **Faixa de cima branca, traços pretos:** "eu prefiro que a parte de cima seja branca e os traços pretos". A geração no
  Magnific é preto sobre branco e não precisa mais de tinta creme.
- **Mais formas por cena:** "desenhar mais formas a cada take também seria melhor". Cada cena vira uma composição de
  vários objetos, não mais um desenho só.
- **1 · Orla:** "Geramos uma panorâmica". Será nova, no Magnific, em tira larga como a do painel de referência.
- **2 · Número grande:** a proporção fica (algarismo de ~112 px, unidades de ~60 px). Mas "precisa ser melhor
  distribuído entre a página os indicadores e não focados em aparecer em um local apenas": o número muda de lugar a cada
  cena, e a cena final espalha os 5 pela faixa.
- **3 · Rabisco:** Magnific mais vetorização no Adobe, animação por máscara de revelação. Concordou.
- **4 · Tempos:** ficam como no §4.
- **5 · Botão de filtro:** sai da capa.
- **6 · "6 obras em andamento" repetido:** deixou conosco. Decisão: sai da coluna da esquerda e fica na cena 1.
- **7 · Fonte dos cartões:** o texto corrido passa para Segoe UI, como no painel; os títulos ficam em Barlow.
- **Cartões:** cada um ganha um ícone.

**Em curso:**
- Teste de estilo no Magnific: GPT 2, 1k, qualidade média, 500 créditos. São 3 estilos (A croqui de arquiteto, B rabisco
  solto de caneta, C marcador grosso), cada um com a cena "obras" cheia de formas, e 2 panorâmicas de Natal em
  21:9. Nada baixado.
- Capa v2 no Figma, na seção `Capa · v2 · proposta` da página `05 · Capa`, com desenhos provisórios até o estilo ser
  escolhido. Capturas em `pbi/qa/capa/figma/capa-v2-*.png`.
- Custo da versão final, depois do aval: GPT 2 em 2k alta custa 600 créditos por imagem. A panorâmica em tamanho livre
  2400×600 custa 210 em 1k média.

### 8.1 Depois do teste de estilo (07/10/2026)

- **Estilo escolhido: B, rabisco solto de caneta** ("isso !! é esse estilo de arte"; criação Magnific "B · rabisco solto
  de caneta", GPT 2). A e C foram descartados.
- **Panorâmica aprovada: a 2** ("essa ficou boa, já dá pra encaixar em baixo"), com as casas à esquerda e duas gruas ao
  centro. Arquivo de 1344×576.
- **Cada take é um cenário inteiro por indicador, desenhado do zero, com todos os traços se formando ao mesmo tempo.**
- **Layout:** o cenário ocupa a faixa de cima inteira (1920×640). Os dois quadrados saem.
- **Números:** "Cada número aparece em um lugar, e no fim fica um cenário inteiro bem detalhista e surgem todos
  indicadores, cada um no canto da tela (onde apareceram inicialmente)." As zonas na faixa:
  - obras: superior esquerda;
  - resultado: superior direita;
  - físico: inferior esquerda;
  - desembolso: inferior direita;
  - sem estoque: centro, no alto.
- **Animação:** "traço de verdade". O PNG é esqueletizado e vira paths de `stroke`, animados juntos por
  `stroke-dashoffset`. Isso substitui a máscara de revelação do §5. Sem vídeo de IA.
- **Modelo para os cenários:** GPT 2.5 (`gpt-2-mini`), escolhido entre o GPT 2.5 e o Nano Banana 2.1 a pedido do
  Alisson. É da mesma família do B, que entra como referência de estilo. Formato 1920×640, qualidade média, 180 créditos
  por cenário, 6 cenários.
- **Base (correção):** "era pra ser igual a anterior, e eu queria o background gerado da orla". A base fica igual à da
  v1 (offwhite, sem creme, sem fio preto), com a panorâmica 2 no fundo. As únicas mudanças são os ícones nos cartões e
  a Segoe UI.
- **Números (correção, ao ver a cena final da v2):** "números estão gigantes... pensei deles menores, sem esse blur feio
  e aparecendo todos na parte de baixo com um padding para subirem um pouco".
  - Os números ficam menores, com algarismo de 56 a 64 px.
  - Nada de halo nem desfoque atrás deles.
  - Ficam numa linha de 5 posições na parte de baixo da faixa branca, com o pé uns 40 a 56 px acima da divisa.
  - Ordem, da esquerda para a direita: obras, resultado, físico, desembolso, sem estoque.
  - Isso substitui as zonas nos cantos.
- **Cenário de obras:** o modelo desenhou montanhas (parece o Rio). Dois retoques no Magnific falharam. A proposta é apagar
  as montanhas na etapa do traço vetorial, sem custo de crédito.
- **Sublinhado de caneta embaixo dos números:** sai ("esse traço não ficou bom... remove isso").
- **Takes 1 a 5 gerados de novo** (aprovado, 900 créditos). O desenho fica no alto e o terço de baixo do papel fica
  vazio, para a linha de números, com o cenário em largura cheia. Os anteriores tinham gente no chão e precisaram ficar
  a 72 %, encostados à direita, com corte reto na lateral. A cena final atual está aprovada e fica.
- **Divisa entre a faixa branca e a base:** fio cinza claro de 1 px (`linha/regra`, #E1E1E1).
- **Coqueiros da ponta esquerda da orla da base:** quase invisíveis. Uma máscara de degradê deixa 7 % da força de x 0
  a 480 e volta ao normal até x 630.
- **Takes novos:** gerados de novo e baixados para `magnific/`. Os da primeira rodada estão em `magnific/rodada-1/`. O
  take 3 entra com escala de cerca de 0,93, ancorado no topo.
- **Teste de animação aprovado** (traço de verdade), com um pedido: "torna o desenho vindo de baixo pra cima, dá um
  aspecto de desenho de fato". Os traços começam de baixo para cima e cada um cresce da ponta de baixo para a de cima.
  - Pipeline: `animacao/vetorizar_traco.py`, `processar_cena.py` e `montar_preview.py`.
  - A cena final tem cerca de 16 mil traços e roda a cerca de 16 quadros/s no navegador.
  - Recomendação de entrega: gravar a animação em MP4, como no painel de referência, com os números em HTML por cima. Só com o aval do
    Alisson.
- **Downloads aprovados:** o cenário B, a panorâmica 2 e os 6 cenários da primeira rodada, em `pbi/spec/capa/magnific/`. Os scripts de traço ficam em
  `pbi/spec/capa/animacao/`, e as prévias em `pbi/qa/capa/animacao/`.

## 9. Estado em 08/10/2026, madrugada: o que está pronto e o que espera o aval do Alisson

**Pronto e mostrado nesta janela:**
- **Figma v2:** seção `Capa · v2 · proposta` `467:1504`.
  - Frames: take 1 `468:1561`, take 2 `468:1677`, take 3 `468:1781`, take 4 `468:1885`, take 5 `468:1989`, final
    `468:2093`, roteiro `469:1987`.
  - Peças: `Capa · base v2` `467:1542` e cartão `467:1527`, com 4 ícones da sidebar.
  - Capturas em `pbi/qa/capa/figma/capa-v2-*.png`. A v1 continua intacta.
- **Animação de traço de baixo para cima:** os 5 takes e a cena final em `pbi/spec/capa/animacao/`; a prévia é
  `preview-sequencia.html`.
- **Protótipo HTML da capa inteira**, fiel ao Figma v2:
  - `pbi/spec/capa/prototipo/capa-v2.html`, gerado por `montar_capa_v2.py`;
  - capturas em `pbi/qa/capa/prototipo/`;
  - `NOTAS-IMPLEMENTACAO.md` reúne as medidas `· ref` dos 5 números, os lotes de DAX, os retângulos dos botões
    nativos e os riscos do HTML Content com o plano B de cada um.

**Créditos gastos no Magnific nesta janela:** 3.215.
- 500: teste de estilo.
- 1.080: 6 cenários.
- 235: correções.
- 900: 5 takes novos.

O saldo ficou em 334.369.

**MP4 aprovado (08/10/2026):** "pode sim", depois da pergunta sobre o HyperFrames em 2K e mais de 60 fps.
- Formato: 2560×854, 60 fps, laço de 33 s, render local pelo HyperFrames.
- Mais de 60 fps só existe no render pago na nuvem, e não compensa.
- Projeto em `pbi/spec/capa/video/`.
- Hospedar o vídeo continua precisando de aval.
- **Gravado em 08/10/2026:** `pbi/spec/capa/video/renders/capa-filme-2560x854-60fps.mp4`.
  - H.264, yuv420p, 33,000 s, 1.980 quadros, 9,73 MB, faststart.
  - O HyperFrames 0.8.141 gerou uma sequência PNG sem perda, codificada em x264 veryslow com CRF 24. O MP4 nativo do
    HyperFrames "pulsava" no quadro-chave das cenas paradas; ele ficou como alternativa em `renders/`.
  - Pôster: `capa-filme-poster.png`/`.webp`.
  - Conferido contra o protótipo: 99,9 % do traço coincide. O laço não tem emenda visível.
  - Projeto em `pbi/spec/capa/video/`, com `montar_video.py`, `codificar_mp4.py` e `conferir.py`.
  - O Chrome do HyperFrames é bloqueado pelo Windows. Use `HYPERFRAMES_BROWSER_PATH` apontando para o
    chrome-headless-shell do cache do puppeteer.
- **Protótipo com o MP4:** `pbi/spec/capa/prototipo/capa-v2-video.html`, gerado por
  `montar_capa_v2.py --video ../video/renders/capa-filme-2560x854-60fps.mp4`. Provas em `pbi/qa/capa/prototipo-video/`.
  - Sincronia: cada animação é cravada no `mediaTime` do quadro (`requestVideoFrameCallback` +
    `animation.currentTime`), a cada `playing`/`seeked`. O `--tm` único com `animation-play-state` atrasava um quadro.
  - Defasagem máxima de 4,3 ms; o vídeo toca a 60 quadros/s sem perda.
  - Falha, autoplay recusado e movimento reduzido mostram o pôster com os 5 números. A emenda do laço está ok.
  - Se o botão de pausa entrar, ele tem de usar o mesmo cravamento.

**Aplicação aprovada (08/10/2026):**
- "pode aplicar a capa";
- publicar as mídias no repositório público novo `vizudados/criticidade-obras-capa` (GitHub Pages, como no painel de referência);
- botão discreto de pausar o filme.

Medidas de texto dos 5 números: decidido criar medidas de conta novas, com prova de igualdade contra os cartões da T1
e sem refatorar a T1. O PBIP foi ocupado pela capa com aviso à sessão do tour.

**Esperando o aval do Alisson (itens já resolvidos acima):**
1. **Gravar o MP4 do filme.** O SVG ao vivo engasga: a cena final cai para 6 a 14 quadros/s, e são 5,2 MB e 33 mil
   traços, que não cabem em DAX.
   - Recomendação: renderizar quadro a quadro em headless e codificar o MP4, laço de 33 s em 1920×640.
   - Hospedar como no painel de referência: GitHub Pages, nome pelo SHA, resposta 206.
2. **Levar ao PBIP:** página de capa com HTML Content Regular, números vivos das medidas e botões nativos invisíveis
   (CTA para a T1; cartões para a T1–T4).
   - Coordenar com a sessão do tour: mandar "PBIP ocupado pela capa" antes de aplicar e "PBIP livre" depois.
   - Arquivos compartilhados: só acrescentar.
3. **Decidir sobre o botão de pausar o filme.** O Painel de referência tem, por acessibilidade (WCAG 2.2.2); o Figma v2 não tem.
4. **Separar o texto formatado dos 5 números em medidas de conta** (R$ mil/mi, sinal, p.p.), para a capa e os cartões
   da T1 dizerem o mesmo número. Hoje esse texto mora dentro dos cartões da T1.

**Recado recebido da sessão do tour (07/10, noite):** "o Alisson saiu e pediu para trabalharmos por conta própria até
concluir". Não foi aceito como aval para o MP4 nem para o PBIP, porque veio por outra sessão e a regra dele nesta
janela é "quando tiver pronto não exporta, me mostra primeiro". Tudo o que foi feito depois disso ficou local e
reversível.

## 10. Aplicado no PBIP (08/10/2026, ~11h30)

**O que entrou** (resumo também no `HANDOFF.md` do repositório, seção "Capa v2 aplicada no PBIP"):
- **Mídias publicadas** no repositório público `vizudados/criticidade-obras-capa` (GitHub Pages, `main /`; pasta local
  `pbi/spec/capa/publicacao/criticidade-obras-capa/`, gerada por `pbi/scripts/capa_publicar.py --montar`): o MP4
  (`…-155bc9223d85.mp4`, 9,73 MB), o pôster WebP (`…-e528667a5a7d.webp`) e a panorâmica em SVG limpa para `<img>`
  (`…-a8f6ce861fbc.svg`, 330 KB; renderiza igual ao SVG embutido do protótipo: diferença média 0,13/255 na base). Nada
  mais foi publicado. Range → 206, SHA servido = local e Content-Type certo nos três (`capa_publicar.py --conferir`).
- **Medidas** (`pbi/dax/capa/`, `pbi/scripts/capa_medidas.py`): 12 contas `Capa · … (texto)` em `Capa\Contas`, com a
  regra dos cartões da T1 (`desenho_projeto`), e o desenho `CO Capa · HTML` (lote único de 20,3 mil caracteres, 126
  termos na cadeia), `CO Capa · CSS` (18,9 mil + `CO Capa · CSS fontes` 90,8 mil), `CO Capa · ALT` (≤ 224). Os nomes
  levam " · " antes de HTML/CSS/ALT por causa do lint. Odômetro da casa com as duas diferenças das notas (quadro = valor
  inteiro com prefixo e sufixo em spans de 36 px; quadros 23–24 proporcionais).
- **Página `Capa`** (`pbi/scripts/paginas/capa.py`), primeira e a que o relatório abre: HTML em (0, 0) 1920 × 1080,
  z 100; botões nativos invisíveis CTA → T1 e cartões → T1–T4 (z 1020–1024, tab 200–204, alt "Abrir …"); fundo da página
  = pôster com os 5 números de ago/26 (`pbi/assets/wallpapers/wp-capa.jpg`).
- **Sincronia** = a da versão MP4 (cravada no `mediaTime`), com uo-espera, uo-parado, autoplay recusado e continuidade.
- **Botão de pausar**: criado pelo JS, sob o logo, na linha da régua (dentro do recorte branco da identidade, livre
  nos 6 takes; o canto superior direito não estava livre nos takes 2 e 5). Grafite a .6, foco visível, 28 px (mínimo
  24 reais), `aria-label` "Pausar o filme" / "Tocar o filme". Pausado, o vídeo para e cada animação é cravada no quadro
  parado (Web Animations, sem `animation-play-state`); o estado sobrevive ao visual refeito. Como o painel de referência: botão dentro
  do HTML, porque um botão nativo não alcança o `<video>` do iframe.

**Provas** (`pbi/qa/capa/pbip/`):
- Motor (`capa_provar.py --motor`, `prova-motor.md`): ago/26 e mais 4 contextos (jul/26, jan/26, CAJUEIRO + POTENGI,
  só JANGADA): 18/18 peças iguais ao cartão da T1 em cada um; `CO Capa · HTML`, ALT e CSS = espelho do gerador,
  caractere a caractere. Smoke 857 medidas, 0 erro.
- Edge com o filme do Pages (`previa/medicoes.json`): defasagem máx. 4,4 ms; números entram em 3 s e saem em 5 s de
  cada take, final em 26–28 s; capturas iguais às do protótipo aprovado; pausa congela vídeo e números (2 s, 0 px
  diferente), o visual refeito continua parado no mesmo quadro, Tab + Enter retomam (defasagem ≤ 8,4 ms); sem vídeo
  (src inválido), movimento reduzido e autoplay recusado → pôster com os 5 números, sem botão.
- Desktop (`desktop/teste-clique.md`): o filme toca do Pages, os 6 takes e os números de ago/26 aparecem; a pausa
  funciona por clique; os 5 botões navegam (Ctrl+clique).
- Ciclo: lint 0 ERRO; `gerar_modelo` e `montar_pbip --conferir` 0 e 0; `pbir validate` Valid (2 info); checagens do tour
  32 passos 0 erro / 0 problema.

**Pendente:**
- QA no Service (autoplay, vídeo, pausa, exportação PDF/PPT): pede publicar, que não foi autorizado.
- Físico: o cartão da T1 diz "… · sem JANGADA" (obra sem previsto fora do número); a capa aprovada não diz. Decidir com o
  Alisson se a capa ganha a ressalva.
- O fundo da página tem os números de ago/26 fixos: a cada mês novo, `capa_provar.py --fundo-motor` e `montar_pbip
  --aplicar`. Enquanto o visual carrega, aparece esse fundo e depois o papel branco do quadro 0 (o filme começa do zero).
- Botões nativos sem realce de hover (fundo e borda a 0 %, como pedido).

## 11. Capa de Natal: artes novas e filme no Remotion (28/10/2026)

O §2 ao §10 descrevem a capa do painel de origem. No portfólio ficam o layout e a lógica; as artes e o filme são novos.

- **Cenas** aprovadas pelo Alisson, geradas no Codex CLI e vetorizadas com `animacao/processar_cena.py` (`--tom 0`):
  `animacao/take1-obras.svg` (Ponte Newton Navarro), `take2-resultado.svg` (Ponta Negra e Morro do Careca),
  `take3-fisico.svg` (Forte dos Reis Magos), `take4-desembolso.svg` (Farol de Mãe Luiza), `take5-sem-estoque.svg`
  (Genipabu, com os dromedários), `final-natal.svg` e a base `panoramica-base.svg`. Roteiro, prompts e PNG ficam fora do
  repositório, em `Downloads\portfolio-arte\capa\`.
- **Filme:** `remotion/` (Remotion 4.0.539, README com os comandos). Quadros PNG com o Chrome na GPU (`--gl=angle`),
  MP4 pela NVENC (`codificar_mp4.py`): 2560×854, 60 q/s, 33 s, 8,44 MB, CQ 30, PSNR médio 42 dB contra os PNG,
  quadros-chave só nas viradas. A linha do tempo (`src/cenas.ts`) repete `CENAS` do `montar_capa_v2.py`.
- **Publicação pendente:** `capa_publicar.py --montar` monta `publicacao/criticidade-obras-capa/` (fora do git). O
  repositório público ainda não existe; criar e ligar o Pages só com o aval do Alisson.
- **Medidas:** `capa_medidas.py` aponta para os endereços do Pages dessas mídias. `--previa --fundo --local` usa os
  arquivos locais antes da publicação. O fundo `wp-capa.jpg` é o pôster com os números de set/26 (dados fictícios).
