/*
@tipo: funcao
@descricao: Os arquivos de uma pasta relativa à raiz dos dados, com as subpastas, no formato de listagem de pasta (Content, Name, Extension, Date modified) mais Relativo: o caminho da subpasta abaixo da pasta pedida, separado por "\" e terminado em "\" ("" na própria pasta). Na entrega a raiz são os arquivos embutidos (fxDadosEmbutidos): o modelo não tem fonte externa nenhuma. O perfil local do gerador troca esta função por uma que também lê a pasta do computador (pbi/m/_local). Pasta sem nenhum arquivo é erro: quem chama trata com try e avisa em fConferencia.
*/
(relativo as text) as table =>
let
    Partes = (t as text) as list => List.Select(Text.SplitAny(Text.Trim(t), "\/"), each _ <> ""),
    // caminho comparável: "\" e "/" iguais, minúsculas, terminado em "/"
    Chave = (t as text) as text => Text.Lower(Text.Combine(Partes(t), "/")) & "/",
    Raiz = Chave("embutido/" & relativo),
    Lista = fxDadosEmbutidos,
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
