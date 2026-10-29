# Diff antes de aplicar · tour guiado

**Quando:** apuração de 07/10/2026. Plano × disco foi comparado por volta de 16h06 e conferido de novo às 16h12 (mesmas contagens nas duas rodadas). O agente seguiu editando o tour depois: `passos-v1.json` (16h07), `passos.json` (16h08) e `brief-tour.md` (16h09). Este relatório é do estado de 16h06-16h12, não do final.

**Como foi feito (somente leitura):**
- `gerar_modelo.py --conferir --sem-tom`. O `--sem-tom` foi usado porque o lint TOM grava em `pbi/qa/modelo`.
- `montar_pbip.py --conferir`. Ele bloqueia (erros L018) porque o contexto vem do disco, que ainda não tem as medidas do tour.
- Como `--conferir` só dá nomes de arquivo, o plano foi gerado em memória chamando as funções dos próprios geradores, com o contexto do plano do modelo. Depois foi comparado com o disco por arquivo, por medida e por objeto. Os scripts de apoio ficaram no scratchpad.
- Nada foi gravado no PBIP, nos geradores ou em `pbi/qa`. Os scripts rodaram com `-B`.

## Resumo

- **Modelo:** 11 arquivos diferentes. Um tem conteúdo do tour (`_Medidas.tmdl`). Os outros 10 têm só forma (formatação, ordem e anotações que o Power BI Desktop escreve ao salvar). Nenhum vem de gerador alterado depois das 13h50.
- **Report:** 414 arquivos diferentes e 12 que saem. Desses, 200 são do tour e do guia. Os outros 226 são só forma ou um recurso órfão.
- **Causa da forma:** o projeto foi regravado inteiro às 15h03. Veja a seção 5.
- **Cartão "Justificativas do mês" (T4):** não está entre as diferenças de conteúdo. Seção 3.
- **Não é seguro aplicar agora.** Seção 6.

## 1. Modelo (`gerar_modelo --conferir`, 11 arquivos)

| arquivo | o que muda | classe | origem provável |
|---|---|---|---|
| `definition/tables/_Medidas.tmdl` | +33 medidas do tour (32 "T<n> · Tour · Passo NN · HTML" e "Comum · Tour · CSS"). −4 medidas "T<n> · Guia · HTML". 77 medidas com a mesma DAX em forma diferente: o gerador escreve a expressão em duas linhas e o disco tem uma (em "Orçamento" também muda a aspa do nome). Ordem diferente em 765 de 798 medidas comuns. | (a) tour, mais (c) forma e ordem | `tour_lib.py` e `pbi/dax/T<n>/Tour` (15h58-16h01). A forma e a ordem vêm do salvamento do Desktop (15h03). |
| `definition/expressions.tmdl` | Os 12 objetos têm o mesmo corpo. O Desktop mudou a ordem: os 3 parâmetros (`pOrigemPlanilhas`, `pSharePointSite`, `pSharePointPasta`) ficaram depois de `stgAbas`. Tirou `PBI_ResultType` dos parâmetros e pôs tabulação em linhas em branco. | (c) | Desktop 15h03 |
| `definition/tables/dObra.tmdl` | 2 linhas em branco com tabulação. M idêntico. | (c) | Desktop 15h03 |
| `definition/tables/fAnaliseCritica.tmdl` | 6 linhas em branco com tabulação. M idêntico. | (c) | Desktop 15h03 |
| `definition/tables/fConferencia.tmdl` | 8 linhas em branco com tabulação. M idêntico. | (c) | Desktop 15h03 |
| `definition/model.tmdl` | Acrescenta `annotation PBI_ProTooling = ["DevMode"]`. A `ref table dJanela` mudou de lugar. | (c) | Desktop 15h03 |
| `definition/cultures/pt-BR.tmdl` | Acrescenta `linguisticMetadata` (72 linhas, `State: Generated`). É gerado automaticamente, sem curadoria manual. | (c) | Desktop 15h03 |
| `definition/relationships.tmdl` | Omite `crossFilteringBehavior: oneDirection` (valor padrão) nas 6 relações. | (c) | Desktop 15h03 |
| `.pbi/editorSettings.json` | Omite 5 chaves que valem `false` (padrão). | (c) | Desktop 15h03 |
| `.platform` | Só bytes: o disco não tem quebra de linha no fim (`\r\n}`). JSON idêntico. | (c) | Desktop 15h03 |
| `definition.pbism` | Só bytes, igual ao `.platform`. JSON idêntico. | (c) | Desktop 15h03 |

