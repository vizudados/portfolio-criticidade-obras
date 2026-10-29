/*
@tipo: funcao
@descricao: O conteúdo (binário) de um arquivo relativo à raiz dos dados (ex.: cadastro\obras_cadastro.csv), achado na listagem da pasta dele (fxArquivosOrigem), nas duas origens: assim a fonte de dados é sempre a pasta raiz ou o site, nunca um caminho montado. Arquivo ausente é erro.
*/
(relativo as text) as binary =>
let
    Partes = List.Select(Text.SplitAny(Text.Trim(relativo), "\/"), each _ <> ""),
    Nome = List.Last(Partes),
    Pasta = Text.Combine(List.RemoveLastN(Partes, 1), "\"),
    Achados = Table.SelectRows(fxArquivosOrigem(Pasta), each [Relativo] = "" and Text.Lower([Name]) = Text.Lower(Nome))
in
    if Table.IsEmpty(Achados) then error Error.Record("Origem", "arquivo não encontrado: " & fxCaminhoOrigem(relativo))
    else Achados{0}[Content]
