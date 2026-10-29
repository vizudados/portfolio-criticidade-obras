/*
@tipo: funcao
@descricao: PERFIL LOCAL (gerar_modelo.py --perfil local). Caminho por extenso de uma pasta ou arquivo relativo à raiz dos dados, para os avisos: "embutido\cronograma" (pOrigem = "Embutido"), "C:\…\dados\cronograma" (pOrigem = "Pasta") ou "https://…/sites/…/Shared Documents/…/dados/cronograma" (pOrigem = "SharePoint").
*/
(relativo as text) as text =>
let
    Partes = (t as text) as list => List.Select(Text.SplitAny(Text.Trim(t), "\/"), each _ <> ""),
    Rel = Partes(relativo),
    Texto = if pOrigem = "Embutido" then Text.Combine({"embutido"} & Rel, "\")
        else if pOrigem = "SharePoint"
        then Text.TrimEnd(Text.Trim(pSiteSharePoint), {"/"}) & "/" & Text.Combine(Partes(pPastaSharePoint) & Rel, "/")
        else Text.TrimEnd(Text.Trim(pPastaDados), {"\", "/"}) & "\" & Text.Combine(Rel, "\")
in
    Texto
