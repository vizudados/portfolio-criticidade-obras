/*
@tipo: funcao
@descricao: Rótulo comparável: minúsculas, sem acento, sem espaço duplicado ("4º passo: Previsto do mês" → "4o passo: previsto do mes"). Os campos da planilha são achados pelo rótulo, nunca pelo endereço, porque o layout muda uma linha entre versões.
*/
(texto as any) as text =>
let
    Base = if texto = null then "" else Text.Lower(Text.From(texto)),
    // "º" e "ª" viram letra (como a decomposição Unicode); "°" (grau) sai
    Trocas = {
        {"á", "a"}, {"à", "a"}, {"â", "a"}, {"ã", "a"}, {"ä", "a"},
        {"é", "e"}, {"è", "e"}, {"ê", "e"}, {"ë", "e"},
        {"í", "i"}, {"ì", "i"}, {"î", "i"}, {"ï", "i"},
        {"ó", "o"}, {"ò", "o"}, {"ô", "o"}, {"õ", "o"}, {"ö", "o"},
        {"ú", "u"}, {"ù", "u"}, {"û", "u"}, {"ü", "u"},
        {"ç", "c"}, {"ñ", "n"}, {"º", "o"}, {"ª", "a"}, {"°", ""}
    },
    SemAcento = List.Accumulate(Trocas, Base, (s, par) => Text.Replace(s, par{0}, par{1})),
    Palavras = List.Select(Text.SplitAny(SemAcento, " #(tab)#(lf)#(cr)#(00A0)"), each _ <> ""),
    Resultado = Text.Combine(Palavras, " ")
in
    Resultado
