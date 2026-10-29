# Brief · redesenho v2 no Power BI (geradores)

07/10/2026. O Figma v2 está aprovado pelo Alisson. Agora o Power BI repete o Figma, pelos geradores. **Leia inteiro antes
de começar**, junto com o seu `pbi/spec/redesenho/t0N.md` (a §5 diz o que muda em cada gerador) e o
`pbi/spec/redesenho/brief-v2.md` (sistema, cores, regras).

## 1. Decisões do Alisson que valem no Power BI

- Cores aprovadas (sistema v2). **Todo número, rótulo e barra negativos ficam em vermelho (`.ng`)**: resultado, variação,
  sem estoque, **desvio físico (atraso)** e ritmo do mês abaixo do previsto. A **única exceção** é o **desvio de
  desembolso negativo** (gastou menos que o previsto), que fica em preto, com a barra na cor da faixa. Limite de régua
  ou faixa nunca é vermelho. (Corrigido em 07/10: a versão anterior deste brief esqueceu o desvio físico.)
- T1: faixa-síntese só na largura da lista (1004).
- T3: barra de executado (avanço e linha do tempo) pela **faixa do desvio físico**; sem previsto em grafite.
- Leituras: como estão no Figma (os blocos que saíram não voltam).
- Drawer, lista de obras: vai sair no **VizuFilter 2.10.0** (outro agente está fazendo), com marca, rótulo e ordem por
  medida. Até ele chegar, a lista continua a segmentação nativa; a troca é da sessão principal.

## 2. O que já está pronto na camada comum (sessão principal; não altere)

- `desenho_comum.py`:
  - tokens v2;
  - marcas `.mk2/.mk1/.mk0/.mkm` (11 px, vermelho, ocre, sálvia, tracejado) e chips `.chip2/.chip1/.chip0/.chipm`
    (25 de altura, 13 px);
  - `.vs` 12 grafite e `.selo` 12;
  - **`.ng`** (vermelho; sobre preto `#F2877C`, sobre creme `#A82C2C`, automático em `.escuro` e `.verso`);
  - hachura da série sem estoque: `.hach` preta, `.hach.ng` / `.hach-ng` vermelha;
  - cartão v2 frente e verso. Na frente, rótulo `.eb` em Barlow SB 15 caixa normal, número 42/50, lado 17/21, contexto
    14/19 em y 102, margem 20, área útil 262. No verso, `.v1` y 16, `.regra` 14/19 de y 36, `.ond` com rótulo de 93,
    `.regua` y 106 em grafite;
  - cabeçalho (`.cab`: rótulo 12, valor Barlow SB 19) e sidebar (mês 23, nota 14).
- `paginas/comum.py`: recorte em uso em (1180, 48, 552 × 24), bloco do mês em (48, 498, 232 × 96).
- Botões: filtro em `paginas/drawer.py` (1760, 38, 44 × 44); guia em `leituras_lib.py` (1816, 38, 44 × 44).

## 3. O que é seu (por tela)

Arquivos que só você edita:
- `paginas/tN.py`, `paginas/tt_tN.py` e `paginas/leituras_tN.py`;
- `desenho_tN.py`, `tooltips_tN.py` e `leituras_tN.py`;
- `contas_tN.py`, só se precisar de conta nova. O contrato conta × desenho continua: o desenho não calcula.
- Exceção: a T1 também edita `paginas/drawer.py`, só a geometria v2 do drawer (680 de largura, `X0` 358, blocos do
  t01.md §2). A lista de obras continua nativa.

Os geradores gravam `pbi/dax/<sua pasta>`.

O que mudar:
1. **Títulos dos cartões em caixa normal** nos literais ("Obras em andamento", "Resultado da obra · ago/26"…), como
   no Figma. A CSS `.eb` não força caixa alta.
2. **Verso:** o `top` da linha "DE ONDE VEM" vai para **82** com régua e **106** sem régua (era 72/89). Textos das regras
   e células encurtados como no Figma.
3. **`.ng`** em todo número e rótulo negativo (resultado, variação, sem estoque, desvio físico, ritmo), com
   `IF ( valor < 0, " ng", "" )` no `class`, como contas → desenho. **Nunca** em desvio de desembolso nem em limite de
   régua. Barras negativas em vermelho.
4. **Status por cor:** use as classes da camada comum. Onde havia hachura como status (atenção), troque pela cor; a
   hachura fica só na série sem estoque.
5. **Geometria v2:** cartões em y 109 do canvas (302 × 140, x 352 · 654 · 955 · 1257 · 1558); painéis, tooltips
   (páginas de tooltip com os tamanhos novos), leituras (= painel) e guia (1120, duas colunas, centrado), todos como no
   seu t0N.md.
