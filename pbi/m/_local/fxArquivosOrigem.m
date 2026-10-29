/*
@tipo: funcao
@descricao: PERFIL LOCAL (gerar_modelo.py --perfil local; nunca vai para o serviço nem para o portfólio). Os arquivos de uma pasta relativa à raiz dos dados, com as subpastas, no formato do Folder.Files (Content, Name, Extension, Date modified) mais Relativo. pOrigem = "Pasta": Folder.Files(pPastaDados); "SharePoint": SharePoint.Files(pSiteSharePoint), só o que está abaixo de pPastaSharePoint; "Embutido": fxDadosEmbutidos. O recorte pela pasta pedida vem pelo Folder Path. Pasta sem nenhum arquivo é erro: quem chama trata com try e avisa em fConferencia.
*/
(relativo as text) as table =>
let
    Partes = (t as text) as list => List.Select(Text.SplitAny(Text.Trim(t), "\/"), each _ <> ""),
    // caminho comparável, nos dois casos: sem o protocolo, "\" e "/" iguais, minúsculas, terminado em "/"
    Chave = (t as text) as text =>
        Text.Lower(Text.Combine(Partes(Text.Replace(Text.Replace(Text.Trim(t), "https://", ""), "http://", "")), "/")) & "/",
    SP = pOrigem = "SharePoint",
    Emb = pOrigem = "Embutido",
    Raiz = Chave(
        if Emb then "embutido/" & relativo
        else if SP then pSiteSharePoint & "/" & pPastaSharePoint & "/" & relativo
        else pPastaDados & "/" & relativo),
    Lista =
        if Emb then fxDadosEmbutidos
        else if SP then SharePoint.Files(pSiteSharePoint, [ApiVersion = 15])
        else Folder.Files(pPastaDados),
    Abaixo = Table.SelectRows(Lista, each Text.StartsWith(Chave([Folder Path]), Raiz)),
    ComRel = Table.AddColumn(Abaixo, "Relativo", each
        let
            // quantas subpastas abaixo da pasta pedida; o nome delas vem do caminho original (maiúsculas e acentos)
            n = List.Count(Partes(Text.Range(Chave([Folder Path]), Text.Length(Raiz)))),
            original = Partes([Folder Path])
        in
            if n = 0 then "" else Text.Combine(List.LastN(original, n), "\") & "\",
        type text),
    Final = if Table.IsEmpty(ComRel)
        then error Error.Record("Origem", "nenhum arquivo em " & fxCaminhoOrigem(relativo))
        else Table.SelectColumns(ComRel, {"Content", "Name", "Extension", "Date modified", "Relativo"})
in
    Final
