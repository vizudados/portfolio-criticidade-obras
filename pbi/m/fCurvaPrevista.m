/*
@tipo: tabela
@descricao: Curva prevista (linha de base) de cada obra, mês a mês, da aba FLUXO-FINACEIRO da cronograma (stgCrono): o previsto acumulado em fração do orçamento e o índice do mês (1 = mês de início), com uma linha 0 (o mês antes do início, previsto 0). Base do atraso em meses (cronograma agregado, Earned Schedule): as medidas leem a curva da obra pelo nome, sem relação. Obra pelo cadastro (nome_crono → obra); fora do cadastro, o nome da cronograma.
@oculta: sim
@coluna: Obra | texto | | Obra (do cadastro, pelo nome na cronograma).
@coluna: Mes | data | formato=dd/mm/yyyy | Mês da curva.
@coluna: Indice | inteiro | formato=0 | Meses desde o início, contando o mês de início como 1 (0 = mês anterior).
@coluna: Custo | decimal | formato=#,0.00 | Custo previsto no mês.
@coluna: PrevAcum | decimal | formato=0.0000% | Previsto acumulado até o mês ÷ soma da curva.
*/
let
    Nomes = Table.SelectRows(Table.SelectColumns(stgCadastro, {"Obra", "NomeCrono"}), each [NomeCrono] <> null),
    ObraDe = (crono as text) as text =>
        let achada = Table.SelectRows(Nomes, each [NomeCrono] = crono) in if Table.IsEmpty(achada) then crono else achada{0}[Obra],
    ComCurva = Table.SelectRows(stgCrono, each [ObraCrono] <> null and not List.IsEmpty([Curva])),
    PorObra = List.Transform(Table.ToRecords(ComCurva), (r) =>
        let
            Ordenada = List.Sort(r[Curva], (a, b) => Value.Compare(a[Mes], b[Mes])),
            Total = List.Sum(List.Transform(Ordenada, each [Custo])),
            Acum = List.Accumulate(Ordenada, {}, (s, x) => s & {(if List.IsEmpty(s) then 0 else List.Last(s)) + x[Custo]}),
            Obra = ObraDe(r[ObraCrono]),
            Linhas = List.Transform(List.Positions(Ordenada), (i) =>
                [Obra = Obra, Mes = Ordenada{i}[Mes], Indice = i + 1, Custo = Ordenada{i}[Custo],
                 PrevAcum = if Total = 0 then null else Acum{i} / Total]),
            Zero = [Obra = Obra, Mes = Date.AddMonths(Ordenada{0}[Mes], -1), Indice = 0, Custo = 0, PrevAcum = 0]
        in
            {Zero} & Linhas),
    Tabela = Table.FromRecords(List.Combine(PorObra), type table [Obra = text, Mes = date, Indice = Int64.Type,
        Custo = number, PrevAcum = number])
in
    Tabela