6. **Fonte maior** em tudo (escala da §3 do brief-v2): nada abaixo de 12 px; Segoe abaixo de 14 só no eixo (13).
7. **Tooltips:** cabeçalho de 72 com a meta em `flex-wrap` (desce para a 2ª linha, 94, quando não cabe com 24 de
   folga); rodapé preso ao pé, numa linha. Lista cresce em altura, colunas em largura.
8. **Defeitos que o redesenho achou** (corrija no seu gerador; está no seu t0N.md):
   - T1: na síntese, "variação de −0,92 p.p." no lugar de "resultado −0,92 p.p.".
   - T2:
     - a leitura da cascata está errada; falta o ramo "com as contas a pagar, o resultado fica negativo";
     - L058 no quadradinho ("sete" repetido) e na cascata ("mais de um quarto" repetido).
   - T4:
     - o desvio da carteira em jun/26 soma a TIROL, que não tem previsto (aplicar a regra "sem previsto" na conta);
     - na leitura, "TIROL (abaixo do previsto)" aparece com 0%.
   - T1: o físico dá 48,9% no Desktop e 44,6% no HTML. Investigue qual está certo, conte o que achou e corrija se for
     do seu lado.

## 4. Casca v2 (papel de parede) — Figma primeiro

- Página **`PBI · Casca v2 · Criticidade de Obras`** (`406:685`) do arquivo `FjBWDk5odF9HaZ2pwhGosl`.
- Crie o frame **`Casca v2 · TN`** (1920 × 1080) a partir de uma cópia **desanexada** da sua `Tela 0N · v2`. Posições:
  T1 (0, 0), T2 (2120, 0), T3 (4240, 0), T4 (6360, 0).
- **Fica só o que é estático** (L047, igual à `Casca · TN` v1 da página `298:685`):
  - sidebar, sem o bloco "Mês de referência", que é HTML;
  - prancheta, título e pergunta;
  - botões do cabeçalho, sem o "filtro em uso", que é HTML;
  - traços e divisórias creme;
  - moldura dos cartões, com o fundo preto do cartão escuro se a v1 fazia assim (confira a v1);
  - título de cada painel e o "?".
  
  Subtítulos, números, listas, gráficos e legendas dinâmicas saem, porque vêm do HTML.
- A T1 também cria **`Casca v2 · Drawer T1…T4`** em (0, 1200), (0, 2400), (0, 3600), (0, 4800): a sidebar estendida a
  680, com véu, como a v1 `Casca · Drawer TN` (`310:4772`…).
- **Exporte** cada frame em SVG com `download_assets` (`defaultFormat: "svg"`), texto em contorno, e grave em
  `pbi/spec/casca/_fonte_v2/TN.svg` (drawer: `D1.svg`…`D4.svg`). Confira que o SVG não tem `<text>`.
- **Não rode `gerar_casca.py` para valer.** A troca de `_fonte` por `_fonte_v2` e dos papéis de parede é da sessão
  principal.
- Para a foto, use o SVG exportado como fundo, se o seu `foto_tN.py` aceitar um papel de parede alternativo. Se não
  aceitar, acrescente essa opção nele.

## 5. Como provar

- O Desktop do projeto está **aberto** (porta em `pbi/qa/porta.txt`, dados reais de ago/26).
  - **Nunca feche, reabra ou salve o Desktop.** Isso é da sessão principal.
  - Não rode `gerar_modelo.py --aplicar` nem `montar_pbip.py --aplicar`.
  - As simulações, sem `--aplicar`, podem rodar.
- Ciclo:
  1. o seu gerador → `python -X utf8 pbi/scripts/lint_conta_desenho.py pbi/dax --so-erros` com **0 ERRO** →
     `gerar_modelo.py` (simulação) → `montar_pbip.py` (simulação) sem erro;
  2. **foto com dados reais** pelo seu script em `pbi/scripts/fotos/foto_tN.py` (consulta só leitura com
     `DEFINE MEASURE`, L066);
  3. compare com a captura do Figma (`pbi/qa/redesenho/t0N-*.png`) e itere até bater: tela, cada tooltip com os seus
     estados, cada leitura, guia e versos.
- As fotos v2 vão para `pbi/qa/redesenho/pbi/t0N-*.png`.
- Mais três agentes trabalham ao mesmo tempo, cada um nos seus arquivos. Se precisar mudar algo da camada comum (§2),
  não mude: escreva no relatório o que e por quê, e contorne no seu arquivo se der.

## 6. Entrega

Relatório curto com:
- arquivos alterados;
- contagem de medidas e o lint;
- as fotos v2 (caminhos), com o que ficou igual ao Figma e o que ainda difere;
- os defeitos corrigidos;
- as pendências;
- os pedidos para a camada comum.

Atualize a §5 do seu t0N.md com "feito / pendente".
