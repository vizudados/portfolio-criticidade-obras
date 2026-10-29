/*
@tipo: tabela
@descricao: Os 10 itens do quadradinho, na ordem e com o sinal da fórmula do resultado (D155), e o texto de "significado de cada item" que a própria planilha traz (lido da aba mais recente que o tiver).
@coluna: Item | texto | chave | Código do item (igual ao nome da coluna em fAnaliseCritica).
@coluna: Ordem | inteiro | formato=0 | Posição no quadradinho (1 a 10).
@coluna: Rotulo | texto | ordenar=Ordem | Rótulo como na planilha.
@coluna: Sinal | inteiro | formato=0 | +1 soma no resultado; −1 subtrai.
@coluna: Ativo | logico | | Pago e ainda não virou obra (saldo de contrato, adiantamentos, estoque, equipamentos): sai do "resultado sem estoque e adiantamentos".
@coluna: Significado | texto | | Texto de ajuda da própria planilha ("significado de cada item").
*/
let
    Itens = #table(type table [Item = text, Ordem = Int64.Type, Rotulo = text, Sinal = Int64.Type, Ativo = logical, Chave = text], {
        {"Credito", 1, "Crédito do orçamento", 1, false, "credito do orcamento"},
        {"SaldoContrato", 2, "Saldo de contrato", 1, true, "saldo de contrato"},
        {"AdiantServicos", 3, "Adiant. de serviços não medidos", 1, true, "adiantamento de servicos nao medidos"},
        {"AdiantMateriais", 4, "Adiant. de materiais não estocados", 1, true, "adiantamento de materiais nao estocados"},
        {"Estoque", 5, "Estoque de materiais", 1, true, "estoque de materiais"},
        {"Equipamentos", 6, "Equipamentos (valor de mercado)", 1, true, "equipamentos (valor de mercado)"},
        {"ReceitaPersonalizacao", 7, "Receita de personalizações", 1, false, "receita de personalizacoes"},
        {"ContasPagar", 8, "Contas a pagar dos medidos", -1, false, "contas a pagar dos medidos"},
        {"Desembolsado", 9, "Valor desembolsado pela obra", -1, false, "valor desembolsado pela obra"},
        {"Divida", 10, "Dívida da obra a ser paga", -1, false, "divida da obra a ser paga"}
    }),
    // Textos de ajuda: da aba mais recente que tenha a seção "significado de cada item"
    ComTexto = Table.SelectRows(stgAbas, each [Leitura][Layout] = true
        and not List.IsEmpty(Record.FieldOrDefault([Leitura], "Significados", {}))),
    Recente = Table.FirstN(Table.Sort(ComTexto, {{"Fonte", Order.Descending}, {"Mes", Order.Descending}}), 1),
    Significados = if Table.IsEmpty(Recente) then {} else Recente{0}[Leitura][Significados],
    ComSignificado = Table.AddColumn(Itens, "Significado", (r) =>
        let s = List.First(List.Select(Significados, each [Rotulo] = r[Chave]), null)
        in if s = null then null else s[Texto], type text),
    Final = Table.SelectColumns(ComSignificado, {"Item", "Ordem", "Rotulo", "Sinal", "Ativo", "Significado"})
in
    Final
