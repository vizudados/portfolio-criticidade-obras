# Criticidade de Obras · portfólio Vizu Dados

Painel Power BI de acompanhamento de obras de uma construtora fictícia de Natal/RN: avanço físico previsto ×
realizado, análise crítica do resultado da obra mês a mês e uma nota de desempenho por obra (Nota da obra). Tour guiado com
narradora e capa em filme.

**Todos os dados são fictícios.** Nomes de empreendimentos, bairros, clientes e valores foram inventados.

## Mapa

| Pasta | O que tem |
|---|---|
| `pbi/pbip/` | O relatório e o modelo (PBIP), gerados pelos scripts. Abra o `.pbip` no Power BI Desktop. |
| `pbi/m/` | Power Query de cada tabela e parâmetro (fonte de `expressions.tmdl` e das partições). |
| `pbi/dax/` | Medidas, uma por arquivo, separadas em conta e desenho. |
| `pbi/scripts/` | Geradores (`contas_*`, `desenho_*`, `leituras_*`, `tooltips_*`, `tour_lib`), montagem (`montar_pbip.py`) e conferências. |
| `pbi/spec/` | Especificações de casca, capa, tour, interações e redesenho. |
| `pipeline/` | Gerador dos dados fictícios e espelho em Python das regras do Power Query. |
| `dados/` | Os dados fictícios que o Power Query lê (planilhas, bases, cronograma, cadastro) e o gabarito do gerador. |
| `docs/` | Planilha de origem, indicadores e criticidade, briefs e specs de interação. |
| `canal/CANAL.md` | Conversa entre a sessão local e a sessão na nuvem. |

Comece por `HANDOFF.md`.
