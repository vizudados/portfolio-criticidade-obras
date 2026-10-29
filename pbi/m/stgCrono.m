/*
@tipo: consulta
@descricao: Consulta auxiliar (não carregada): a cronograma de cada obra, uma linha por obra da aba PREVXREA (a de mês mais recente no nome) da planilha de versão mais recente (fxArquivosCrono; versão no nome ATUALIZADO EM MMAAAA). Os campos são achados pelo rótulo do cabeçalho, nunca pelo endereço. Orcamento = ORÇ OBRA RESULTADO; M2 = M2 EQUIVALENTE (NBR); TipoOrcamento = TIPO DE ORÇAMENTO com a inicial maiúscula (Final, Preliminar, Executivo, Legal). Situacao = Concluída se o REALIZADO ACUMULADO chega a 99% do orçamento, A iniciar se fica abaixo de 0,5%, senão Em andamento. Inicio = na obra A iniciar, o primeiro mês com previsto depois do mês de corte (coluna PREVISTO); nas demais, o primeiro mês da aba FLUXO-FINACEIRO da obra (coluna MÊS, mesmo com custo zero; a linha ACUMULADO-MM/AA conta como MM/AA); sem aba, vazio. TerminoPrevisto = o último mês com previsto diferente de zero na PREVXREA (PREVISTO e os meses depois de DESVIO). Obra = nome na cronograma, vínculo explícito com nome_crono do cadastro (sem fuzzy). Curva = a aba FLUXO-FINACEIRO da obra, lista de [Mes, Custo] (a curva prevista, base de fCurvaPrevista), com MÊS e CUSTO PREVISTO achados pelo rótulo do cabeçalho. Problemas (pasta, arquivo, aba, layout, curva de uma aba FLUXO que não fecha no orçamento, obra repetida) vão na coluna Problemas, lista de registros [Aba, Regra, Severidade, Detalhe], para fConferencia; pasta ou arquivo ausente vira uma linha sem ObraCrono. Nunca quebra a atualização.
*/
let
    Rotulo = (v as any) as text => fxNormaliza(v),
    Chave = (v as any) as text => if v = null then "" else Text.Upper(Text.Trim(Text.From(v))),
    Num = (v as any) as nullable number => if v = null then null else try Number.From(v) otherwise null,
    // data: o Excel.Workbook só entrega como data a célula com formato de data EMBUTIDO do Excel; com formato
    // personalizado ("mmm/yy", como o LibreOffice grava) chega o número de série. Aceita os dois: um número de 30000 a
    // 60000 (de 1982 a 2064) é lido como data (Date.From: 1899-12-30 + n)
    EhData = (v as any) as logical => v is datetime or v is date or (v is number and v >= 30000 and v <= 60000),
    MesDeData = (v as any) as nullable date =>
        if not EhData(v) then null
        else let d = if v is number then Date.From(v) else v in #date(Date.Year(d), Date.Month(d), 1),

    // rótulo de mês da coluna MÊS: data, ou "ACUMULADO-MM/AA" (linha de realizado acumulado da cronograma, conta como MM/AA)
    MesDaCelula = (v as any) as nullable date =>
        if EhData(v) then MesDeData(v)
        else if v is text and Text.StartsWith(Text.Upper(Text.Trim(v)), "ACUMULADO-") then
            let
                parte = Text.Split(Text.AfterDelimiter(Text.Trim(v), "-"), "/"),
                mes = try Number.From(Text.Trim(parte{0})) otherwise null,
                ano = try Number.From(Text.Trim(parte{1})) otherwise null
            in
                if mes <> null and ano <> null and mes >= 1 and mes <= 12 then #date(2000 + ano, mes, 1) else null
        else null,

    // obra da aba FLUXO-FINACEIRO <ESTÁGIO> <OBRA>: tira o prefixo e os estágios (PRE, EX, VI, LE)
    ObraDaAba = (nome as text) as text =>
        let
            tokens = List.Select(Text.Split(Text.Upper(fxNormaliza(nome)), " "), each _ <> ""),
            semPrefixo = if List.Count(tokens) > 0 and List.Contains({"FLUXO-FINACEIRO", "FLUXO-FINANCEIRO"}, tokens{0})
                then List.Skip(tokens, 1) else tokens,
            semEstagio = List.Skip(semPrefixo, each List.Contains({"PRE", "EX", "VI", "LE"}, _))
        in
            Text.Combine(semEstagio, " "),

    // mês de referência da aba PREVXREA pelo nome ("PREVXREA ABR 26" -> 202604); 0 quando não acha
    ChaveMesAba = (nome as text) as number =>
        let
            tokens = List.Select(Text.Split(Text.Upper(fxNormaliza(nome)), " "), each _ <> ""),
            meses = [JAN = 1, FEV = 2, MAR = 3, ABR = 4, MAI = 5, JUN = 6, JUL = 7, AGO = 8, SET = 9, OUT = 10, NOV = 11, DEZ = 12],
            mes = List.Select(List.Transform(tokens, each Record.FieldOrDefault(meses, _, null)), each _ <> null),
            anos = List.Transform(List.Select(tokens, each Text.Length(_) >= 2 and Text.Select(_, {"0".."9"}) = _),
                each let n = Number.From(_) in if Text.Length(_) = 2 then 2000 + n else n),
            mes1 = if List.IsEmpty(mes) then null else mes{0},
            ano1 = if List.IsEmpty(anos) then null else anos{0}
        in
            if mes1 = null or ano1 = null then 0 else ano1 * 100 + mes1,

    // ---------- arquivo: o de versão mais recente (ATUALIZADO EM MMAAAA; sem isso, a data de modificação)
    Arquivos = fxArquivosCrono,
    ErrosPasta = Table.SelectRows(Arquivos, each [ErroPasta] <> null),
    TemErroPasta = Table.RowCount(ErrosPasta) > 0,
    Candidatos = Table.SelectRows(Arquivos, each [ErroPasta] = null
        and Text.StartsWith(fxNormaliza([Name]), fxNormaliza(pPrefixoCrono))
        and Text.Lower(Text.End([Name], 5)) = ".xlsx"
        and not Text.StartsWith([Name], "~$")),
    DigitosVersao = (nome as text) as text =>
        let s = try Text.BetweenDelimiters(Text.Upper(nome), "ATUALIZADO EM ", ".") otherwise ""
        in Text.Select(s, {"0".."9"}),
    VersaoNoNome = (nome as text) as logical => Text.Length(DigitosVersao(nome)) = 6,
    ChaveVersao = (nome as text) as number =>
        let d = DigitosVersao(nome)
        in if Text.Length(d) = 6 then Number.From(Text.End(d, 4) & Text.Start(d, 2)) else 0,
    VersaoDe = (nome as text, modificado as any) as text =>
        let d = DigitosVersao(nome)
        in if Text.Length(d) = 6 then Text.Start(d, 2) & "/" & Text.End(d, 4)
           else try Date.ToText(DateTime.Date(modificado), "MM/yyyy") otherwise "",
    ComChave = Table.AddColumn(Candidatos, "ChaveVersao", each ChaveVersao([Name]), type number),
    Ordenado = Table.Sort(ComChave, {{"ChaveVersao", Order.Descending}, {"Date modified", Order.Descending}}),
    TemArquivo = Table.RowCount(Ordenado) > 0,
    Arquivo = if TemArquivo then Ordenado{0} else null,
    NomeArq = if TemArquivo then Arquivo[Name] else null,
    VersaoArq = if TemArquivo then VersaoDe(Arquivo[Name], Arquivo[Date modified]) else null,
    Tentativa = if TemArquivo then try Excel.Workbook(Arquivo[Content], false, true) else null,
    TemPasta = TemArquivo and Tentativa <> null and not Tentativa[HasError],
    ArquivoIlegivel = TemArquivo and Tentativa <> null and Tentativa[HasError],
    Abas = if TemPasta then Table.SelectRows(Tentativa[Value], each [Kind] = "Sheet")
        else #table(type table [Name = text, Kind = text, Data = table], {}),

    // ---------- PREVXREA: a de mês mais recente no nome; rótulos do cabeçalho (linha com OBRA)
    Previ = Table.SelectRows(Abas, each Text.StartsWith(fxNormaliza([Name]), "prevxrea")),
    NumPrevi = Table.RowCount(Previ),
    PreviOrd = Table.Sort(Table.AddColumn(Previ, "MesAba", each ChaveMesAba([Name]), type number),
        {{"MesAba", Order.Descending}, {"Name", Order.Ascending}}),
    NomeAba = if NumPrevi = 0 then null else PreviOrd{0}[Name],
    Linhas = if NumPrevi = 0 then {} else Table.ToRows(PreviOrd{0}[Data]),
    H = List.First(List.Select(List.FirstN(List.Positions(Linhas), 15), each Rotulo(Linhas{_}{0}) = "obra"), null),
    CabLinha = if H = null then {} else Linhas{H},
    DatasLinha = if H = null or H + 1 >= List.Count(Linhas) then {} else Linhas{H + 1},
    Coluna = (criterio as function) as nullable number =>
        List.First(List.Select(List.Positions(CabLinha), each criterio(Rotulo(CabLinha{_}))), null),
    colObra = Coluna((r as text) as logical => r = "obra"),
    colTipo = Coluna((r as text) as logical => Text.StartsWith(r, "tipo de orcamento")),
    colM2 = Coluna((r as text) as logical => Text.StartsWith(r, "m2 equivalente")),
    colOrc = Coluna((r as text) as logical => Text.StartsWith(r, "orc obra resultado")),
    colReal = Coluna((r as text) as logical => r = "realizado acumulado"),
    colPrev = Coluna((r as text) as logical => r = "previsto"),
    colDesv = Coluna((r as text) as logical => r = "desvio"),
    Faltam = List.Select({
        if colObra = null then "OBRA" else "",
        if colOrc = null then "ORÇ OBRA RESULTADO" else "",
        if colPrev = null then "PREVISTO" else "",
        if colDesv = null then "DESVIO" else "",
        if colReal = null then "REALIZADO ACUMULADO" else ""}, each _ <> ""),
    LayoutOk = NumPrevi > 0 and List.IsEmpty(Faltam),
    // previsto mensal: a coluna PREVISTO (mês de corte) e as colunas de mês depois de DESVIO
    ColsPrev = if not LayoutOk then {} else List.Select(List.Positions(CabLinha),
        each _ = colPrev or (_ > colDesv and EhData(DatasLinha{_}))),
    Corte = if not LayoutOk then null else MesDeData(DatasLinha{colPrev}),

    // ---------- abas FLUXO-FINACEIRO: a curva de cada obra. O mês e o custo previsto são achados pelo rótulo do
    // cabeçalho (MÊS e CUSTO PREVISTO, numa das 15 primeiras linhas), nunca pela posição: o Excel.Workbook começa a aba
    // na primeira célula usada, então uma coluna A vazia desloca tudo (a curva saía vazia com a aba em B3)
    AbasFluxo = Table.SelectRows(Abas, each Text.StartsWith(fxNormaliza([Name]), "fluxo-fina")),
    LeAbaFluxo = (aba as record) as record =>
        let
            tent = try (
                let
                    linhas = Table.ToRows(aba[Data]),
                    rotulos = (l as list) as list => List.Transform(l, Rotulo),
                    h = List.First(List.Select(List.FirstN(List.Positions(linhas), 15),
                        each List.Contains(rotulos(linhas{_}), "mes") and List.Contains(rotulos(linhas{_}), "custo previsto")),
                        null),
                    cab = if h = null
                        then error Error.Record("Layout", "cabeçalho com MÊS e CUSTO PREVISTO não encontrado")
                        else rotulos(linhas{h}),
                    cMes = List.PositionOf(cab, "mes"),
                    cCusto = List.PositionOf(cab, "custo previsto"),
                    regs = List.Transform(List.Skip(linhas, h + 1), each [Mes = MesDaCelula(_{cMes}), Custo = Num(_{cCusto})])
                in
                    List.Select(regs, each [Mes] <> null))
        in
            if tent[HasError]
            then [Aba = aba[Name], Chave = ObraDaAba(aba[Name]), Linhas = {}, Erro = tent[Error][Message]]
            else [Aba = aba[Name], Chave = ObraDaAba(aba[Name]), Linhas = tent[Value], Erro = null],
    Tabs = List.Transform(Table.ToRecords(Table.Sort(AbasFluxo, {{"Name", Order.Ascending}})), each LeAbaFluxo(_)),
    TabsDaObra = (nome as text) as list => List.Select(Tabs, each [Chave] = nome),
    // o {0} no fim: List.Sum de lista vazia dá null (uma aba sem meses lidos tem soma zero, não vazia)
    Soma = (linhas as list) as number => List.Sum(List.Transform(linhas, each if [Custo] = null then 0 else [Custo]) & {0}),

    // ---------- uma obra: linha da PREVXREA (rótulos achados pelo cabeçalho)
    LeObra = (linha as list) as record =>
        let
            nome = Chave(linha{colObra}),
            tipo = if colTipo = null then null else Text.Proper(Text.Lower(Text.Trim(Text.From(linha{colTipo})))),
            orc = if colOrc = null then null else Num(linha{colOrc}),
            m2 = if colM2 = null then null else Num(linha{colM2}),
            real = if colReal = null then 0 else if Num(linha{colReal}) = null then 0 else Num(linha{colReal}),
            meses = List.Select(List.Transform(ColsPrev, each [Mes = MesDeData(DatasLinha{_}), Valor = Num(linha{_})]),
                each [Mes] <> null and [Valor] <> null and [Valor] <> 0),
            pct = if orc = null or orc = 0 then null else real / orc,
            situacao = if pct = null then null
                else if pct >= 0.99 then "Concluída"
                else if pct < 0.005 then "A iniciar"
                else "Em andamento",
            termino = if List.IsEmpty(meses) then null else List.Max(List.Transform(meses, each [Mes])),
            inicioAI = if Corte = null then null
                else List.Min(List.Transform(List.Select(meses, each [Mes] > Corte), each [Mes])),
            tabs = TabsDaObra(nome),
            tab = if List.IsEmpty(tabs) then null else tabs{0},
            inicioFluxo = if tab = null then null else List.Min(List.Transform(tab[Linhas], each [Mes])),
            inicio = if situacao = "A iniciar" then inicioAI else inicioFluxo,
            probs = List.Combine({
                if List.Count(tabs) > 1
                then {[Aba = tabs{0}[Aba], Regra = "aba_fluxo_duplicada", Severidade = "média",
                    Detalhe = "mais de uma aba FLUXO-FINACEIRO para a obra (" & Text.Combine(List.Transform(tabs, each [Aba]), ", ")
                        & "): vale a primeira por nome"]}
                else {},
                if tab <> null and tab[Erro] <> null
                then {[Aba = tab[Aba], Regra = "aba_fluxo_ilegivel", Severidade = "alta",
                    Detalhe = "a aba não abriu (" & tab[Erro] & "): o início dessa obra fica vazio"]}
                else {},
                if tab <> null and tab[Erro] = null and orc <> null and orc > 0
                    and Number.Abs(Soma(tab[Linhas]) / orc - 1) > 0.01
                then {[Aba = tab[Aba], Regra = "curva_nao_fecha", Severidade = "média",
                    Detalhe = "a curva da aba soma R$ " & Number.ToText(Soma(tab[Linhas]), "N2", "pt-BR") & " ("
                        & Number.ToText(Soma(tab[Linhas]) / orc * 100, "N1", "pt-BR") & "% do orçamento de R$ "
                        & Number.ToText(orc, "N2", "pt-BR") & "): a curva não fecha; confira com a cronograma"]}
                else {},
                if tab <> null and tab[Erro] = null and List.IsEmpty(tab[Linhas])
                then {[Aba = tab[Aba], Regra = "aba_fluxo_sem_meses", Severidade = "média",
                    Detalhe = "a aba não tem mês lido na coluna MÊS (datas): o início dessa obra fica vazio"]}
                else {},
                if situacao = "Em andamento" and tab = null
                then {[Aba = NomeAba, Regra = "sem_aba_fluxo", Severidade = "média",
                    Detalhe = "obra em andamento sem aba FLUXO-FINACEIRO na planilha: o início fica vazio"]}
                else {},
                if situacao = null
                then {[Aba = NomeAba, Regra = "situacao_indefinida", Severidade = "média",
                    Detalhe = "sem orçamento na PREVXREA: situação e datas da obra ficam vazias"]}
                else {}
            })
        in
            [ObraCrono = nome, TipoOrcamento = tipo, Orcamento = orc, M2 = m2, Inicio = inicio,
                TerminoPrevisto = termino, Situacao = situacao, VersaoCrono = VersaoArq, ArquivoCrono = NomeArq,
                // curva prevista mês a mês (linha de base): a aba FLUXO-FINACEIRO da obra, [Mes, Custo]
                Curva = if tab = null or tab[Erro] <> null then {}
                    else List.Transform(tab[Linhas], each [Mes = [Mes], Custo = if [Custo] = null then 0 else [Custo]]),
                Problemas = probs],
    Bloco = if not LayoutOk then {} else List.FirstN(List.Skip(Linhas, H + 2), each Chave(_{colObra}) <> ""),
    ObrasTodas = List.Transform(Bloco, each LeObra(_)),
    Nomes = List.Transform(ObrasTodas, each [ObraCrono]),
    Repetidos = List.Distinct(List.Select(Nomes, (x) => List.Count(List.Select(Nomes, (y) => y = x)) > 1)),
    PrimeiraVez = List.Select(List.Positions(ObrasTodas), (i) => not List.Contains(List.FirstN(Nomes, i), Nomes{i})),
    Obras = List.Transform(PrimeiraVez, (i) => ObrasTodas{i}),

    // ---------- problemas da planilha inteira (pasta, arquivo, aba, layout, obra repetida)
    Globais = List.Combine({
        if TemErroPasta then {[Aba = null, Regra = "pasta_ausente", Severidade = "alta", Detalhe = ErrosPasta{0}[ErroPasta]]}
            else {},
        if not TemErroPasta and not TemArquivo
            then {[Aba = null, Regra = "arquivo_ausente", Severidade = "alta",
                Detalhe = "nenhuma planilha '" & pPrefixoCrono & "' (.xlsx) na pasta da cronograma: situação, orçamento e datas das obras da cronograma ficam vazios"]}
            else {},
        if ArquivoIlegivel
            then {[Aba = null, Regra = "arquivo_ilegivel", Severidade = "alta",
                Detalhe = "o arquivo " & NomeArq & " não abriu (" & Tentativa[Error][Message] & ")"]}
            else {},
        if TemArquivo and not VersaoNoNome(NomeArq)
            then {[Aba = null, Regra = "versao_desconhecida", Severidade = "média",
                Detalhe = "o nome não traz 'ATUALIZADO EM MMAAAA': a versão " & VersaoArq & " veio da data de modificação"]}
            else {},
        if TemPasta and NumPrevi = 0
            then {[Aba = null, Regra = "aba_ausente", Severidade = "alta",
                Detalhe = "nenhuma aba PREVXREA em " & NomeArq & ": nenhuma obra da cronograma é lida"]}
            else {},
        if TemPasta and NumPrevi > 1
            then {[Aba = NomeAba, Regra = "aba_previxrea_varias", Severidade = "info",
                Detalhe = Text.From(NumPrevi) & " abas PREVXREA: vale a do mês mais recente no nome ('" & NomeAba & "')"]}
            else {},
        if TemPasta and NumPrevi > 0 and not LayoutOk
            then {[Aba = NomeAba, Regra = "layout", Severidade = "alta",
                Detalhe = "cabeçalho da PREVXREA sem o rótulo " & Text.Combine(Faltam, ", ") & ": nenhuma obra da cronograma é lida"]}
            else {},
        List.Transform(Repetidos, (x) => [Aba = NomeAba, Regra = "obra_duplicada", Severidade = "média",
            Detalhe = "a obra '" & x & "' aparece mais de uma vez na PREVXREA: vale a primeira linha"])
    }),

    Registros = List.Combine({
        if List.IsEmpty(Globais) then {}
            else {[ObraCrono = null, TipoOrcamento = null, Orcamento = null, M2 = null, Inicio = null,
                TerminoPrevisto = null, Situacao = null, VersaoCrono = null, ArquivoCrono = null, Curva = {},
                Problemas = Globais]},
        Obras
    }),
    Tipo = type table [ObraCrono = nullable text, TipoOrcamento = nullable text, Orcamento = nullable number,
        M2 = nullable number, Inicio = nullable date, TerminoPrevisto = nullable date, Situacao = nullable text,
        VersaoCrono = nullable text, ArquivoCrono = nullable text, Curva = list, Problemas = list],
    Saida = Table.FromRecords(Registros, Tipo)
in
    Saida