Classes: (a) 1 arquivo (`_Medidas`, que também tem forma); (b) 0; (c) 10.

(b) é zero porque nenhum gerador do modelo mudou depois das 13h50: `gerar_modelo.py` é de 06/10 18h16, `dax_para_tmdl.py` de 03/10, e `pbi/m/*.m` é anterior a 13h50.

## 2. Report (`montar_pbip`, plano × disco)

| grupo | qtd | classe | origem provável |
|---|---|---|---|
| visuais novos `T<n>_Tour_P<NN>`, `_TourAnt_`, `_TourProx_`, `_TourFecha_` (32 passos × 4) | 128 | (a) | `paginas/tour.py` e `tour_lib.py` (16h01) |
| bookmarks novos `T<n>_TOUR_NN` e `T<n>_TOUR_00` | 36 | (a) | `paginas/tour.py` |
| `bookmarks.json`: grupo "tour" (36) novo; grupo "leituras" de 23 para 19 | 1 arquivo | (a) | `paginas/tour.py` e `leituras` (15h57) |
| visuais `T<n>_Gui_Fora` e `T<n>_Gui_Html` que saem | 8 | (a) | `leituras_t<n>.py` (15h57) |
| bookmarks `T<n>_GUIA_01` que saem | 4 | (a) | idem |
| visuais `T<n>_Aj_Guia` (botão "?"): texto, tooltip e link passam de `T<n>_GUIA_01` para `T<n>_TOUR_01` | 4 | (a) | `leituras_lib.py` e `paginas/leituras_t<n>.py` (15h57) |
| bookmarks `T<n>_LEITURA_*` sem os visuais Gui (lista e estado) | 19 | (a) | idem. Todas as diferenças desses bookmarks estão em campos `Gui_` ou em `targetVisualNames`. |
| recurso `wp-provisorio.svg` (está no plano, não está no disco) e `report.json` (lista de recursos) | 2 | (c) | `paginas/comum.py` (07/10 12h05) sempre registra o recurso. Nenhuma página do disco o usa. Provavelmente o Desktop tirou o recurso não usado no salvamento de 15h03. |
| JSON só de forma: 187 visuais, 19 páginas, 8 bookmarks, 10 outros | 224 | (c) | Desktop 15h03 (CRLF, sem quebra no fim, ordem de chaves) |

Totais: visuais 319 = 128 + 4 + 187. Bookmarks 63 = 36 + 19 + 8. Páginas 19. Saem 12 (manifesto de 13h51): 8 visuais Gui e 4 bookmarks GUIA_01.

- **(a)** 188 arquivos mudam e 12 saem: 200.
- **(b)** 0. `pbip_lib.py` mudou às 15h57, mas os 187 visuais que já existiam batem em JSON com o disco. Ele não alterou conteúdo existente.
- **(c)** 226 = 224 de forma + `wp-provisorio.svg` + `report.json`.

## 3. Cartão "Justificativas do mês" (T4)

**Não está entre as diferenças de conteúdo.**
- Visual `T4_Kpi_Justificativas`: só forma.
- Medida `T4 · Cartão justificativas · HTML` e as medidas de base (justificativas em branco, exigidas e preenchidas): mesma DAX. Só 4 delas mudam a quebra de linha.
- `justificativas_rodape.py`: última alteração em 06/10 22h54. Compila (95 linhas, funções `_px_nomes` e `nomes`). Não foi tocado depois das 13h50. É importado por `contas_t4.py` e `desenho_t4.py`, ambos anteriores às 13h50.

