/*
@tipo: consulta
@descricao: Consulta auxiliar (não carregada): uma linha por arquivo × aba das bases complementares (fxArquivosBases), fora LEIA-ME e MODELO, com os valores crus da aba num registro (Valores), se a aba tem algum campo preenchido (Preenchida), se é a aba que vale para a obra × mês (Vale) e a lista dos problemas achados (Problemas: Regra, Severidade, Detalhe), que fConferencia publica. Mês pelo nome da aba (fxMesDaAba, depois de maiúsculas e sem espaço nas pontas). Obra pelo nome do arquivo (Base complementar - <OBRA>.xlsx, sem sufixo de cópia ou de conflito como " (1)", " - Cópia" ou "-PC"), a chave do painel; obra fora de dObra não é lida (aviso); a célula Obra só é conferida (diferente = aviso). Só os arquivos da raiz da pasta (subpasta = aviso, não lida). Cada campo é achado pelo rótulo: a coluna dos rótulos é a do "Versão do modelo" (coluna B do modelo) e o valor fica duas colunas à direita (coluna D), em qualquer linha. Modelo BC 2.0 (dados fictícios da F2, 28/10/2026): PPC, inspeções, HHT, acidentes, checklist NR-18, pedidos e dias de chuva; os rótulos, a versão e as faixas vêm de fxRegrasBase (dicionário NOTA). Mês repetido: vale a aba preenchida mais à direita (entre arquivos da mesma obra, o modificado por último); aba vazia só vale se nenhuma estiver preenchida. Texto onde se espera número vira nulo; número fora da faixa válida chega como foi digitado, com aviso. Faixas válidas vêm de fxRegrasBase (gerada do dicionário NOTA). Arquivo ilegível, aba sem o rótulo âncora e pasta que não abre viram problema, nunca erro de atualização.
*/
let
    Arquivos = fxArquivosBases,
    // versão, rótulos e faixas válidas: fxRegrasBase, gerada do dicionário NOTA (pbi/scripts/contas_base.py)
    Regras = fxRegrasBase(),
    VersaoModelo = Regras[Versao],
    Meses = {"JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"},
    // {campo, rótulos aceitos (normalizados), rótulo para os avisos}: os três fixos e os da base (fxRegrasBase)
    Campos = {
        {"Versao", {"versao do modelo"}, "Versão do modelo"},
        {"ObraCelula", {"obra"}, "Obra"},
        {"Gestor", {"gestor da obra", "gestor"}, "Gestor da obra"}
    } & Regras[Campos],
    Numericos = Record.FieldNames(Regras[Faixas]),
    // campos que contam para "aba preenchida" (Versão e Obra vêm prontas no modelo)
    Conteudo = List.Skip(List.Transform(Campos, each _{0}), 2),
    RotuloDe = (campo as text) as text => List.First(List.Select(Campos, each _{0} = campo)){2},
    Vazio = (v as any) as logical => v = null or (v is text and Text.Trim(v) = ""),
    Texto = (v as any) as text => if v is text then v else Text.From(v),
    Problema = (regra as text, severidade as text, detalhe as text) as record =>
        [Regra = regra, Severidade = severidade, Detalhe = detalhe],

    // ---- Leitura de uma aba: registro com o valor cru de cada campo, ou null sem o rótulo âncora
    LerAba = (dados as table) as nullable record =>
        let
            Linhas = List.Buffer(Table.ToRows(dados)),
            Celula = (linha as list, c as number) as any => if c < List.Count(linha) then linha{c} else null,
            Ancora = List.First(List.Select(List.Transform(Linhas, (linha) =>
                List.PositionOf(List.Transform(linha, each _ is text and fxNormaliza(_) = "versao do modelo"), true)),
                each _ >= 0), null),
            Valor = (rotulos as list) as any =>
                let achada = List.First(List.Select(Linhas, (linha) =>
                        let r = Celula(linha, Ancora) in r is text and List.Contains(rotulos, fxNormaliza(r))), null)
                in if achada = null then null else Celula(achada, Ancora + 2)
        in
            if Ancora = null then null
            else Record.FromList(List.Transform(Campos, each Valor(_{1})), List.Transform(Campos, each _{0})),

    // ---- Valores crus → tipados, e os problemas de preenchimento
    Tratar = (b as record) as record =>
        let
            Num = (campo as text) as nullable number => let v = Record.Field(b, campo) in if v is number then v else null,
            Livre = (campo as text) as nullable text =>
                let v = Record.Field(b, campo) in if Vazio(v) then null else Text.Trim(Texto(v)),
            NaoNumericos = List.Select(Numericos, (campo) =>
                let v = Record.Field(b, campo) in not Vazio(v) and not (v is number)),
            ForaDaFaixa = List.Select(Numericos, (campo) =>
                let v = Record.Field(b, campo), f = Record.Field(Regras[Faixas], campo)
                in v is number and (v < f{0} or v > f{1})),
            Valores = [Gestor = Livre("Gestor")]
                & Record.FromList(List.Transform(Numericos, each Num(_)), Numericos),
            Problemas =
                List.Transform(NaoNumericos, (campo) => Problema("valor_nao_numerico", "média",
                    "'" & RotuloDe(campo) & "' = '" & Text.Trim(Texto(Record.Field(b, campo)))
                        & "': texto onde se espera número; o campo fica vazio"))
                & List.Transform(ForaDaFaixa, (campo) => Problema("valor_fora_da_faixa", "média",
                    "'" & RotuloDe(campo) & "' = " & Text.From(Record.Field(b, campo), "pt-BR") & ": fora da faixa válida ("
                        & Text.From(Record.Field(Regras[Faixas], campo){0}, "pt-BR") & " a "
                        & Text.From(Record.Field(Regras[Faixas], campo){1}, "pt-BR") & "); o item fica sem dado"))
        in
            [Valores = Valores, Preenchida = List.AnyTrue(List.Transform(Conteudo, each not Vazio(Record.Field(b, _)))),
             Problemas = Problemas],

    // "Base complementar - POTENGI.xlsx" → POTENGI. Cópias e conflitos dão a mesma obra: "… - CAJUEIRO (1).xlsx",
    // "… - CAJUEIRO - Cópia.xlsx", "… - CAJUEIRO-NOTEBOOK.xlsx" (conflito de sincronização), "Cópia de Base complementar - …".
    ObraDoArquivo = (nome as text) as text =>
        let
            Base = fxNormaliza(Text.BeforeDelimiter(nome, ".", {0, RelativePosition.FromEnd})),
            Partes = Text.Split(Base, "("),
            SemParenteses = Text.Combine({Partes{0}} & List.Transform(List.Skip(Partes, 1),
                each Text.AfterDelimiter(_, ")")), " "),
            Resto = if Text.Contains(SemParenteses, "base complementar")
                then Text.AfterDelimiter(SemParenteses, "base complementar")
                else Text.AfterDelimiter(SemParenteses, "-", {0, RelativePosition.FromEnd}),
            Obra = Text.Trim(Text.BeforeDelimiter(Text.Trim(Resto, {" ", "-"}) & "-", "-"))
        in
            Text.Upper(Obra),
    // obras do painel (dObra): base de obra fora delas não é lida (senão vira linha órfã nos totais por item)
    ObrasPainel = List.Buffer(dObra[Obra]),
    ObraDoPainel = (obra as text) as nullable text =>
        List.First(List.Select(ObrasPainel, each fxNormaliza(_) = fxNormaliza(obra)), null),

    Linha = (arquivo, data, obraArquivo, aba, ordem, mes, obra, valores, preenchida, problemas) as record =>
        [Arquivo = arquivo, DataArquivo = data, ObraArquivo = obraArquivo, Aba = aba, OrdemAba = ordem, Mes = mes,
         Obra = obra, Valores = valores, Preenchida = preenchida, Problemas = problemas],

    DoArquivo = (arq as record) as list =>
        if arq[ErroPasta] <> null then
            {Linha(null, null, null, null, null, null, null, null, false, {Problema("pasta_ausente", "alta", arq[ErroPasta])})}
        else if arq[Subpasta] <> null then
            {Linha(arq[Name], arq[Date modified], ObraDoArquivo(arq[Name]), null, null, null, ObraDoArquivo(arq[Name]),
                null, false, {Problema("subpasta_ignorada", "média", "'" & arq[Subpasta] & arq[Name]
                    & "' está numa subpasta da pasta das bases: não é lido (só valem os arquivos da raiz)")})}
        else if ObraDoPainel(ObraDoArquivo(arq[Name])) = null then
            {Linha(arq[Name], arq[Date modified], ObraDoArquivo(arq[Name]), null, null, null, ObraDoArquivo(arq[Name]),
                null, false, {Problema("obra_desconhecida", "média", "'" & arq[Name] & "': a obra '"
                    & ObraDoArquivo(arq[Name]) & "' (pelo nome do arquivo) não está no painel; o arquivo não é lido")})}
        else
            let
                ObraArq = ObraDoPainel(ObraDoArquivo(arq[Name])),
                Pasta = try Table.Buffer(Table.SelectRows(Excel.Workbook(arq[Content], null, true), each [Kind] = "Sheet")),
                Folhas = if Pasta[HasError] then {} else Table.ToRecords(Table.AddIndexColumn(Pasta[Value], "OrdemAba", 1, 1)),
                Mensais = List.Select(Folhas, each not List.Contains({"leia-me", "leia me", "leiame", "modelo"},
                    fxNormaliza([Name]))),
                DaAba = (f as record) as record =>
                    let
                        Nome = f[Name],
                        Mes = fxMesDaAba(Text.Upper(Text.Trim(Nome))),
                        Canonico = if Mes = null then null else Meses{Date.Month(Mes) - 1} & " " & Text.From(Date.Year(Mes)),
                        Lida = if Mes = null then null else (try LerAba(f[Data]) otherwise null),
                        Tratado = if Lida = null then null else Tratar(Lida),
                        ObraD5 = if Lida = null or Vazio(Lida[ObraCelula]) then null
                            else Text.Upper(Text.Trim(Texto(Lida[ObraCelula]))),
                        Versao = if Lida = null or Vazio(Lida[Versao]) then "" else Text.Trim(Texto(Lida[Versao])),
                        Problemas = List.RemoveNulls({
                            if Mes = null then Problema("aba_fora_do_padrao", "média", "'" & Nome
                                & "': o nome não traz um mês no padrão MMM AAAA (ex.: SET 2026); a aba fica de fora") else null,
                            if Mes <> null and Nome <> Canonico then Problema("nome_da_aba", "baixa", "'" & Nome
                                & "' fora do padrão MMM AAAA (maiúsculas, sem espaço nas pontas); lida como " & Canonico) else null,
                            if Mes <> null and Lida = null then Problema("layout", "alta",
                                "rótulo 'Versão do modelo' não encontrado; a aba fica de fora") else null,
                            if Lida <> null and Versao <> VersaoModelo then Problema("versao_desconhecida", "média",
                                "versão do modelo '" & Versao & "' (esperada " & VersaoModelo & "); lida pelos rótulos de "
                                    & VersaoModelo) else null,
                            if ObraD5 <> null and fxNormaliza(ObraD5) <> fxNormaliza(ObraArq) then Problema("obra_divergente",
                                "média", "célula Obra = '" & ObraD5 & "', arquivo = '" & ObraArq & "'; vale o arquivo") else null
                        }) & (if Tratado = null then {} else Tratado[Problemas])
                    in
                        Linha(arq[Name], arq[Date modified], ObraArq, Nome, f[OrdemAba], Mes,
                            ObraArq,
                            if Tratado = null then null else Tratado[Valores],
                            Tratado <> null and Tratado[Preenchida], Problemas)
            in
                if Pasta[HasError] then
                    {Linha(arq[Name], arq[Date modified], ObraArq, null, null, null, ObraArq, null, false,
                        {Problema("arquivo_ilegivel", "alta", "o arquivo não abre como pasta de trabalho do Excel: "
                            & Pasta[Error][Message])})}
                else if List.IsEmpty(Mensais) then
                    {Linha(arq[Name], arq[Date modified], ObraArq, null, null, null, ObraArq, null, false,
                        {Problema("base_vazia", "info", "o arquivo não tem nenhuma aba de mês")})}
                else List.Transform(Mensais, DaAba),

    Tipo = type table [Arquivo = nullable text, DataArquivo = nullable datetime, ObraArquivo = nullable text,
        Aba = nullable text, OrdemAba = nullable Int64.Type, Mes = nullable date, Obra = nullable text,
        Valores = nullable record, Preenchida = logical, Problemas = list],
    Tabela = Table.Buffer(Table.FromRecords(List.Combine(List.Transform(Table.ToRecords(Arquivos), DoArquivo)), Tipo)),

    // Mês repetido (na mesma base ou em duas bases da mesma obra): vale a aba preenchida mais à direita do arquivo mais
    // recente; a vazia só vale quando nenhuma está preenchida
    Candidatas = Table.SelectRows(Tabela, each [Mes] <> null and [Valores] <> null),
    Escolhidas = Table.Group(Candidatas, {"Obra", "Mes"}, {{"Chave", each
        let t = Table.Sort(_, {{"Preenchida", Order.Descending}, {"DataArquivo", Order.Descending},
                {"OrdemAba", Order.Descending}})
        in t{0}[Arquivo] & "|" & t{0}[Aba], type text}}),
    Chaves = List.Buffer(Escolhidas[Chave]),
    ComVale = Table.AddColumn(Tabela, "Vale", each [Mes] <> null and [Valores] <> null
        and List.Contains(Chaves, [Arquivo] & "|" & [Aba]), type logical),
    // a aba que valeu para a obra × mês ("arquivo › aba"), para o aviso de mês duplicado
    Vencedoras = Table.Buffer(Escolhidas),
    ComVencedora = Table.AddColumn(ComVale, "Vencedora", (r) =>
        if r[Mes] = null or r[Valores] = null then null
        else Text.Replace(Table.SelectRows(Vencedoras, each [Obra] = r[Obra] and [Mes] = r[Mes]){0}[Chave], "|", " › "),
        type nullable text)
in
    ComVencedora
