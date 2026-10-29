/*
@tipo: parametro
@descricao: Cadastro de obras (CSV ";", UTF-8), relativo à raiz dos dados (pOrigem): obra, código, SPE, nome da obra na cronograma (nome_crono, vínculo explícito), fonte do dado físico, pasta da obra na análise crítica (pasta_analise_critica), bairro, unidades e entrega contratual. Situação, orçamento, tipo, m², início e término vêm da cronograma. Se o arquivo não existir, a atualização para: é o único arquivo sem o qual o painel não monta.
*/
"cadastro\obras_cadastro.csv" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]