O que ficou interrompido no cartão não aparece no diff: o disco tem o que o código gera hoje. O que falta é a conferência em foto, que não é diff.

## 4. Estado do tour nesta apuração

- `tour_lib.py` foi alterado às 16h01. `passos.json` às 16h08. Ambos seguem em edição.
- O gerador já não roda para todos os passos. Em T4 passo 03 (id `MES`, "O resultado, mês a mês") dá `KeyError: 'fecho'` em `_corpo_mes`. Os outros 31 passos geram.
- Os DAX do tour em disco (15h58-16h01) não batem com o que o gerador produz agora: os 31 que geram diferem. Exemplo: o card do T1 passo 1 mudou de 836×78 para 766×60.
- O HTML de cada passo tem agora cerca de 126 mil caracteres. As poses do personagem vêm em base64 (`data:image`). Os DAX em disco têm cerca de 2,4 mil. Se o tour for aplicado com os DAX atuais, o modelo fica com HTML que o gerador não produz mais, e o report fica com visuais de outra versão.
- Peso: 32 medidas de cerca de 126 mil caracteres são cerca de 4 MB de DAX dentro do `_Medidas.tmdl`. Vale decidir antes se a pose fica embutida ou vai como recurso.

## 5. Evidência do salvamento de 15h03

- Todos os 20 arquivos do modelo e 210 do report têm hora de gravação 15h03, inclusive os que não mudaram.
- `.pbi/cache.abf` e `.pbi/localSettings.json` têm essa hora. São arquivos que o Desktop cria.
- O backup `modelo-20261007-135032` (estado antes da aplicação das 13h50) não tem `linguisticMetadata` nem `PBI_ProTooling`, e já tinha as expressões na ordem do gerador. Os 3 parâmetros estavam lá.
- A forma em uma linha das 77 medidas também já estava nesse backup. Então não dá para atribuir só ao salvamento de 15h03.
- O Desktop não está aberto agora (checado). Não há log que confirme quem salvou. A conclusão é inferência forte, não prova.
- Não há `modelo-*.zip` depois de 13h50, nem `report-*.zip` depois de 13h51.

## 6. Recomendação

**Não aplicar agora.** Não há subconjunto seguro para aplicar parcialmente:
- Tour e guia formam um bloco. Os botões "?" (`T<n>_Aj_Guia`) já apontam para `T<n>_TOUR_01`, que só existe com o tour. O `montar_pbip` recusa a aplicação se o bookmark do link não existir. E as medidas do tour precisam estar no modelo antes do report (L018).
- A forma (c) não precisa ficar de fora. O `gerar_modelo --aplicar` regrava os 11 arquivos inteiros; o efeito é sair o `linguisticMetadata`, que o Desktop regenera, e o `PBI_ProTooling`. O `montar_pbip` regrava só arquivo com conteúdo diferente (compara JSON), então os 224 JSON de forma ficam como estão. O `wp-provisorio.svg` volta, e o Desktop deve tirá-lo de novo no próximo salvamento (é órfão, sem efeito visual).

**Ordem quando o tour estiver fechado:**
1. Confirmar que o `passos.json` gera sem erro (T4 passo 03 sem `KeyError`).
2. Regenerar os DAX do tour com `tour_lib.py` (sem `--previa`).
3. Rodar `gerar_modelo --conferir --sem-tom` e `montar_pbip --conferir`. Os dois devem ficar sem erro de conferência.
4. `gerar_modelo --aplicar`.
5. `montar_pbip --aplicar`.
6. Conferir de novo. Desktop fechado nos dois passos de aplicação (ambos checam).

Depois de aplicar, o `gerar_modelo --conferir` compara bytes: se alguém salvar no Desktop, ele acusa os mesmos 11 arquivos de forma. O `montar_pbip` compara JSON e não tem esse problema.

## Apoio (scratchpad, não faz parte do PBIP)

- `diff_apuracao.py`: plano × disco do modelo e do report. Saída em `saida_apuracao.txt`; diffs em `diff\`.
- `verificar.py` a `verificar7.py`: medidas, expressões, bookmarks e DAX do tour.
