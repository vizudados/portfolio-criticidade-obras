/*
@tipo: funcao
@descricao: Caminho por extenso de uma pasta ou arquivo relativo à raiz dos dados, para os avisos: "embutido\cronograma" (na entrega, os arquivos estão dentro do modelo). O perfil local do gerador troca esta função pela que escreve o caminho da pasta do computador (pbi/m/_local).
*/
(relativo as text) as text =>
let
    Partes = (t as text) as list => List.Select(Text.SplitAny(Text.Trim(t), "\/"), each _ <> ""),
    Texto = Text.Combine({"embutido"} & Partes(relativo), "\")
in
    Texto
