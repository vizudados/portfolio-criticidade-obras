/*
@tipo: tabela
@descricao: Obra em foco das telas Análise crítica e Avanço físico (seletor de escolha única, no drawer). Desconectada de propósito. A primeira linha, "Mais crítica do mês", é a escolha automática: as medidas usam a obra de maior pontuação de criticidade no mês de referência entre as obras do recorte. O seletor de escolha única marca a primeira linha quando nada está escolhido.
@coluna: ObraFoco | texto | chave; ordenar=OrdemFoco | Obra (só as que têm planilha Análise Crítica), depois da linha automática.
@coluna: Selo | texto | | REAL ou ILUSTR. (vazio na linha automática).
@coluna: OrdemFoco | inteiro | oculta; formato=0 | Ordem no seletor: 0 = mais crítica do mês; depois, ordem alfabética.
@coluna: Automatico | logico | oculta | Verdadeiro só na linha "Mais crítica do mês" (não conta como filtro escolhido).
*/
let
    Origem = Table.SelectRows(dObra, each [TemAnaliseCritica] = true),
    Colunas = Table.SelectColumns(Origem, {"Obra", "Selo"}),
    Renomeado = Table.RenameColumns(Colunas, {{"Obra", "ObraFoco"}}),
    Ordenado = Table.Sort(Renomeado, {{"ObraFoco", Order.Ascending}}),
    ComOrdem = Table.AddIndexColumn(Ordenado, "OrdemFoco", 1, 1, Int64.Type),
    Obras = Table.AddColumn(ComOrdem, "Automatico", each false, type logical),
    Automatica = #table(type table [ObraFoco = text, Selo = text, OrdemFoco = Int64.Type, Automatico = logical],
        {{"Mais crítica do mês", null, 0, true}}),
    Tabela = Table.Combine({Automatica, Obras})
in
    Tabela
