/*
@tipo: tabela
@descricao: Mês de referência (seletor do drawer, de escolha única). Desconectada de propósito: as medidas leem o mês escolhido e os gráficos mês a mês mantêm o eixo do primeiro mês do histórico (pInicioHistorico) até ele. A primeira linha é o "Último mês", que acompanha a atualização: o seletor de escolha única marca a primeira linha quando nada está escolhido, e o rótulo dela muda a cada mês novo, então a escolha salva cai de volta nela.
@coluna: MesRef | data | formato=dd/mm/yyyy | Primeiro dia do mês (na linha "Último mês", o mais recente que pelo menos metade das obras já fechou).
@coluna: MesRefAno | texto | ordenar=OrdemRef | Rótulo curto: jun/26 (na linha automática, "último · jun/26").
@coluna: MesRefLongo | texto | chave; ordenar=OrdemRef | Rótulo longo: junho de 2026 (na linha automática, "Último mês · junho de 2026").
@coluna: OrdemRef | inteiro | oculta; formato=0 | Ordem no seletor: 0 = último mês automático; 1 = mês mais recente.
@coluna: Automatico | logico | oculta | Verdadeiro só na linha "Último mês" (não conta como filtro escolhido).
*/
let
    Origem = Table.SelectColumns(dMes, {"Mes", "MesAno", "MesAnoLongo", "Ordem"}),
    Renomeado = Table.RenameColumns(Origem, {{"Mes", "MesRef"}, {"MesAno", "MesRefAno"}, {"MesAnoLongo", "MesRefLongo"},
        {"Ordem", "OrdemRef"}}),
    Total = Table.RowCount(Renomeado),
    Meses = Table.AddColumn(
        Table.TransformColumns(Renomeado, {{"OrdemRef", each Total + 1 - _, Int64.Type}}),
        "Automatico", each false, type logical),
    // "Último mês" = o mais recente que pelo menos metade das obras já fechou: uma obra adiantada (aba de set/26 com
    // as outras em ago/26) não puxa a referência para um mês quase vazio; ela continua escolhível na lista
    PorMes = Table.Group(fAnaliseCritica, {"Mes"}, {{"Obras", each List.Count(List.Distinct([Obra])), Int64.Type}}),
    TotalObras = List.Count(List.Distinct(fAnaliseCritica[Obra])),
    Fechados = Table.SelectRows(PorMes, each [Obras] * 2 >= TotalObras),
    MesAuto = if Table.IsEmpty(Fechados) then List.Max(Renomeado[MesRef]) else List.Max(Fechados[Mes]),
    Ultimo = Table.First(Table.SelectRows(Renomeado, each [MesRef] = MesAuto)),
    Automatica = #table(
        type table [MesRef = date, MesRefAno = text, MesRefLongo = text, OrdemRef = Int64.Type, Automatico = logical],
        {{Ultimo[MesRef], "último · " & Ultimo[MesRefAno], "Último mês · " & Ultimo[MesRefLongo], 0, true}}),
    Tabela = if Total = 0 then Meses else Table.Combine({Automatica, Meses})
in
    Tabela
