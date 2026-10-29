/*
@tipo: tabela
@descricao: Linhas das tabelas anexadas de cada aba (estoque, adiantamentos, contas a pagar, itens irregulares…), uma por linha preenchida com valor diferente de zero, de pInicioHistorico em diante. É o detalhe que compõe cada item do quadradinho (tooltip da análise crítica).
@coluna: Obra | texto | | Obra.
@coluna: Mes | data | formato=dd/mm/yyyy | Mês de referência.
@coluna: Item | texto | | Item do quadradinho que a linha compõe (código de dItem; itens irregulares corrigem o desembolsado).
@coluna: Descricao | texto | | Descrição digitada na linha ("(sem descrição)" quando vazia).
@coluna: Valor | decimal | oculta; formato=#,0.00 | Valor da linha.
@coluna: Linha | inteiro | oculta; formato=0 | Ordem da linha dentro da tabela anexada.
*/
let
    Origem = Table.SelectRows(stgAbas, each [Leitura][Layout] = true and [Mes] >= pInicioHistorico),
    Unicas = Table.Combine(Table.Group(Origem, {"Obra", "Mes"},
        {{"T", each Table.FirstN(Table.Sort(_, {{"Preliminar", Order.Ascending}, {"OrdemAba", Order.Descending}}), 1),
            type table}})[T]),
    ItemDaTabela = [SaldoContrato = "SaldoContrato", AdiantServicos = "AdiantServicos",
        AdiantMateriais = "AdiantMateriais", Estoque = "Estoque", Equipamentos = "Equipamentos",
        ReceitaPersonalizacao = "ReceitaPersonalizacao", ContasPagar = "ContasPagar", ItensIrregulares = "Desembolsado",
        Divida = "Divida"],
    Linhas = List.Combine(List.Transform(Table.ToRecords(Unicas), (a) =>
        List.Combine(List.Transform(a[Leitura][Tabelas], (t) =>
            List.Transform(List.Positions(t[Itens]), (i) =>
                let it = t[Itens]{i} in
                [Obra = a[Obra], Mes = a[Mes], Item = Record.Field(ItemDaTabela, t[Grupo]),
                 Descricao = it[Descricao], Valor = it[Valor], Linha = i + 1]))))),
    Tabela = if List.IsEmpty(Linhas)
        then #table(type table [Obra = text, Mes = date, Item = text, Descricao = text, Valor = number, Linha = Int64.Type], {})
        else Table.FromRecords(Linhas),
    Tipado = Table.TransformColumnTypes(Tabela, {{"Obra", type text}, {"Mes", type date},
        {"Item", type text}, {"Descricao", type text}, {"Valor", type number}, {"Linha", Int64.Type}}),
    // sem nenhuma aba lida (pasta ausente ou vazia): tabela vazia com as colunas do cabeçalho (@coluna)
    Vazia = #table(type table [Obra = nullable text, Mes = nullable date, Item = nullable text, Descricao = nullable text,
        Valor = nullable number, Linha = nullable Int64.Type], {})
in
    if Table.RowCount(stgAbas) = 0 then Vazia else Tipado
