# Criticidade de Obras · instruções da sessão

Projeto de **portfólio da Vizu Dados**. Tudo em português do Brasil. **Comece por `HANDOFF.md`** e depois leia o fim de
`canal/CANAL.md`.

## Regras que não se negociam

- **Dados 100 % fictícios**, de uma construtora de **Natal/RN**: empreendimentos, bairros, títulos, clientes e valores
  inventados. Nunca use dado real de cliente da Vizu, nem nome de cliente da Vizu, em código, comentário, doc ou commit.
- **Imagem nenhuma é gerada nesta sessão.** Personagem, capa e artes saem da máquina local do Alisson, pelo Codex CLI.
  Se uma tarefa precisar de imagem nova, peça no canal e siga com o resto.
- A logo do painel é a da Vizu (`assets/logos/vizu-dados-horizontal.svg`).
- Tratamento de dados no **Power Query** (`pbi/m/`). O Python de `pipeline/` gera os dados fictícios e espelha as
  regras do M para conferir número; não aparece no painel.
- Medidas separadas em **conta** (todo cálculo) e **desenho** (HTML, texto, rótulo, só lê medidas). O PBIP é saída dos
  scripts: mude a fonte (`pbi/m`, `pbi/dax`, `pbi/scripts`, `pbi/spec`) e rode a montagem; não edite o PBIP à mão.

## Papéis

- **Sessão local (Alisson + orquestrador):** aprova propostas, gera imagens, publica o PBIP no workspace Power BI e
  confere o painel no navegador.
- **Sessão na nuvem:** pesquisa, dados fictícios, modelo, DAX, Power Query, ajustes de telas e montagem do PBIP. Não
  abre o Power BI Desktop; a conferência visual volta pelo canal.

## Canal (`canal/CANAL.md`)

- A sessão local manda mensagem direto para a sessão na nuvem e registra no canal. A nuvem não consegue mandar
  mensagem de volta: **responde escrevendo no canal, com commit e push.** Um vigia na máquina local avisa quando chega
  commit novo no canal.
- Cada entrada é acrescentada no fim, nunca editada:
  `## AAAA-MM-DD HH:MM · de: nuvem|local · tipo: entrega|pergunta|retorno|bloqueio` + texto curto + lista de arquivos.
- **Toda entrega termina com commit e push do branch de trabalho**, com a entrada do canal no mesmo commit.
- Pergunta que trava o trabalho: tipo `bloqueio`, e siga no que não depende dela.
