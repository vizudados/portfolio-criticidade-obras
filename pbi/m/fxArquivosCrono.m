/*
@tipo: consulta
@descricao: Consulta auxiliar (não carregada): os arquivos da raiz da pasta da cronograma (pPastaCrono, relativa à raiz dos dados de pOrigem, sem as subpastas), no formato de listagem de pasta (Content, Name, Date modified, ErroPasta). Pasta que não abre não quebra a atualização: a consulta devolve uma linha só com ErroPasta preenchido, que stgCrono leva para fConferencia (a cronograma fica vazia). Só leitura.
*/
let
    // Buffer dentro do try: a pasta inexistente só aparece quando a lista de arquivos é lida; só a raiz entra
    Tentativa = try Table.Buffer(Table.SelectColumns(
        Table.SelectRows(fxArquivosOrigem(pPastaCrono), each [Relativo] = ""), {"Content", "Name", "Date modified"})),
    Tipo = type table [Content = nullable binary, Name = nullable text, #"Date modified" = nullable datetime,
        ErroPasta = nullable text],
    Erro = #table(Tipo, {{null, null, null, "a pasta da cronograma não abriu (" & fxCaminhoOrigem(pPastaCrono) & "): "
        & Tentativa[Error][Message]}}),
    Ok = Table.AddColumn(Tentativa[Value], "ErroPasta", each null, type nullable text)
in
    if Tentativa[HasError] then Erro else Value.ReplaceType(Ok, Tipo)
