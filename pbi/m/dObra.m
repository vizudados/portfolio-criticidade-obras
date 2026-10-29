/*
@tipo: tabela
@descricao: Obras: as do cadastro (em andamento, a iniciar e concluídas), as que estão na cronograma sem estar no cadastro (entram assim mesmo, sem código nem SPE) e qualquer obra que tenha planilha Análise Crítica lida em stgAbas. Situação, orçamento, tipo, m², início e término vêm da cronograma (stgCrono), pelo nome da obra na cronograma (NomeCrono do cadastro); código e SPE vêm do cadastro. Fonte diz se o dado da obra é real (planilha da obra) ou ilustrativo (planilha de exemplo, com FICTICIO no nome); obra sem análise crítica é cronograma. Selo só aparece quando há planilha de exemplo na leitura: aí a real leva REAL e a de exemplo ILUSTR.; com todas reais, nenhuma leva selo.
@coluna: Obra | texto | chave | Nome da obra (do cadastro; obra só da cronograma leva o nome da cronograma).
@coluna: Codigo | texto | | Código do empreendimento no Fluxo de Caixa (cadastro).
@coluna: SPE | texto | | Sociedade de propósito específico (cadastro).
@coluna: Situacao | texto | ordenar=OrdemSituacao | Em andamento, A iniciar ou Concluída (cronograma: realizado acumulado ÷ orçamento).
@coluna: OrdemSituacao | inteiro | oculta; formato=0 | 1 em andamento · 2 a iniciar · 3 concluída · 9 sem situação na cronograma.
@coluna: TipoOrcamentoCrono | texto | | Tipo do orçamento na cronograma (versão em VersaoCrono).
@coluna: OrcamentoCrono | decimal | oculta; formato=#,0.00 | Orçamento na cronograma (versão em VersaoCrono).
@coluna: M2 | decimal | oculta; formato=#,0 | Área (m² NBR), da cronograma.
@coluna: Inicio | data | formato=dd/mm/yyyy | Início da obra (mês), da cronograma.
@coluna: TerminoPrevisto | data | formato=dd/mm/yyyy | Término previsto (mês), da cronograma.
@coluna: VersaoCrono | texto | | Versão da cronograma de onde vêm os campos (MM/AAAA, do nome do arquivo).
@coluna: Fonte | texto | | Real, Ilustrativo ou cronograma (só cronograma, sem análise crítica).
@coluna: Selo | texto | | ILUSTR. para planilha fictícia; REAL só quando há fictícia na leitura; vazio nos demais casos.
@coluna: TemAnaliseCritica | logico | | A obra tem planilha Análise Crítica lida.
@coluna: Bairro | texto | | Bairro da obra (cadastro).
@coluna: Unidades | inteiro | formato=0 | Unidades do empreendimento (cadastro).
@coluna: EntregaContratual | data | formato=dd/mm/yyyy | Entrega contratual (cadastro): base do prazo com a tolerância de 180 dias.
*/
let
    Cadastro = Table.SelectColumns(stgCadastro, {"Obra", "Codigo", "SPE", "NomeCrono"}),
    Crono = Table.SelectRows(stgCrono, each [ObraCrono] <> null),

    // Fonte de cada obra pelas planilhas lidas (real vence ilustrativo)
    Planilhas = Table.Group(Table.SelectColumns(stgAbas, {"Obra", "Fonte"}), {"Obra"},
        {{"FontePlanilha", each if List.Contains([Fonte], "Real") then "Real" else "Ilustrativo", type text}}),
    TemFicticia = List.Contains(Planilhas[FontePlanilha], "Ilustrativo"),

    // o cadastro leva a cronograma pelo nome da obra na cronograma (vínculo explícito, sem fuzzy)
    ComCrono = Table.NestedJoin(Cadastro, {"NomeCrono"}, Crono, {"ObraCrono"}, "G", JoinKind.LeftOuter),
    DoCadastro = Table.ExpandTableColumn(ComCrono, "G",
        {"TipoOrcamento", "Orcamento", "M2", "Inicio", "TerminoPrevisto", "Situacao", "VersaoCrono"},
        {"TipoOrcamentoCrono", "OrcamentoCrono", "M2", "Inicio", "TerminoPrevisto", "Situacao", "VersaoCrono"}),
    NomesNoCadastro = List.Select(Cadastro[NomeCrono], each _ <> null),

    // obra da cronograma que não está no cadastro: entra assim mesmo, sem código nem SPE (aviso em fConferencia)
    // (e não entra a cronograma cujo nome já é de uma obra do cadastro sem nome_crono: a chave Obra não pode repetir)
    SoCrono = Table.SelectRows(Crono, each not List.Contains(NomesNoCadastro, [ObraCrono]) and not List.Contains(Cadastro[Obra], [ObraCrono])),
    Forma = type table [Obra = text, Codigo = nullable text, SPE = nullable text, Situacao = nullable text,
        TipoOrcamentoCrono = nullable text, OrcamentoCrono = nullable number, M2 = nullable number,
        Inicio = nullable date, TerminoPrevisto = nullable date, VersaoCrono = nullable text],
    NovasCrono = Table.FromRecords(List.Transform(Table.ToRecords(SoCrono), (r) => [Obra = r[ObraCrono], Codigo = null,
        SPE = null, Situacao = r[Situacao], TipoOrcamentoCrono = r[TipoOrcamento], OrcamentoCrono = r[Orcamento],
        M2 = r[M2], Inicio = r[Inicio], TerminoPrevisto = r[TerminoPrevisto], VersaoCrono = r[VersaoCrono]]), Forma),

    // obra só com planilha Análise Crítica (fora do cadastro e da cronograma): em andamento, como antes
    NomesJa = List.Combine({Cadastro[Obra], Table.Column(NovasCrono, "Obra")}),
    SoNasPlanilhas = Table.SelectRows(Planilhas, each not List.Contains(NomesJa, [Obra])),
    NovasPlanilhas = Table.FromRecords(List.Transform(SoNasPlanilhas[Obra], (o) => [Obra = o, Codigo = null, SPE = null,
        Situacao = "Em andamento", TipoOrcamentoCrono = null, OrcamentoCrono = null, M2 = null, Inicio = null,
        TerminoPrevisto = null, VersaoCrono = null]), Forma),

    Todas = Table.Combine({Table.SelectColumns(DoCadastro, {"Obra", "Codigo", "SPE", "Situacao", "TipoOrcamentoCrono",
        "OrcamentoCrono", "M2", "Inicio", "TerminoPrevisto", "VersaoCrono"}), NovasCrono, NovasPlanilhas}),
    ComFonte = Table.NestedJoin(Todas, {"Obra"}, Planilhas, {"Obra"}, "P", JoinKind.LeftOuter),
    Expandido = Table.ExpandTableColumn(ComFonte, "P", {"FontePlanilha"}),
    Final = Table.FromRecords(List.Transform(Table.ToRecords(Expandido), (r) =>
        let Fonte = if r[FontePlanilha] = null then "cronograma" else r[FontePlanilha] in
        Record.RemoveFields(r, {"FontePlanilha"}) & [
            OrdemSituacao = if r[Situacao] = "Em andamento" then 1 else if r[Situacao] = "A iniciar" then 2
                else if r[Situacao] = "Concluída" then 3 else 9,
            Fonte = Fonte,
            Selo = if Fonte = "Ilustrativo" then "ILUSTR." else if Fonte = "Real" and TemFicticia then "REAL" else "",
            TemAnaliseCritica = r[FontePlanilha] <> null
        ])),
    Ordenado = Table.SelectColumns(Final, {"Obra", "Codigo", "SPE", "Situacao", "OrdemSituacao", "TipoOrcamentoCrono",
        "OrcamentoCrono", "M2", "Inicio", "TerminoPrevisto", "VersaoCrono", "Fonte", "Selo", "TemAnaliseCritica"}),
    TipadoFinal = Table.TransformColumnTypes(Ordenado, {{"Obra", type text}, {"Codigo", type text}, {"SPE", type text},
        {"Situacao", type text}, {"OrdemSituacao", Int64.Type}, {"TipoOrcamentoCrono", type text},
        {"OrcamentoCrono", type number}, {"M2", type number}, {"Inicio", type date}, {"TerminoPrevisto", type date},
        {"VersaoCrono", type text}, {"Fonte", type text}, {"Selo", type text}, {"TemAnaliseCritica", type logical}}),
    // bairro, unidades e entrega contratual vêm do cadastro (obra fora do cadastro: vazios)
    Extras = Table.SelectColumns(stgCadastro, {"Obra", "Bairro", "Unidades", "EntregaContratual"}),
    ComExtras = Table.ExpandTableColumn(Table.NestedJoin(TipadoFinal, {"Obra"}, Extras, {"Obra"}, "C", JoinKind.LeftOuter),
        "C", {"Bairro", "Unidades", "EntregaContratual"}),
    Saida = Table.TransformColumnTypes(ComExtras, {{"Bairro", type text}, {"Unidades", Int64.Type},
        {"EntregaContratual", type date}})
in
    Saida
