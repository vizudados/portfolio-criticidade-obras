/*
@tipo: tabela
@descricao: Janela das séries mês a mês (seletor do drawer, de escolha única): quantos meses, até o mês de referência, os gráficos, os tooltips e as leituras olham. Desconectada. A primeira linha (12 meses) é a padrão: o seletor de escolha única a marca quando nada está escolhido. A série nunca começa antes do primeiro mês do histórico (pInicioHistorico).
@coluna: Janela | texto | chave; ordenar=Ordem | Rótulo do seletor (12 meses, 9 meses, 6 meses, 3 meses).
@coluna: Meses | inteiro | formato=0 | Quantos meses a janela cobre, contando o de referência.
@coluna: Ordem | inteiro | oculta; formato=0 | Ordem no seletor (1 = 12 meses, a padrão).
*/
let
    Tabela = #table(type table [Janela = text, Meses = Int64.Type, Ordem = Int64.Type], {
        {"12 meses", 12, 1},
        {"9 meses", 9, 2},
        {"6 meses", 6, 3},
        {"3 meses", 3, 4}
    })
in
    Tabela
