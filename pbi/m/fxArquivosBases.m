/*
@tipo: consulta
@descricao: Consulta auxiliar (não carregada): os .xlsx da pasta das bases complementares (pPastaBases, relativa à raiz dos dados de pOrigem), no formato de listagem de pasta (Content, Name, Date modified, Subpasta, ErroPasta), sem o MODELO, sem o arquivo de trava do Excel (~$) e sem nada marcado OBSOLETO. Só vale a RAIZ da pasta: arquivo em subpasta (backup, cópia de sincronização) chega com Subpasta preenchida, não é lido e vira aviso em fConferencia (senão um arquivo de mesmo nome duplicaria a obra × mês). Pasta que não abre não quebra a atualização: a consulta devolve uma linha só com ErroPasta preenchido, que stgAbasADO leva para fConferencia (as obras ficam pendentes). Só leitura.
*/
let
    // Buffer dentro do try: o erro de pasta inexistente só aparece quando a lista de arquivos é lida
    Tentativa = try Table.Buffer(Table.AddColumn(fxArquivosOrigem(pPastaBases), "Subpasta",
        each if [Relativo] = "" then null else [Relativo], type nullable text)),
    Xlsx = (t as table) as table => Table.SelectRows(t, each Text.Lower([Extension]) = ".xlsx"
        and not Text.StartsWith([Name], "~$")
        and not Text.Contains(fxNormaliza([Name]), "modelo")
        and not Text.Contains(fxNormaliza([Name]), "obsolet")),
    Tipo = type table [Content = nullable binary, Name = nullable text, #"Date modified" = nullable datetime,
        Subpasta = nullable text, ErroPasta = nullable text],
    Erro = #table(Tipo, {{null, null, null, null, "a pasta das bases complementares não abriu ("
        & fxCaminhoOrigem(pPastaBases) & "): " & Tentativa[Error][Message]}}),
    Ok = Table.AddColumn(Table.SelectColumns(Xlsx(Tentativa[Value]), {"Content", "Name", "Date modified", "Subpasta"}),
        "ErroPasta", each null, type nullable text)
in
    if Tentativa[HasError] then Erro else Value.ReplaceType(Ok, Tipo)
