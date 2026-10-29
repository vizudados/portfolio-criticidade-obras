/*
@tipo: funcao
@descricao: Mês de referência pelo nome da aba. Aceita mês abreviado ou por extenso, com ou sem acento, colado ou não ao ano de 2 ou 4 dígitos, e qualquer complemento depois do ano ou entre parênteses: JUN26, ABRIL26, "NOV25 ", MARÇO 2026, NOVEMBRO2025, SET 2026, "ABRIL 2026 (RETA FINAL)", JUNHO 2025 EXECUTIVO. Fica fora (null) a aba sem ano (MAIO EXECUTIVO.), a que não começa por mês (ESTOQUE, EST AGO, Planilha1, Estudo 5 meses) e a marcada como OBSOLETO, TESTE, REV ou CÓPIA.
*/
(nome as text) as nullable date =>
let
    Normal = Text.Upper(fxNormaliza(nome)),
    // o complemento entre parênteses sai do nome, mas conta para as marcas de descarte
    Partes = Text.Split(Normal, "("),
    Parenteses = Text.Combine(List.Transform(List.Skip(Partes, 1), each Text.BeforeDelimiter(_, ")")), " "),
    Fora = Text.Combine({Partes{0}} & List.Transform(List.Skip(Partes, 1), each Text.AfterDelimiter(_, ")")), " "),
    Palavras = List.Select(Text.Split(Text.Select(Fora, {"A".."Z", "0".."9", " "}), " "), each _ <> ""),
    Marcas = List.Select(Text.Split(Text.Select(Fora & " " & Parenteses, {"A".."Z", "0".."9", " "}), " "), each _ <> ""),
    Descartada = List.ContainsAny(Marcas, {"OBSOLETO", "OBSOLETA", "TESTE", "REV", "COPIA"}),
    Primeira = if List.IsEmpty(Palavras) then "" else Palavras{0},
    Letras = Text.Select(Primeira, {"A".."Z"}),
    Colado = Text.Range(Primeira, Text.Length(Letras)),
    LetrasPrimeiro = Text.StartsWith(Primeira, Letras) and Text.Select(Colado, {"0".."9"}) = Colado,
    Ano = if Colado <> "" then Colado
        else if List.Count(Palavras) > 1 and Text.Select(Palavras{1}, {"0".."9"}) = Palavras{1} then Palavras{1}
        else "",
    Meses = [JAN = 1, JANEIRO = 1, FEV = 2, FEVEREIRO = 2, MAR = 3, MARCO = 3, ABR = 4, ABRIL = 4, MAI = 5, MAIO = 5,
        JUN = 6, JUNHO = 6, JUL = 7, JULHO = 7, AGO = 8, AGOSTO = 8, SET = 9, SETEMBRO = 9, OUT = 10, OUTUBRO = 10,
        NOV = 11, NOVEMBRO = 11, DEZ = 12, DEZEMBRO = 12],
    Valido = not Descartada and LetrasPrimeiro and Letras <> "" and Record.HasFields(Meses, Letras)
        and (Text.Length(Ano) = 2 or Text.Length(Ano) = 4),
    Mes = if Valido
        then #date((if Text.Length(Ano) = 2 then 2000 else 0) + Number.From(Ano), Record.Field(Meses, Letras), 1)
        else null
in
    Mes
