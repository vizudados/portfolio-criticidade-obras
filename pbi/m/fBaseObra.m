/*
@tipo: tabela
@descricao: Bases complementares (modelo BC 2.0): uma linha por obra × mês com algum campo preenchido (a aba que vale em stgAbasBase), de pInicioHistorico em diante, só com o VALOR CRU que foi digitado na base. Faixas, pontos e nota ficam na DAX (dicionário NOTA nas contas do painel). Texto onde se espera número chega vazio (o aviso vai para fConferencia); número fora da faixa válida chega como foi digitado e a DAX o trata como sem dado. Acidentes12m, HHT12m e DiasPerdidos12m somam os 12 meses até o da linha (inclusive os anteriores ao histórico), para as taxas de frequência e de gravidade da NBR 14280. Obra × mês sem base (ou com a aba vazia) não tem linha.
@coluna: Obra | texto | | Obra (pelo nome do arquivo da base).
@coluna: Mes | data | formato=dd/mm/yyyy | Mês de referência (pelo nome da aba).
@coluna: Gestor | texto | | Gestor da obra.
@coluna: PPC | decimal | oculta; formato=0.00% | PPC do mês: pacotes concluídos ÷ planejados (fração).
@coluna: ServicosVerificados | decimal | oculta; formato=0 | Serviços verificados no mês (FVS).
@coluna: AprovadosPrimeira | decimal | oculta; formato=0 | Serviços aprovados na primeira inspeção.
@coluna: HHT | decimal | oculta; formato=#,0 | Horas-homem trabalhadas no mês.
@coluna: Acidentes | decimal | oculta; formato=0 | Acidentes com afastamento no mês.
@coluna: DiasPerdidos | decimal | oculta; formato=0 | Dias perdidos por acidente no mês (NBR 14280).
@coluna: NR18Aplicaveis | decimal | oculta; formato=0 | Itens aplicáveis do checklist NR-18 no mês.
@coluna: NR18Conformes | decimal | oculta; formato=0 | Itens conformes do checklist NR-18 no mês.
@coluna: PedidosPrevistos | decimal | oculta; formato=0 | Pedidos com entrega prevista no mês.
@coluna: PedidosNoPrazo | decimal | oculta; formato=0 | Pedidos entregues no prazo e completos.
@coluna: DiasChuva | decimal | oculta; formato=0 | Dias impraticáveis por chuva no mês.
@coluna: Acidentes12m | decimal | oculta; formato=0 | Acidentes com afastamento nos 12 meses até o mês.
@coluna: HHT12m | decimal | oculta; formato=#,0 | Horas-homem trabalhadas nos 12 meses até o mês.
@coluna: DiasPerdidos12m | decimal | oculta; formato=0 | Dias perdidos por acidente nos 12 meses até o mês.
@coluna: Arquivo | texto | oculta | Arquivo da base.
@coluna: Aba | texto | oculta | Aba da base (SET 2026).
*/
let
    Numericos = {"PPC", "ServicosVerificados", "AprovadosPrimeira", "HHT", "Acidentes", "DiasPerdidos", "NR18Aplicaveis",
        "NR18Conformes", "PedidosPrevistos", "PedidosNoPrazo", "DiasChuva"},
    Campos = {"Gestor"} & Numericos,
    // todas as abas que valem (também as anteriores ao histórico, para a janela de 12 meses dos acidentes)
    Todas = Table.Buffer(Table.ExpandRecordColumn(
        Table.SelectColumns(Table.SelectRows(stgAbasBase, each [Vale] and [Preenchida]), {"Obra", "Mes", "Valores", "Arquivo", "Aba"}),
        "Valores", Campos)),
    Soma12 = (obra as text, mes as date, campo as text) as nullable number =>
        let
            Janela = Table.SelectRows(Todas, each [Obra] = obra and [Mes] <= mes and [Mes] > Date.AddMonths(mes, -12)),
            Valores = List.RemoveNulls(Table.Column(Janela, campo))
        in
            if List.IsEmpty(Valores) then null else List.Sum(Valores),
    NoHistorico = Table.SelectRows(Todas, each [Mes] >= pInicioHistorico),
    ComJanela = Table.AddColumn(Table.AddColumn(Table.AddColumn(NoHistorico,
        "Acidentes12m", each Soma12([Obra], [Mes], "Acidentes")),
        "HHT12m", each Soma12([Obra], [Mes], "HHT")),
        "DiasPerdidos12m", each Soma12([Obra], [Mes], "DiasPerdidos")),
    Doze = {"Acidentes12m", "HHT12m", "DiasPerdidos12m"},
    Colunas = Table.SelectColumns(ComJanela, {"Obra", "Mes", "Gestor"} & Numericos & Doze & {"Arquivo", "Aba"}),
    Tipado = Table.TransformColumnTypes(Colunas,
        {{"Obra", type text}, {"Mes", type date}, {"Gestor", type text}}
        & List.Transform(Numericos & Doze, each {_, type number})
        & {{"Arquivo", type text}, {"Aba", type text}}),
    Ordenado = Table.Sort(Tipado, {{"Obra", Order.Ascending}, {"Mes", Order.Ascending}})
in
    Ordenado
