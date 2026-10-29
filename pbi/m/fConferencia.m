/*
@tipo: consulta
@descricao: Consulta auxiliar (não carregada no modelo): relatório de conferência das planilhas (bastidor, não aparece nas telas). O que não fecha ou está fora do padrão em cada aba: conta que diverge da regra, valor digitado fora da conta, acumulado que regride, mês anterior apontando para outra aba, nome de aba fora do padrão… Uma linha por aviso, com as colunas Obra, Mes, Aba, Regra, Titulo, Severidade, OrdemSeveridade e Detalhe. Regras espelhadas de pipeline/extrair_analise_critica.py; de pInicioHistorico em diante, mais os avisos do arquivo (sem mês). Também os problemas das bases complementares (stgAbasBase; regras com prefixo base_): pasta que não abre, arquivo ilegível, aba fora do padrão, layout sem o rótulo âncora, versão do modelo desconhecida, obra da célula diferente do arquivo, arquivo em subpasta (não lido), obra fora do painel (não lida), dois arquivos da mesma obra, valor não numérico, opção fora da lista, número fora da faixa válida, mês duplicado e obra × mês com Análise Crítica sem aba preenchida na base (agrupado por obra quando a base não tem nenhum mês preenchido). Também a cronograma (stgCrono; regras crono_): pasta, arquivo, aba PREVXREA, layout, aba FLUXO que não abre, aba FLUXO duplicada, curva da aba que não fecha no orçamento, obra repetida, e o vínculo com o cadastro (nome_crono): obra do cadastro sem nome_crono, obra do cadastro sem linha na cronograma, obra da cronograma fora do cadastro.
*/
let
    Reais = (v as nullable number) as text =>
        (if v < 0 then "−" else "") & "R$ " & Number.ToText(Number.Abs(v), "N2", "pt-BR"),
    Pct = (v as nullable number) as text => Number.ToText(v * 100, "N2", "pt-BR") & "%",
    Titulos = [
        layout = "Layout não reconhecido", nome_da_aba = "Nome de aba fora do padrão",
        mes_divergente = "Mês de análise desatualizado", previsto_regrediu = "Previsto acumulado caiu",
        executado_regrediu = "Executado acumulado caiu", executado_nao_fecha = "Executado acumulado não fecha",
        previsto_reprogramado = "Previsto acumulado reprogramado", mes_anterior_errado = "Mês anterior aponta para a aba errada",
        previsto_rs_repetido = "Previsto do mês repetido", tipo_orcamento_mudou = "Tipo de orçamento mudou",
        projeto_divergente = "Nome do projeto divergente", conta_diverge = "Resultado apresentado ≠ regra da planilha",
        item_fora_da_conta = "Valor digitado fora da conta", item_sem_descricao = "Item sem descrição",
        abas_ocultas = "Abas ocultas de layout antigo", aba_duplicada = "Duas abas para o mesmo mês",
        previsto_vazio = "Previsto em branco",
        base_pasta_ausente = "Base complementar: pasta não abre", base_arquivo_ilegivel = "Base complementar: arquivo ilegível",
        base_base_vazia = "Base complementar: arquivo sem aba de mês", base_aba_fora_do_padrao = "Base complementar: aba fora do padrão",
        base_nome_da_aba = "Base complementar: nome de aba fora do padrão", base_layout = "Base complementar: layout não reconhecido",
        base_versao_desconhecida = "Base complementar: versão do modelo desconhecida",
        base_obra_divergente = "Base complementar: obra diferente do arquivo", base_valor_nao_numerico = "Base complementar: valor não numérico",
        base_valor_fora_da_lista = "Base complementar: opção fora da lista", base_mes_duplicado = "Base complementar: duas abas para o mesmo mês",
        base_base_ausente = "Base complementar: mês sem aba preenchida", base_base_sem_mes = "Base complementar: nenhum mês preenchido",
        base_subpasta_ignorada = "Base complementar: arquivo em subpasta", base_obra_desconhecida = "Base complementar: obra fora do painel",
        base_arquivo_duplicado = "Base complementar: dois arquivos da mesma obra", base_valor_fora_da_faixa = "Base complementar: valor fora da faixa",
        pasta_analise_critica_ausente = "Análise crítica: pasta não abre",
        pasta_analise_critica_vazia = "Análise crítica: pasta sem planilha",
        crono_pasta_ausente = "Base da cronograma: pasta não abre",
        crono_arquivo_ausente = "Base da cronograma: planilha não encontrada",
        crono_arquivo_ilegivel = "Base da cronograma: arquivo ilegível", crono_versao_desconhecida = "Base da cronograma: versão fora do nome",
        crono_aba_ausente = "Base da cronograma: aba PREVXREA não achada", crono_aba_previxrea_varias = "Base da cronograma: mais de uma aba PREVXREA",
        crono_layout = "Base da cronograma: layout não reconhecido", crono_aba_fluxo_ilegivel = "Base da cronograma: aba FLUXO não abre",
        crono_aba_fluxo_duplicada = "Base da cronograma: duas abas FLUXO para a obra", crono_curva_nao_fecha = "Base da cronograma: curva não fecha no orçamento",
        crono_situacao_indefinida = "Base da cronograma: obra sem orçamento", crono_obra_duplicada = "Base da cronograma: obra repetida",
        crono_sem_cadastro = "Base da cronograma: obra fora do cadastro", crono_sem_crono = "Base da cronograma: obra do cadastro sem linha na cronograma",
        crono_sem_vinculo = "Base da cronograma: obra do cadastro sem nome na cronograma", crono_sem_aba_fluxo = "Base da cronograma: obra em andamento sem aba FLUXO",
        crono_aba_fluxo_sem_meses = "Base da cronograma: aba FLUXO sem mês lido"],
    Severidades = [alta = 1, #"média" = 2, baixa = 3, info = 4],
    NomeTabela = [SaldoContrato = "Saldo de contrato", AdiantServicos = "Adiantamento de serviços não medidos",
        AdiantMateriais = "Adiantamento de materiais não estocados", Estoque = "Estoque de materiais",
        Equipamentos = "Equipamentos comprados", ReceitaPersonalizacao = "Receitas de personalizações",
        ContasPagar = "Contas a pagar dos medidos", ItensIrregulares = "Itens apontados irregularmente",
        Divida = "Dívida da obra a ser paga"],
    Aviso = (obra as text, mes as nullable date, aba as text, regra as text, severidade as text, detalhe as text) as record =>
        [Obra = obra, Mes = mes, Aba = aba, Regra = regra, Titulo = Record.Field(Titulos, regra),
         Severidade = severidade, OrdemSeveridade = Record.Field(Severidades, severidade), Detalhe = detalhe],
    Placeholder = (d as text) as logical =>
        let
            n = fxNormaliza(d),
            Palavra = Text.TrimEnd(n, {"0".."9", " "}),
            Numero = Text.Trim(Text.Range(n, Text.Length(Palavra)))
        in
            List.Contains({"servico", "material", "equipamento", "reforma", "divida", "item"}, Palavra)
                and Numero <> "" and Text.Select(Numero, {"0".."9"}) = Numero,

    Visiveis = Table.SelectRows(stgAbas, each [Oculta] <> true),

    // ---- Avisos de cada aba, olhando também a aba anterior da mesma obra
    PorObra = Table.Group(Visiveis, {"Obra"}, {{"Avisos", (t) =>
        let
            Abas = List.Buffer(Table.ToRecords(Table.Sort(t, {{"Mes", Order.Ascending}, {"OrdemAba", Order.Ascending}}))),
            DaAba = (i as number) as list =>
                let
                    a = Abas{i},
                    f = a[Leitura],
                    p = if i = 0 then null else Abas{i - 1}[Leitura],
                    pa = if i = 0 then null else Abas{i - 1},
                    TemP = p <> null and Record.FieldOrDefault(p, "Layout", false) = true,
                    Ok = Record.FieldOrDefault(f, "Layout", false) = true,
                    Nome = Text.Trim(a[Aba]),
                    Padrao = Text.Length(Nome) = 5 and Text.Select(Text.Start(Nome, 3), {"A".."Z"}) = Text.Start(Nome, 3)
                        and Text.Select(Text.End(Nome, 2), {"0".."9"}) = Text.End(Nome, 2),
                    R = (regra, sev, det) => Aviso(a[Obra], a[Mes], Nome, regra, sev, det),
                    Lista =
                        if not Ok then {R("layout", "alta", Record.FieldOrDefault(f, "Erro",
                            "bloco 'RESULTADO PARA UTILIZAR NA APRESENTAÇÃO' não encontrado"))}
                        else {
                            if a[Aba] <> Nome or not Padrao then R("nome_da_aba", "baixa", "'" & a[Aba] & "' fora do padrão MMMAA (3 letras + ano)") else null,
                            if pa <> null and pa[Mes] = a[Mes] then R("aba_duplicada", "média", "'" & Text.Trim(pa[Aba]) & "' e '" & Nome & "' são do mesmo mês; vale a que não é preliminar e, entre iguais, a mais à direita") else null,
                            if f[MesCelula] <> null and f[MesCelula] <> a[Mes] then R("mes_divergente", "média",
                                "célula 'Mês de análise' = " & Date.ToText(f[MesCelula], "MM/yyyy") & ", aba = " & Date.ToText(a[Mes], "MM/yyyy")) else null,
                            if f[PrevAcum] = null then R("previsto_vazio", "alta",
                                "previsto acumulado em branco na aba: sem ele não há desvio físico (o indicador fica sem dado)") else null,
                            if TemP and f[PrevAcum] <> null and p[PrevAcum] <> null and f[PrevAcum] + 0.000001 < p[PrevAcum] then R("previsto_regrediu", "alta",
                                "previsto acumulado caiu de " & Pct(p[PrevAcum]) & " para " & Pct(f[PrevAcum])) else null,
                            if TemP and f[ExecAcum] + 0.000001 < p[ExecAcum] then R("executado_regrediu", "alta",
                                "executado acumulado caiu de " & Pct(p[ExecAcum]) & " para " & Pct(f[ExecAcum])) else null,
                            if TemP and Number.Abs(f[ExecAcum] - (p[ExecAcum] + f[ExecMes])) > 0.0015 then R("executado_nao_fecha", "média",
                                "acum. anterior " & Pct(p[ExecAcum]) & " + mês " & Pct(f[ExecMes]) & " ≠ acum. " & Pct(f[ExecAcum])) else null,
                            if TemP and f[PrevAcum] <> null and p[PrevAcum] <> null and f[PrevMes] <> null
                                and Number.Abs(f[PrevAcum] - (p[PrevAcum] + f[PrevMes])) > 0.0015 and f[PrevAcum] >= p[PrevAcum]
                                then R("previsto_reprogramado", "baixa", "acum. anterior " & Pct(p[PrevAcum]) & " + mês " & Pct(f[PrevMes])
                                    & " ≠ acum. " & Pct(f[PrevAcum]) & " (cronograma reprogramado ou digitação)") else null,
                            if TemP and f[ResultadoAnteriorPlanilha] <> null and p[ResultadoPlanilha] <> null
                                and Number.Abs(f[ResultadoAnteriorPlanilha] - p[ResultadoPlanilha]) > 1
                                then R("mes_anterior_errado", "alta", "'Resultado do mês anterior' = " & Reais(f[ResultadoAnteriorPlanilha])
                                    & ", mas a aba " & Text.Trim(pa[Aba]) & " fechou " & Reais(p[ResultadoPlanilha])) else null,
                            if TemP and f[PrevistoMesRS] <> null and f[PrevistoMesRS] = p[PrevistoMesRS] then R("previsto_rs_repetido", "baixa",
                                "valor previsto do mês igual ao do mês anterior (" & Reais(f[PrevistoMesRS]) & ")") else null,
                            if TemP and f[TipoOrcamento] <> p[TipoOrcamento] then R("tipo_orcamento_mudou", "info",
                                Text.From(p[TipoOrcamento]) & " → " & Text.From(f[TipoOrcamento])) else null,
                            if f[Projeto] <> null and fxNormaliza(f[Projeto]) <> fxNormaliza(a[Obra]) then R("projeto_divergente", "média",
                                "célula Projeto = '" & Text.From(f[Projeto]) & "'") else null,
                            if f[ResultadoPlanilha] <> null then
                                let regra = f[ExecAcum] * f[Orcamento] + f[SomaSaldoContrato] + f[SomaAdiantServicos] + f[SomaAdiantMateriais]
                                    + f[SomaEstoque] + f[SomaEquipamentos] + f[SomaReceitaPersonalizacao] - f[SomaContasPagar]
                                    - (f[DesembolsadoBruto] - f[SomaItensIrregulares]) + f[SomaDivida]
                                in if Number.Abs(f[ResultadoPlanilha] - regra) >= 1 then R("conta_diverge", "alta",
                                    "pela regra da planilha daria " & Reais(regra) & "; a aba apresentou " & Reais(f[ResultadoPlanilha])) else null
                            else null
                        }
                        & List.Transform(List.Select(f[Tabelas], each [Soma] <> 0 and ([TotalPlanilha] = null
                                or Number.Abs([TotalPlanilha] - [Soma]) >= 1)),
                            each R("item_fora_da_conta", "alta", Reais([Soma]) & " digitados em '" & Record.Field(NomeTabela, [Grupo])
                                & "', mas o total dessa tabela não soma as linhas: o valor não entrou no resultado apresentado"))
                        & List.Combine(List.Transform(f[Tabelas], (tb) => List.Transform(
                            List.Select(tb[Itens], each Placeholder([Descricao])),
                            each R("item_sem_descricao", "baixa", Record.Field(NomeTabela, tb[Grupo]) & ": " & Reais([Valor]) & " na linha '"
                                & [Descricao] & "' (rótulo padrão, sem descrição)"))))
                in
                    List.RemoveNulls(Lista)
        in
            List.Combine(List.Transform(List.Positions(Abas), DaAba))}}),
    AvisosAbas = List.Combine(PorObra[Avisos]),

    // ---- Avisos do arquivo: abas mensais ocultas (layout antigo, fora da leitura)
    Ocultas = Table.Group(Table.SelectRows(stgAbas, each [Oculta] = true), {"Obra"},
        {{"Abas", each List.Sort([Aba]), type list}}),
    AvisosArquivo = List.Transform(Table.ToRecords(Ocultas), (o) =>
        Aviso(o[Obra], null, Text.Combine(List.FirstN(o[Abas], 3), ", ") & (if List.Count(o[Abas]) > 3 then "…" else ""),
            "abas_ocultas", "média", Text.From(List.Count(o[Abas])) & " abas mensais ocultas com layout antigo (fora da leitura)")),

    // ---- Bases complementares: os problemas que stgAbasBase achou, o mês repetido e a obra × mês sem aba na base
    AbasBase = Table.ToRecords(stgAbasBase),
    DaBase = (a as record) as list =>
        let
            Obra = if a[Obra] = null then "(bases complementares)" else a[Obra],
            Onde = if a[Aba] <> null then a[Aba] else if a[Arquivo] <> null then a[Arquivo] else ""
        in
            List.Transform(a[Problemas], (p) => Aviso(Obra, a[Mes], Onde, "base_" & p[Regra], p[Severidade], p[Detalhe]))
            // mês repetido: avisa a aba que perdeu quando ela estava preenchida ou é do mesmo arquivo da que valeu (a aba
            // vazia de uma cópia inteira da base já está no aviso de arquivo duplicado)
            & (if a[Mes] <> null and a[Valores] <> null and not a[Vale]
                and (a[Preenchida] or Text.StartsWith(a[Vencedora], a[Arquivo] & " › ")) then {Aviso(Obra, a[Mes], Onde, "base_mes_duplicado",
                "média", "'" & a[Aba] & "' repete o mês de outra aba da obra; vale '" & a[Vencedora] & "' (a preenchida mais à direita; entre "
                    & "arquivos, o modificado por último)")} else {}),
    ChaveBase = (obra as text, mes as date) as text => fxNormaliza(obra) & "|" & Date.ToText(mes, "yyyy-MM"),
    // dois arquivos na raiz para a mesma obra (cópia, conflito de sincronização): um aviso por obra
    ArquivosPorObra = Table.Group(Table.Distinct(Table.SelectColumns(Table.SelectRows(stgAbasBase,
            each [Mes] <> null and [Valores] <> null), {"Obra", "Arquivo", "DataArquivo"})), {"Obra"},
        {{"Arquivos", each Table.Sort(_, {{"DataArquivo", Order.Descending}}), type table}}),
    AvisosArquivoBase = List.Transform(Table.ToRecords(Table.SelectRows(ArquivosPorObra, each Table.RowCount([Arquivos]) > 1)),
        (o) => Aviso(o[Obra], null, o[Arquivos]{0}[Arquivo], "base_arquivo_duplicado", "média",
            Text.From(Table.RowCount(o[Arquivos])) & " arquivos da obra na pasta: " & Text.Combine(o[Arquivos][Arquivo], ", ")
                & ". Mês a mês vale a aba preenchida do modificado por último ('" & o[Arquivos]{0}[Arquivo] & "'); apague a cópia")),
    // "com base" = aba que vale e está preenchida (aba vazia = sem base, como em fBaseObra)
    ComAbaBase = List.Buffer(List.Transform(List.Select(AbasBase, each [Vale] and [Preenchida]),
        each ChaveBase([Obra], [Mes]))),
    ObrasComBase = List.Buffer(List.Distinct(List.Transform(List.Select(AbasBase, each [Vale] and [Preenchida]),
        each fxNormaliza([Obra])))),
    SemBase = List.Select(Table.ToRecords(Table.SelectColumns(fAnaliseCritica, {"Obra", "Mes"})),
        each not List.Contains(ComAbaBase, ChaveBase([Obra], [Mes]))),
    // obra cuja base não tem nenhum mês preenchido: um aviso só (com as bases ainda vazias, um por mês seria ruído)
    SemNenhumMes = Table.Group(Table.FromRecords(List.Select(SemBase,
            each not List.Contains(ObrasComBase, fxNormaliza([Obra]))), type table [Obra = text, Mes = date]),
        {"Obra"}, {{"Meses", each List.Sort([Mes]), type list}}),
    AvisosBase = List.Select(List.Combine(List.Transform(AbasBase, DaBase)), each [Mes] = null or [Mes] >= pInicioHistorico)
        & List.Transform(List.Select(SemBase, each List.Contains(ObrasComBase, fxNormaliza([Obra]))),
            each Aviso([Obra], [Mes], "", "base_base_ausente", "info", "a obra tem Análise Crítica no mês e a base "
                & "complementar não tem a aba do mês, ou a aba está vazia: a obra fica pendente na nota"))
        & AvisosArquivoBase
        & List.Transform(Table.ToRecords(SemNenhumMes), each Aviso([Obra], null, "", "base_base_sem_mes", "info",
            "a base complementar não tem nenhum mês preenchido: os " & Text.From(List.Count([Meses]))
                & " meses com Análise Crítica (" & Date.ToText(List.First([Meses]), "MM/yyyy") & " a "
                & Date.ToText(List.Last([Meses]), "MM/yyyy") & ") ficam pendentes na nota")),

    // ---- cronograma (stgCrono): problemas da planilha que a consulta leu, e o vínculo da cronograma com o cadastro (nome_crono)
    LinhasCrono = Table.ToRecords(stgCrono),
    AvisosCrono = List.Combine(List.Transform(LinhasCrono, (g) =>
        List.Transform(if g[Problemas] = null then {} else g[Problemas], (p) =>
            Aviso(if g[ObraCrono] = null then "(cronograma)" else g[ObraCrono], null,
                if p[Aba] = null then "" else p[Aba], "crono_" & p[Regra], p[Severidade], p[Detalhe])))),
    NomesCrono = List.Select(List.Transform(LinhasCrono, (g) => g[ObraCrono]), (n) => n <> null),
    CadastroLinhas = Table.ToRecords(stgCadastro),
    NomesCadastro = List.Select(List.Transform(CadastroLinhas, (c) => c[NomeCrono]), (n) => n <> null),
    AvisosVinculoCrono = List.Combine({
        List.Transform(List.Select(CadastroLinhas, (c) => c[NomeCrono] = null), (c) =>
            Aviso(c[Obra], null, "", "crono_sem_vinculo", "alta",
                "a obra está no cadastro sem nome_crono: a cronograma não é lida para ela; situação, orçamento e datas ficam vazios")),
        if List.IsEmpty(NomesCrono) then {} else List.Transform(List.Select(CadastroLinhas, (c) => c[NomeCrono] <> null and not List.Contains(NomesCrono, c[NomeCrono])), (c) =>
            Aviso(c[Obra], null, "", "crono_sem_crono", "alta",
                "o cadastro diz que a obra é '" & c[NomeCrono] & "' na cronograma, mas a planilha não tem essa obra: situação, orçamento e datas ficam vazios")),
        List.Transform(List.Select(LinhasCrono, (g) => g[ObraCrono] <> null and not List.Contains(NomesCadastro, g[ObraCrono])), (g) =>
            Aviso(g[ObraCrono], null, "", "crono_sem_cadastro", "média",
                "obra da cronograma sem linha no cadastro: entra no painel sem código nem SPE; para completar, incluir a obra no cadastro (obras_cadastro.csv, na pasta de dados do projeto) com o nome_crono"))
    }),
    // ---- pasta da análise crítica que não abre (fxArquivosPlanilhas): as obras ficam sem análise crítica
    ErroPlanilhas = Table.SelectRows(fxArquivosPlanilhas, each [ErroPasta] <> null),
    XlsxPlanilhas = Table.SelectRows(fxArquivosPlanilhas, each Text.Lower([Extension]) = ".xlsx"),
    AvisosPlanilhas = if Table.RowCount(ErroPlanilhas) > 0
        then {Aviso("(análise crítica)", null, "", "pasta_analise_critica_ausente", "alta", ErroPlanilhas{0}[ErroPasta])}
        else if Table.RowCount(XlsxPlanilhas) = 0
        then {Aviso("(análise crítica)", null, "", "pasta_analise_critica_vazia", "média",
            "a pasta de análise crítica não tem nenhum .xlsx: as obras ficam sem análise crítica")}
        else {},
    Todos = List.Select(AvisosAbas, each [Mes] >= pInicioHistorico) & AvisosArquivo & AvisosBase & AvisosCrono & AvisosVinculoCrono & AvisosPlanilhas,
    Tabela = Table.FromRecords(Todos, type table [Obra = text, Mes = nullable date, Aba = text, Regra = text,
        Titulo = text, Severidade = text, OrdemSeveridade = Int64.Type, Detalhe = text]),
    Ordenado = Table.Sort(Tabela, {{"OrdemSeveridade", Order.Ascending}, {"Obra", Order.Ascending}, {"Mes", Order.Ascending}})
in
    Ordenado
