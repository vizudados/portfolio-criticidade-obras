/*
@tipo: consulta
@descricao: Consulta auxiliar (não carregada): os arquivos da pasta de análise crítica (pPastaPlanilhas, relativa à raiz dos dados de pOrigem), com as subpastas, no formato de listagem de pasta (Content, Name, Extension, Date modified) mais Relativo, o caminho da subpasta abaixo da pasta separado por "\" (ex.: "DUNAS\"). Pasta que não abre não quebra a atualização: a consulta devolve uma linha só com ErroPasta preenchido e Name vazio (a linha não entra na análise), que fConferencia avisa. Só leitura.
*/
let
    // Buffer dentro do try: a pasta inexistente só aparece quando a lista de arquivos é lida
    Tentativa = try Table.Buffer(fxArquivosOrigem(pPastaPlanilhas)),
    Tipo = type table [Content = nullable binary, Name = nullable text, Extension = nullable text,
        #"Date modified" = nullable datetime, Relativo = nullable text, ErroPasta = nullable text],
    Erro = #table(Tipo, {{null, "", "", null, null, "a pasta de análise crítica não abriu (" & fxCaminhoOrigem(pPastaPlanilhas)
        & "): " & Tentativa[Error][Message]}}),
    Ok = Table.AddColumn(Tentativa[Value], "ErroPasta", each null, type nullable text)
in
    if Tentativa[HasError] then Erro else Value.ReplaceType(Ok, Tipo)
