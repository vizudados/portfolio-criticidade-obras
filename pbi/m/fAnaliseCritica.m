/*
@tipo: tabela
@descricao: Uma linha por obra × mês (aba mensal), de pInicioHistorico em diante. Valores do "quadradinho" como a planilha apresenta (área de impressão A132:J157), para bater centavo a centavo com o que a diretoria imprime; o resultado pela regra (recalculado das entradas e das tabelas anexadas) fica ao lado, para a conferência. As colunas *Anterior vêm da aba do mês anterior da mesma obra (lida mesmo antes do histórico), no lugar da referência manual entre abas.
@coluna: Obra | texto | | Obra (pelo nome do arquivo da planilha).
@coluna: Mes | data | formato=dd/mm/yyyy | Mês de referência (pelo nome da aba).
@coluna: Aba | texto | oculta | Nome da aba na planilha (JUN26, MAIO26…).
@coluna: Arquivo | texto | oculta | Arquivo de origem.
@coluna: Fonte | texto | oculta | Real ou Ilustrativo (planilha fictícia).
@coluna: TipoOrcamento | texto | oculta | Tipo do orçamento projetado (alvo, legal, preliminar, executivo, final).
@coluna: Orcamento | decimal | oculta; formato=#,0.00 | Orçamento da obra projetado (passo 3, com INCC no a realizar).
@coluna: PrevMes | decimal | oculta; formato=0.00% | % previsto do mês (passo 4).
@coluna: ExecMes | decimal | oculta; formato=0.00% | % executado do mês (passo 5).
@coluna: PrevAcum | decimal | oculta; formato=0.00% | % previsto acumulado (passo 6).
@coluna: ExecAcum | decimal | oculta; formato=0.00% | % executado acumulado (passo 7).
@coluna: Credito | decimal | oculta; formato=#,0.00 | Item 1 do quadradinho: crédito do orçamento (executado acumulado × orçamento).
@coluna: SaldoContrato | decimal | oculta; formato=#,0.00 | Item 2: saldo de contrato.
@coluna: AdiantServicos | decimal | oculta; formato=#,0.00 | Item 3: adiantamento de serviços não medidos.
@coluna: AdiantMateriais | decimal | oculta; formato=#,0.00 | Item 4: adiantamento de materiais não estocados.
@coluna: Estoque | decimal | oculta; formato=#,0.00 | Item 5: estoque de materiais.
@coluna: Equipamentos | decimal | oculta; formato=#,0.00 | Item 6: equipamentos (valor de mercado), como apresentado.
@coluna: ReceitaPersonalizacao | decimal | oculta; formato=#,0.00 | Item 7: receita de personalizações.
@coluna: ContasPagar | decimal | oculta; formato=#,0.00 | Item 8: contas a pagar dos medidos (subtrai).
@coluna: Desembolsado | decimal | oculta; formato=#,0.00 | Item 9: valor desembolsado pela obra, corrigido dos itens irregulares (subtrai).
@coluna: Divida | decimal | oculta; formato=#,0.00 | Item 10: dívida da obra a ser paga (soma, como na fórmula da planilha).
@coluna: Resultado | decimal | oculta; formato=#,0.00 | Resultado mensal da obra, como a planilha apresenta.
@coluna: ResultadoRegra | decimal | oculta; formato=#,0.00 | Resultado pela regra da planilha, recalculado das entradas e da soma das tabelas anexadas (conferência).
@coluna: ResultadoAnteriorPlanilha | decimal | oculta; formato=#,0.00 | "Resultado do mês anterior" como a aba mostra (referência manual; conferência).
@coluna: DesembolsadoBruto | decimal | oculta; formato=#,0.00 | Valor desembolsado digitado no passo 15 (antes de tirar os itens irregulares).
@coluna: ItensIrregulares | decimal | oculta; formato=#,0.00 | Soma dos itens apontados irregularmente.
@coluna: PrevistoMesRS | decimal | oculta; formato=#,0.00 | Valor previsto para o mês, em R$ (tabela informativa).
@coluna: DesembolsadoMesRS | decimal | oculta; formato=#,0.00 | Valor desembolsado no mês, em R$ (tabela informativa).
@coluna: Justificativa | texto | oculta | Justificativa da diferença entre previsto e desembolsado do mês.
@coluna: MesAnterior | data | oculta; formato=dd/mm/yyyy | Mês da aba anterior da mesma obra (vazio no primeiro mês da planilha).
@coluna: ResultadoAnterior | decimal | oculta; formato=#,0.00 | Resultado apresentado na aba anterior.
@coluna: OrcamentoAnterior | decimal | oculta; formato=#,0.00 | Orçamento da aba anterior.
@coluna: PrevAcumAnterior | decimal | oculta; formato=0.00% | % previsto acumulado da aba anterior.
@coluna: ExecAcumAnterior | decimal | oculta; formato=0.00% | % executado acumulado da aba anterior.
*/
let
    Origem = stgAbas,
    Validas = Table.SelectRows(Origem, each [Leitura][Layout] = true),
    // Uma aba por obra e mês: se a planilha tiver duas, a preliminar perde (ABRIL 2026 (RETA FINAL) × (PRELIMINAR));
    // entre as demais (ex.: MAI26 e MAIO26), vale a mais à direita
    // sem nenhuma aba lida, Table.Combine de lista vazia não tem colunas: a tabela vazia segue com as suas
    Unicas = if Table.RowCount(Validas) = 0 then Validas else Table.Combine(Table.Group(Validas, {"Obra", "Mes"},
        {{"T", each Table.FirstN(Table.Sort(_, {{"Preliminar", Order.Ascending}, {"OrdemAba", Order.Descending}}), 1),
            type table}})[T]),
    Campos = {"Projeto", "MesCelula", "TipoOrcamento", "Orcamento", "PrevMes", "ExecMes", "PrevAcum", "ExecAcum",
        "DesembolsadoBruto", "SomaSaldoContrato", "SomaAdiantServicos", "SomaAdiantMateriais", "SomaEstoque",
        "SomaEquipamentos", "SomaReceitaPersonalizacao", "SomaContasPagar", "SomaItensIrregulares", "SomaDivida",
        "QCredito", "QSaldoContrato", "QAdiantServicos", "QAdiantMateriais", "QEstoque", "QEquipamentos",
        "QReceitaPersonalizacao", "QContasPagar", "QDesembolsado", "QDivida", "ResultadoPlanilha", "ResultadoAnteriorPlanilha",
        "PrevistoMesRS", "DesembolsadoMesRS", "Justificativa"},
    Abertos = Table.ExpandRecordColumn(Unicas, "Leitura", Campos),
    Ou = (a as nullable number, b as number) as number => if a = null then b else a,

    // Valores do quadradinho (o que a planilha apresenta); sem valor salvo, cai na regra
    Apresentado = Table.AddColumn(Abertos, "Valores", each
        let
            CreditoRegra = [ExecAcum] * [Orcamento],
            DesembolsadoRegra = [DesembolsadoBruto] - [SomaItensIrregulares],
            ResultadoRegra = CreditoRegra + [SomaSaldoContrato] + [SomaAdiantServicos] + [SomaAdiantMateriais]
                + [SomaEstoque] + [SomaEquipamentos] + [SomaReceitaPersonalizacao] - [SomaContasPagar] - DesembolsadoRegra
                - [SomaDivida]    // versão 01 da planilha: a dívida da obra desconta (docs/08, L13)
        in
            [
                Credito = Ou([QCredito], CreditoRegra),
                SaldoContrato = Ou([QSaldoContrato], [SomaSaldoContrato]),
                AdiantServicos = Ou([QAdiantServicos], [SomaAdiantServicos]),
                AdiantMateriais = Ou([QAdiantMateriais], [SomaAdiantMateriais]),
                Estoque = Ou([QEstoque], [SomaEstoque]),
                Equipamentos = Ou([QEquipamentos], [SomaEquipamentos]),
                ReceitaPersonalizacao = Ou([QReceitaPersonalizacao], [SomaReceitaPersonalizacao]),
                ContasPagar = Ou([QContasPagar], [SomaContasPagar]),
                Desembolsado = Ou([QDesembolsado], DesembolsadoRegra),
                Divida = Ou([QDivida], [SomaDivida]),
                Resultado = Ou([ResultadoPlanilha], ResultadoRegra),
                ResultadoRegra = ResultadoRegra,
                ItensIrregulares = [SomaItensIrregulares]
            ]),
    Valores = Table.ExpandRecordColumn(Apresentado, "Valores", {"Credito", "SaldoContrato", "AdiantServicos",
        "AdiantMateriais", "Estoque", "Equipamentos", "ReceitaPersonalizacao", "ContasPagar", "Desembolsado", "Divida",
        "Resultado", "ResultadoRegra", "ItensIrregulares"}),

    // Aba anterior da mesma obra (a planilha liga o "mês anterior" por referência manual; aqui é pela ordem dos meses)
    ComAnterior = Table.Combine(Table.Group(Valores, {"Obra"}, {{"T", (t) =>
        let
            Ordenada = Table.Buffer(Table.Sort(t, {{"Mes", Order.Ascending}})),
            ComIndice = Table.AddIndexColumn(Ordenada, "i", 0, 1),
            ComAnt = Table.AddColumn(ComIndice, "Ant", each if [i] = 0 then null else Ordenada{[i] - 1})
        in
            ComAnt, type table}})[T]),
    Anterior = (r as nullable record, campo as text) as any => if r = null then null else Record.Field(r, campo),
    ComCamposAnteriores = Table.FromRecords(List.Transform(Table.ToRecords(ComAnterior), (r) =>
        Record.RemoveFields(r, {"i", "Ant"}) & [
            MesAnterior = Anterior(r[Ant], "Mes"),
            ResultadoAnterior = Anterior(r[Ant], "Resultado"),
            OrcamentoAnterior = Anterior(r[Ant], "Orcamento"),
            PrevAcumAnterior = Anterior(r[Ant], "PrevAcum"),
            ExecAcumAnterior = Anterior(r[Ant], "ExecAcum")
        ])),

    NoHistorico = Table.SelectRows(ComCamposAnteriores, each [Mes] >= pInicioHistorico),
    Colunas = Table.SelectColumns(NoHistorico, {"Obra", "Mes", "Aba", "Arquivo", "Fonte", "TipoOrcamento", "Orcamento",
        "PrevMes", "ExecMes", "PrevAcum", "ExecAcum", "Credito", "SaldoContrato", "AdiantServicos", "AdiantMateriais",
        "Estoque", "Equipamentos", "ReceitaPersonalizacao", "ContasPagar", "Desembolsado", "Divida", "Resultado",
        "ResultadoRegra", "ResultadoAnteriorPlanilha", "DesembolsadoBruto", "ItensIrregulares", "PrevistoMesRS",
        "DesembolsadoMesRS", "Justificativa", "MesAnterior", "ResultadoAnterior", "OrcamentoAnterior",
        "PrevAcumAnterior", "ExecAcumAnterior"}),
    Tipado = Table.TransformColumnTypes(Colunas, {
        {"Obra", type text}, {"Mes", type date}, {"Aba", type text}, {"Arquivo", type text}, {"Fonte", type text},
        {"TipoOrcamento", type text}, {"Orcamento", type number}, {"PrevMes", type number}, {"ExecMes", type number},
        {"PrevAcum", type number}, {"ExecAcum", type number}, {"Credito", type number}, {"SaldoContrato", type number},
        {"AdiantServicos", type number}, {"AdiantMateriais", type number}, {"Estoque", type number},
        {"Equipamentos", type number}, {"ReceitaPersonalizacao", type number}, {"ContasPagar", type number},
        {"Desembolsado", type number}, {"Divida", type number}, {"Resultado", type number},
        {"ResultadoRegra", type number}, {"ResultadoAnteriorPlanilha", type number},
        {"DesembolsadoBruto", type number}, {"ItensIrregulares", type number}, {"PrevistoMesRS", type number},
        {"DesembolsadoMesRS", type number}, {"Justificativa", type text}, {"MesAnterior", type date},
        {"ResultadoAnterior", type number}, {"OrcamentoAnterior", type number}, {"PrevAcumAnterior", type number},
        {"ExecAcumAnterior", type number}}),
    Ordenado = Table.Sort(Tipado, {{"Obra", Order.Ascending}, {"Mes", Order.Ascending}}),
    // sem nenhuma aba lida (pasta ausente ou vazia): tabela vazia com as colunas do cabeçalho (@coluna)
    Vazia = #table(type table [Obra = nullable text, Mes = nullable date, Aba = nullable text, Arquivo = nullable text,
        Fonte = nullable text, TipoOrcamento = nullable text, Orcamento = nullable number, PrevMes = nullable number,
        ExecMes = nullable number, PrevAcum = nullable number, ExecAcum = nullable number, Credito = nullable number,
        SaldoContrato = nullable number, AdiantServicos = nullable number, AdiantMateriais = nullable number,
        Estoque = nullable number, Equipamentos = nullable number, ReceitaPersonalizacao = nullable number,
        ContasPagar = nullable number, Desembolsado = nullable number, Divida = nullable number,
        Resultado = nullable number, ResultadoRegra = nullable number, ResultadoAnteriorPlanilha = nullable number,
        DesembolsadoBruto = nullable number, ItensIrregulares = nullable number, PrevistoMesRS = nullable number,
        DesembolsadoMesRS = nullable number, Justificativa = nullable text, MesAnterior = nullable date,
        ResultadoAnterior = nullable number, OrcamentoAnterior = nullable number, PrevAcumAnterior = nullable number,
        ExecAcumAnterior = nullable number], {})
in
    if Table.RowCount(stgAbas) = 0 then Vazia else Ordenado
