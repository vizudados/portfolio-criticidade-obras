/*
@tipo: consulta
@descricao: Consulta auxiliar (não carregada): o cadastro de obras (pCadastroObras, relativo à raiz dos dados de pOrigem) tipado, uma linha por obra, só com o que é do cadastro: código, SPE, o nome da obra na cronograma (NomeCrono, vínculo explícito com stgCrono), a pasta da obra em análise crítica (coluna Pasta: vazia = obra sem análise crítica no painel), o bairro, as unidades e a entrega contratual. Situação, orçamento, tipo, m², início e término vêm da cronograma (stgCrono).
*/
let
    Csv = Csv.Document(fxConteudoOrigem(pCadastroObras), [Delimiter = ";", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Cabecalho = Table.PromoteHeaders(Csv, [PromoteAllScalars = true]),
    SemBOM = Table.TransformColumnNames(Cabecalho, each Text.Replace(_, "#(FEFF)", "")),
    ComPasta = if Table.HasColumns(SemBOM, "pasta_analise_critica") then SemBOM
        else Table.AddColumn(SemBOM, "pasta_analise_critica", each null),
    ComNome = if Table.HasColumns(ComPasta, "nome_crono") then ComPasta
        else Table.AddColumn(ComPasta, "nome_crono", each null),
    // colunas da versão de 28/10/2026 (dados fictícios): sem elas, vazias
    ComExtras = List.Accumulate({"bairro", "unidades", "entrega_contratual"}, ComNome,
        (t, c) => if Table.HasColumns(t, c) then t else Table.AddColumn(t, c, each null)),
    Renomeado = Table.RenameColumns(ComExtras, {{"obra", "Obra"}, {"codigo", "Codigo"}, {"spe", "SPE"},
        {"nome_crono", "NomeCrono"}, {"pasta_analise_critica", "Pasta"}, {"bairro", "Bairro"}, {"unidades", "Unidades"},
        {"entrega_contratual", "EntregaContratual"}}),
    Vazio = (t as nullable text) as nullable text => if t = null or Text.Trim(t) = "" then null else Text.Trim(t),
    Maiusc = (t as nullable text) as nullable text => if t = null or Text.Trim(t) = "" then null else Text.Upper(Text.Trim(t)),
    Tipado = Table.TransformColumns(Renomeado, {
        {"Obra", each Text.Upper(Text.Trim(_)), type text},
        {"NomeCrono", Maiusc, type nullable text},
        {"Pasta", Vazio, type nullable text},
        {"Bairro", Vazio, type nullable text},
        {"Unidades", each try Number.From(_) otherwise null, type nullable number},
        // data ISO (AAAA-MM-DD), mês do primeiro dia
        {"EntregaContratual", each try Date.StartOfMonth(Date.FromText(Text.Trim(_), [Format = "yyyy-MM-dd"])) otherwise null,
            type nullable date}})
in
    Table.SelectColumns(Tipado, {"Obra", "Codigo", "SPE", "NomeCrono", "Pasta", "Bairro", "Unidades", "EntregaContratual"})
