/*
@tipo: funcao
@descricao: Lê uma aba mensal da planilha Análise Crítica e devolve um registro com as entradas (passos 1 a 16), as tabelas anexadas (soma das linhas, total que a planilha mostra e as linhas), o "quadradinho" como a planilha apresenta (área de impressão), a tabela informativa do desembolso e os textos de "significado de cada item". Tudo é achado pelo rótulo: as abas até JAN26 estão uma linha abaixo das de FEV26 em diante, e a origem da leitura (coluna A ou B) depende de como o arquivo foi salvo. Regras espelhadas de pipeline/extrair_analise_critica.py.
*/
(aba as table) as record =>
let
    // Listas em buffer: sem isso o M refaz a leitura da aba a cada busca de rótulo (listas são preguiçosas)
    Linhas = List.Buffer(Table.ToRows(aba)),
    NLinhas = List.Count(Linhas),
    Valor = (l as number, c as number) as any =>
        if l < 0 or l >= NLinhas then null
        else let linha = Linhas{l} in if c < 0 or c >= List.Count(linha) then null else linha{c},

    // Células com texto, com o rótulo normalizado: [L = linha, C = coluna, T = rótulo]
    Textos = List.Buffer(List.Combine(List.Transform({0 .. NLinhas - 1}, (l) =>
        let linha = Linhas{l} in
        List.RemoveNulls(List.Transform({0 .. List.Count(linha) - 1}, (c) =>
            let v = linha{c} in
            if v is text and Text.Trim(v) <> "" then [L = l, C = c, T = fxNormaliza(v)] else null))))),

    // Âncoras: o bloco de resultado e a coluna dos passos (coluna B da planilha)
    LinhaResultado = List.First(List.Transform(List.Select(Textos,
        each Text.StartsWith([T], "resultado para utilizar na apresentacao")), each [L]), null),
    ColunaB = List.First(List.Transform(List.Select(Textos, each Text.Contains([T], "projeto (definir")), each [C]), null),
    Layout = LinhaResultado <> null and ColunaB <> null,
    LinhaSignificado = List.First(List.Transform(List.Select(Textos,
        each Text.StartsWith([T], "significado de cada item")), each [L]), null),
    FimBloco = if LinhaSignificado <> null then LinhaSignificado else LinhaResultado + 30,
    Col = (x as number) as number => ColunaB + (x - 2),          // coluna da planilha (B = 2) → posição lida

    // ---- 1. Passos de entrada (rótulo na coluna B, acima do bloco de resultado)
    Passos = List.Select(Textos, each [L] < LinhaResultado and [C] = ColunaB),
    Acha = (teste as function) as nullable number => List.Last(List.Transform(List.Select(Passos, teste), each [L]), null),
    ValoresDaLinha = (l as number, c1 as number, c2 as number) as list =>
        List.Transform({Col(c1) .. Col(c2)}, each Valor(l, _)),
    UltimoNumero = (l as nullable number) as nullable number =>
        if l = null then null else List.Last(List.Select(ValoresDaLinha(l, 3, 12), each _ is number), null),
    UltimoTexto = (l as nullable number) as nullable text =>
        if l = null then null else List.Last(List.Select(ValoresDaLinha(l, 3, 12), each _ is text and Text.Trim(_) <> ""), null),
    PrimeiroValor = (l as nullable number) as any =>
        if l = null then null
        else List.First(List.Select(ValoresDaLinha(l, 3, 10), each _ <> null and not (_ is text and Text.Trim(_) = "")), null),
    // a primeira data da linha; sem data, o primeiro número de série plausível (30000 a 60000): o Excel.Workbook entrega
    // como número a data com formato personalizado ("mm/yyyy", como o LibreOffice grava)
    PrimeiraData = (l as nullable number) as nullable date =>
        if l = null then null
        else let
                vals = ValoresDaLinha(l, 3, 10),
                d = List.First(List.Select(vals, each _ is datetime or _ is date), null),
                n = List.First(List.Select(vals, each _ is number and _ >= 30000 and _ <= 60000), null)
             in if d <> null then Date.From(d) else if n <> null then Date.From(n) else null,
    Zero = (v as nullable number) as number => if v = null then 0 else v,

    LProjeto = Acha(each Text.Contains([T], "projeto (definir")),
    LMes = Acha(each Text.Contains([T], "mes de analise (definir")),
    LOrcamento = Acha(each Text.Contains([T], "orcamento da obra projetado")),
    LPrevMes = Acha(each Text.StartsWith([T], "4 passo") or Text.StartsWith([T], "4o passo")
        or Text.Contains([T], "previsto do mes (incluir")),
    LExecMes = Acha(each Text.Contains([T], "executado do mes (incluir")),
    LPrevAcum = Acha(each Text.Contains([T], "previsto acumulado do mes")),
    LExecAcum = Acha(each Text.Contains([T], "executado acumulado do mes")),
    LDesembolsado = Acha(each Text.Contains([T], "valor desembolsado pela obra")),
    DesembolsadoBruto = if LDesembolsado = null then null else Valor(LDesembolsado, Col(6)),

    // ---- 2. Tabelas anexadas: título → linhas até "Total"; valor três colunas à direita (B → E, G → J)
    Grupos = {
        {"saldo de contrato", "SaldoContrato"},
        {"adiantamento de materiais nao estocados", "AdiantMateriais"},
        {"adiantamento de servicos nao medidos", "AdiantServicos"},
        {"estoque de materiais", "Estoque"},
        {"equipamentos comprados", "Equipamentos"},
        // rótulo normalizado (sem acento): com acento a tabela nunca era achada (defeito achado na F2, 28/10/2026)
        {"receitas de personalizacoes", "ReceitaPersonalizacao"},
        {"contas a pagar dos medidos", "ContasPagar"},
        {"itens apontados irregularmente no relatorio", "ItensIrregulares"},
        {"divida da obra a ser paga", "Divida"}
    },
    LerTabela = (titulo as record, grupo as text) as record =>
        let
            L0 = titulo[L],
            C0 = titulo[C],
            Corpo = List.Generate(() => L0 + 1, each _ < L0 + 16 and fxNormaliza(Valor(_, C0)) <> "total", each _ + 1),
            LTotal = L0 + 1 + List.Count(Corpo),
            AchouTotal = LTotal < L0 + 16 and fxNormaliza(Valor(LTotal, C0)) = "total",
            Itens = List.RemoveNulls(List.Transform(Corpo, (l) =>
                let
                    v = Valor(l, C0 + 3),
                    d = Valor(l, C0),
                    Descricao = if d = null or Text.Trim(Text.From(d)) = "" then "(sem descrição)" else Text.Trim(Text.From(d))
                in
                    if v is number and v <> 0 then [Grupo = grupo, Descricao = Descricao, Valor = v] else null)),
            Soma = List.Sum(List.Transform(Itens, each [Valor])),
            Total = if AchouTotal then Valor(LTotal, C0 + 3) else null
        in
            [Grupo = grupo, Soma = Zero(Soma), TotalPlanilha = if Total is number then Total else null,
             TotalVazio = AchouTotal and Total = null, Itens = Itens],
    Tabelas = List.Buffer(List.Transform(Grupos, (g) =>
        let t = List.First(List.Select(Textos, each [L] < LinhaResultado and [T] = g{0}), null)
        in if t = null then [Grupo = g{1}, Soma = 0, TotalPlanilha = null, TotalVazio = false, Itens = {}]
           else LerTabela(t, g{1}))),
    Tabela = (grupo as text) as record => List.First(List.Select(Tabelas, each [Grupo] = grupo)),
    Soma = (grupo as text) as number => Tabela(grupo)[Soma],

    // ---- 3. Bloco de resultado (área de impressão, até "significado de cada item")
    Bloco = List.Select(Textos, each [L] >= LinhaResultado and [L] < FimBloco),
    AchaBloco = (teste as function) as nullable record => List.First(List.Select(Bloco, teste), null),
    NumeroOuNulo = (v as any) as nullable number => if v is number then v else null,
    NaColuna = (r as nullable record, x as number) as nullable number =>
        if r = null then null else NumeroOuNulo(Valor(r[L], Col(x))),
    RResultado = AchaBloco(each Text.StartsWith([T], "resultado mensal da obra")),
    RAnterior = AchaBloco(each Text.StartsWith([T], "resultado do mes anterior")),
    RPrevistoRS = AchaBloco(each Text.StartsWith([T], "valor previsto para")),
    RDesembolsadoRS = AchaBloco(each Text.StartsWith([T], "valor desembolsado") and [C] = Col(7)),
    RJustificativa = AchaBloco(each Text.StartsWith([T], "justificativa para diferenca")),
    RDiferenca = AchaBloco(each Text.StartsWith([T], "diferenca entre o previsto") and [C] = Col(7)),
    PrevistoMesRS = let v = NaColuna(RPrevistoRS, 10) in if v = 0 then null else v,
    DesembolsadoMesRS = let v = NaColuna(RDesembolsadoRS, 10) in if v = 0 then null else v,
    // Justificativa: há dois leiautes. Com rótulo ("Justificativa para diferença…" logo abaixo da "Diferença entre o
    // previsto…", texto na linha seguinte: CAJUEIRO e DUNAS) e sem rótulo (texto direto na coluna G, uma ou duas linhas
    // abaixo da "Diferença…": REDINHA G144 e TIROL G143 em 2026). Regra: o primeiro texto da coluna G nas 4 linhas
    // abaixo da "Diferença…", pulando o rótulo e parando num título de tabela ("Tabela informativa…"). Defeito achado
    // em 07/10/2026: só o leiaute com rótulo era lido, e jun/jul de REDINHA e TIROL saíam como "em branco".
    Justificativa =
        let
            base = if RDiferenca <> null then RDiferenca[L] else if RJustificativa <> null then RJustificativa[L] else null,
            candidatos = if base = null then {} else List.Transform({base + 1 .. base + 4}, each Valor(_, Col(7))),
            textos = List.Transform(candidatos, each if _ = null then "" else Text.Trim(Text.From(_))),
            ate = List.FirstN(textos, each not Text.StartsWith(fxNormaliza(_), "tabela informativa")),
            uteis = List.Select(ate, each _ <> "" and _ <> "-"
                and not Text.StartsWith(fxNormaliza(_), "justificativa para diferenca"))
        in
            List.First(uteis, null),
    // O quadradinho: itens 1 a 10 com o rótulo na coluna C e o valor na D
    Quadro = List.Select(Bloco, each [C] = Col(3)),
    Q = (prefixo as text) as nullable number =>
        let r = List.First(List.Select(Quadro, each Text.StartsWith([T], prefixo)), null) in NaColuna(r, 4),

    // ---- 4. Significado de cada item (texto de ajuda da própria planilha: rótulo e, na linha de baixo, o texto)
    Significados =
        if LinhaSignificado = null then {}
        else List.RemoveNulls(List.Transform(List.Select(Textos, each [L] > LinhaSignificado and Text.EndsWith([T], ":")),
            (r) =>
                let t = Valor(r[L] + 1, r[C])
                in if t is text and Text.Trim(t) <> "" then [Rotulo = Text.TrimEnd(r[T], ":"), Texto = Text.Trim(t)] else null)),

    Campos = [
        Layout = true,
        Projeto = PrimeiroValor(LProjeto),
        MesCelula = PrimeiraData(LMes),
        Orcamento = Zero(UltimoNumero(LOrcamento)),
        TipoOrcamento = if LOrcamento = null then null else UltimoTexto(LOrcamento + 1),
        // previsto em branco fica vazio (obra que não preenche o cronograma, ex.: JANGADA): zero viraria desvio falso
        PrevMes = UltimoNumero(LPrevMes),
        ExecMes = Zero(UltimoNumero(LExecMes)),
        PrevAcum = UltimoNumero(LPrevAcum),
        ExecAcum = Zero(UltimoNumero(LExecAcum)),
        DesembolsadoBruto = Zero(NumeroOuNulo(DesembolsadoBruto)),
        SomaSaldoContrato = Soma("SaldoContrato"),
        SomaAdiantServicos = Soma("AdiantServicos"),
        SomaAdiantMateriais = Soma("AdiantMateriais"),
        SomaEstoque = Soma("Estoque"),
        SomaEquipamentos = Soma("Equipamentos"),
        SomaReceitaPersonalizacao = Soma("ReceitaPersonalizacao"),
        SomaContasPagar = Soma("ContasPagar"),
        SomaItensIrregulares = Soma("ItensIrregulares"),
        SomaDivida = Soma("Divida"),
        Tabelas = Tabelas,
        QCredito = Q("credito do orcamento"),
        QSaldoContrato = Q("saldo de contrato"),
        QAdiantServicos = Q("adiantamento de servicos"),
        QAdiantMateriais = Q("adiantamento de materiais"),
        QEstoque = Q("estoque de materiais"),
        QEquipamentos = Q("equipamentos"),
        QReceitaPersonalizacao = Q("receita de personalizacoes"),
        QContasPagar = Q("contas a pagar"),
        QDesembolsado = Q("valor desembolsado"),
        QDivida = Q("divida da obra"),
        ResultadoPlanilha = NaColuna(RResultado, 4),
        ResultadoAnteriorPlanilha = NaColuna(RAnterior, 4),
        PrevistoMesRS = PrevistoMesRS,
        DesembolsadoMesRS = DesembolsadoMesRS,
        Justificativa = Justificativa,
        Significados = Significados
    ]
in
    if Layout then Campos else [Layout = false]
