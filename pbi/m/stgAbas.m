/*
@tipo: consulta
@descricao: Consulta auxiliar (não carregada): as abas mensais da planilha Análise Crítica de cada obra, uma linha por obra × aba, com a leitura da aba (fxLerAba) num registro. A obra vem da subpasta (coluna pasta_analise_critica do cadastro); pasta fora do cadastro não entra. De cada obra vale uma planilha só: a que tem a aba mensal mais recente (empate: a modificada por último), entre os .xlsx cujo nome começa com "Análise Crítica", fora o que estiver marcado OBSOLETO no caminho ou no nome. Sem pasta no cadastro, a obra sai do nome do arquivo (planilha de exemplo, com FICTICIO no nome). Base de fAnaliseCritica, fItens, dItem e fConferencia.
*/
let
    Arquivos = fxArquivosPlanilhas,
    Planilhas = Table.SelectRows(Arquivos, each Text.Lower([Extension]) = ".xlsx"
        and Text.StartsWith(fxNormaliza([Name]), "analise critica")
        and not Text.StartsWith([Name], "~$")
        and not Text.Contains(fxNormaliza([Relativo] & " " & [Name]), "obsolet")),

    // Obra pela subpasta de primeiro nível, conforme o cadastro
    Pastas = Table.SelectRows(stgCadastro, each [Pasta] <> null),
    PorPasta = Table.RowCount(Pastas) > 0,
    Mapa = Record.FromList(Pastas[Obra], List.Transform(Pastas[Pasta], fxNormaliza)),
    ObraDaPasta = (relativo as text) as nullable text =>
        Record.FieldOrDefault(Mapa, fxNormaliza(Text.BeforeDelimiter(relativo, "\")), null),
    // Exemplos de nome sem pasta: "Analise Critica CAJUEIRO - jun26.xlsx", "Analise Critica PONTA NEGRA - jun26 (FICTICIO).xlsx"
    ObraDoArquivo = (nome as text) as text =>
        let
            Base = fxNormaliza(Text.BeforeDelimiter(nome, ".", {0, RelativePosition.FromEnd})),
            Resto = Text.Trim(Text.AfterDelimiter(Base, "analise critica")),
            Cortes = List.Select(List.Transform({"_", "(", " -"}, each Text.PositionOf(Resto, _)), each _ >= 0),
            Fim = if List.IsEmpty(Cortes) then Text.Length(Resto) else List.Min(Cortes)
        in
            Text.Upper(Text.Trim(Text.Start(Resto, Fim))),
    ComObra = Table.AddColumn(Planilhas, "Obra",
        each if PorPasta then ObraDaPasta([Relativo]) else ObraDoArquivo([Name]), type nullable text),
    DaCarteira = Table.SelectRows(ComObra, each [Obra] <> null),
    ComFonte = Table.AddColumn(DaCarteira, "Fonte",
        each if Text.Contains(fxNormaliza([Name]), "ficticio") then "Ilustrativo" else "Real", type text),

    // Índice das abas mensais de cada planilha (a leitura da aba vem depois, só da planilha escolhida)
    Folhas = Table.AddColumn(ComFonte, "Folhas", each
        let
            Pasta = Excel.Workbook([Content], null, true),
            SoAbas = Table.SelectRows(Pasta, each [Kind] = "Sheet"),
            ComOrdem = Table.AddIndexColumn(SoAbas, "OrdemAba", 1, 1),
            ComMes = Table.AddColumn(ComOrdem, "Mes", each fxMesDaAba([Name]), type nullable date),
            Mensais = Table.SelectRows(ComMes, each [Mes] <> null),
            ComOculta = if Table.HasColumns(Mensais, "Hidden") then Mensais else Table.AddColumn(Mensais, "Hidden", each false)
        in
            Table.SelectColumns(ComOculta, {"Name", "OrdemAba", "Mes", "Hidden", "Data"})),
    ComUltimo = Table.Buffer(Table.AddColumn(Folhas, "UltimoMes",
        each List.Max(Table.SelectRows([Folhas], each [Hidden] <> true)[Mes]), type nullable date)),
    // Uma planilha por obra: a que chega ao mês mais recente; as demais são versões anteriores ou cópias
    // sem nenhuma planilha (pasta ausente ou vazia), Table.Combine de lista vazia não tem colunas: a tabela vazia mantém as
    // colunas de ComUltimo, e as consultas de baixo seguem sem erro
    Escolhidas = if Table.RowCount(Table.SelectRows(ComUltimo, each [UltimoMes] <> null)) = 0
        then Table.FirstN(ComUltimo, 0)
        else Table.Combine(Table.Group(Table.SelectRows(ComUltimo, each [UltimoMes] <> null), {"Obra"},
        {{"T", each Table.FirstN(Table.Sort(_, {{"UltimoMes", Order.Descending}, {"Date modified", Order.Descending},
            {"Name", Order.Ascending}}), 1), type table}})[T]),

    Expandido = Table.ExpandTableColumn(Table.SelectColumns(Escolhidas, {"Name", "Obra", "Fonte", "Folhas"}), "Folhas",
        {"Name", "OrdemAba", "Mes", "Hidden", "Data"}, {"Aba", "OrdemAba", "Mes", "Oculta", "Data"}),
    Renomeado = Table.RenameColumns(Expandido, {{"Name", "Arquivo"}}),
    // Duas abas do mesmo mês (ABRIL 2026 (RETA FINAL) e (PRELIMINAR)): a preliminar perde para a outra
    ComPreliminar = Table.AddColumn(Renomeado, "Preliminar", each Text.Contains(fxNormaliza([Aba]), "preliminar"),
        type logical),
    ComLeitura = Table.AddColumn(ComPreliminar, "Leitura", each
        if [Oculta] = true then [Layout = false, Erro = "aba oculta"]
        else
            let Tentativa = try fxLerAba([Data])
            in if Tentativa[HasError] then [Layout = false, Erro = "aba ilegível: " & Tentativa[Error][Message]]
               else Tentativa[Value], type record),
    // Buffer: cada aba é lida uma vez por atualização, mesmo com as consultas de baixo percorrendo a tabela várias vezes
    // sem nenhuma planilha (pasta ausente ou vazia): tabela vazia com as mesmas colunas, para as consultas de baixo
    Final = if Table.RowCount(Escolhidas) = 0
        then #table({"Obra", "Fonte", "Arquivo", "Aba", "OrdemAba", "Preliminar", "Mes", "Oculta", "Leitura"}, {})
        else Table.Buffer(Table.SelectColumns(ComLeitura, {"Obra", "Fonte", "Arquivo", "Aba", "OrdemAba", "Preliminar", "Mes",
            "Oculta", "Leitura"}))
in
    Final
