/*
@tipo: tabela
@descricao: Meses do histórico, de pInicioHistorico até o último mês com aba em fAnaliseCritica. Eixo dos gráficos mês a mês. O mês de referência escolhido no drawer vem de dMesRef (desconectada), para que o seletor não corte o eixo.
@coluna: Mes | data | chave; formato=dd/mm/yyyy | Primeiro dia do mês.
@coluna: Ano | inteiro | formato=0 | Ano.
@coluna: MesNum | inteiro | formato=0 | Número do mês (1 a 12).
@coluna: MesNome | texto | ordenar=Ordem | Nome do mês por extenso, minúsculo (junho).
@coluna: MesAno | texto | ordenar=Ordem | Rótulo curto: jun/26.
@coluna: MesAnoLongo | texto | ordenar=Ordem | Rótulo longo: junho de 2026.
@coluna: MesAbrev | texto | ordenar=Ordem | Mês abreviado sem ano: jun.
@coluna: Ordem | inteiro | formato=0 | Ordem do mês no histórico (1 = primeiro mês).
*/
let
    // sem nenhuma aba lida (pasta ausente ou vazia), o eixo fica no primeiro mês do histórico, em vez de quebrar
    Ultimo = if List.IsEmpty(List.RemoveNulls(fAnaliseCritica[Mes])) then pInicioHistorico else List.Max(fAnaliseCritica[Mes]),
    Quantos = (Date.Year(Ultimo) - Date.Year(pInicioHistorico)) * 12 + Date.Month(Ultimo) - Date.Month(pInicioHistorico) + 1,
    Meses = List.Transform({0 .. Quantos - 1}, each Date.AddMonths(pInicioHistorico, _)),
    Nomes = {"janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
        "novembro", "dezembro"},
    Linhas = List.Transform(List.Positions(Meses), (i) =>
        let m = Meses{i}, nome = Nomes{Date.Month(m) - 1} in
        [Mes = m, Ano = Date.Year(m), MesNum = Date.Month(m), MesNome = nome,
         MesAno = Text.Start(nome, 3) & "/" & Text.End(Text.From(Date.Year(m)), 2),
         MesAnoLongo = nome & " de " & Text.From(Date.Year(m)), MesAbrev = Text.Start(nome, 3), Ordem = i + 1]),
    Tabela = Table.FromRecords(Linhas, type table [Mes = date, Ano = Int64.Type, MesNum = Int64.Type, MesNome = text,
        MesAno = text, MesAnoLongo = text, MesAbrev = text, Ordem = Int64.Type])
in
    Tabela
