/*
@tipo: tabela
@descricao: Os 9 itens da Nota da obra (docs/08 §3), com a dimensão, o máximo, a fonte, a unidade do X, o texto das faixas e a explicação de uma linha. Eixo das listas e dos tooltips por item (e, por Dimensao, das listas por dimensão). GERADA por pbi/scripts/contas_base.py a partir do dicionário NOTA (fonte única): não edite à mão.
@coluna: Item | texto | chave | Código do item.
@coluna: Ordem | inteiro | formato=0 | Ordem do item na régua (1 = custo).
@coluna: Dimensao | texto | ordenar=OrdemDimensao | Dimensão (Custo, Prazo, Caixa, Qualidade, Segurança, Suprimentos, Gestão).
@coluna: OrdemDimensao | inteiro | oculta; formato=0 | Ordem da dimensão.
@coluna: Rotulo | texto | ordenar=Ordem | Nome do item.
@coluna: RotuloCurto | texto | ordenar=Ordem | Nome curto, para listas.
@coluna: RotuloMedio | texto | ordenar=Ordem | Nome médio, para tabelas de tooltip.
@coluna: RotuloFrase | texto | | Nome dentro de frase, com artigo (o custo, a previsão de caixa).
@coluna: Maximo | decimal | formato=0.00 | Pontos máximos do item (a soma dá 10).
@coluna: Fonte | texto | | Análise Crítica ou Base complementar.
@coluna: Unidade | texto | | Unidade do X: indice, meses, pct, taxa ou checagens.
@coluna: FaixaTexto | texto | | Faixas → pontos, para exibição.
@coluna: Explica | texto | | O que o item mede, em uma linha.
*/
let
    Tabela = #table(
        type table [Item = text, Ordem = Int64.Type, Dimensao = text, OrdemDimensao = Int64.Type, Rotulo = text,
            RotuloCurto = text, RotuloMedio = text, RotuloFrase = text, Maximo = number, Fonte = text, Unidade = text,
            FaixaTexto = text, Explica = text],
        {
            {"custo", 1, "Custo", 1, "Custo (IDC)", "Custo", "Custo · IDC", "o custo", 3, "Análise Crítica", "indice", "IDC ≥ 1,00 → 3 · 0,98 ≤ IDC < 1,00 → 2,5 · 0,96 ≤ IDC < 0,98 → 2 · 0,94 ≤ IDC < 0,96 → 1,5 · 0,92 ≤ IDC < 0,94 → 1 · 0,90 ≤ IDC < 0,92 → 0,5 · IDC < 0,90 → 0", "Para cada R$ 1,00 aplicado, quanto de orçamento a obra entregou (valor agregado ÷ custo aplicado)."},
            {"prazo", 2, "Prazo", 2, "Atraso em meses", "Atraso", "Prazo · atraso", "o atraso", 2, "Análise Crítica", "meses", "atraso ≤ 0,5 mês → 2 · 0,5 mês < atraso ≤ 1 mês → 1,5 · 1 mês < atraso ≤ 2 meses → 1 · 2 meses < atraso ≤ 3 meses → 0,5 · atraso > 3 meses → 0", "Quantos meses a obra está atrás do cronograma: o executado de hoje é o previsto de quantos meses atrás."},
            {"ppc", 3, "Prazo", 2, "Plano semanal cumprido (PPC)", "PPC", "Prazo · PPC", "o plano semanal", 1, "Base complementar", "pct", "PPC ≥ 80% → 1 · 70% ≤ PPC < 80% → 0,5 · 60% ≤ PPC < 70% → 0,25 · PPC < 60% → 0", "De cada 10 tarefas prometidas na semana, quantas foram feitas (média do mês)."},
            {"caixa", 4, "Caixa", 3, "Acerto da previsão de caixa", "Caixa", "Previsão de caixa", "a previsão de caixa", 1, "Análise Crítica", "pct", "desvio < 10% → 1 · 10% ≤ desvio ≤ 20% → 0,5 · desvio > 20% → 0", "Quanto o desembolso do mês fugiu do previsto, para mais ou para menos."},
            {"inspecao", 5, "Qualidade", 4, "Aprovação na 1.ª inspeção", "1.ª inspeção", "Qualidade · 1.ª inspeção", "a aprovação na 1.ª inspeção", 1, "Base complementar", "pct", "aprovação ≥ 95% → 1 · 90% ≤ aprovação < 95% → 0,75 · 85% ≤ aprovação < 90% → 0,5 · 80% ≤ aprovação < 85% → 0,25 · aprovação < 80% → 0", "Serviços aprovados na primeira inspeção, sem retrabalho, entre os verificados no mês."},
            {"acidentes", 6, "Segurança", 5, "Frequência de acidentes", "Acidentes", "Segurança · acidentes", "a frequência de acidentes", 0.5, "Base complementar", "taxa", "TF = 0 → 0,5 · 0 < TF ≤ 7,5 → 0,25 · TF > 7,5 → 0", "Acidentes com afastamento por milhão de horas trabalhadas, nos últimos 12 meses (NBR 14280)."},
            {"nr18", 7, "Segurança", 5, "Canteiro conforme NR-18", "NR-18", "Segurança · NR-18", "o canteiro (NR-18)", 0.5, "Base complementar", "pct", "conformidade ≥ 95% → 0,5 · 85% ≤ conformidade < 95% → 0,25 · conformidade < 85% → 0", "Itens do checklist da NR-18 conformes, entre os aplicáveis no mês."},
            {"entregas", 8, "Suprimentos", 6, "Entregas no prazo e completas", "Entregas", "Suprimentos · entregas", "as entregas de material", 0.5, "Base complementar", "pct", "entregas ≥ 90% → 0,5 · 80% ≤ entregas < 90% → 0,25 · entregas < 80% → 0", "Pedidos de material entregues no prazo e completos, entre os previstos no mês."},
            {"analise", 9, "Gestão", 7, "Análise crítica sem pendência", "Análise crítica", "Gestão · análise crítica", "a análise crítica", 0.5, "Análise Crítica", "checagens", "3 de 3 → 0,5 · 2 de 3 → 0,25 · 0 ou 1 de 3 → 0", "Checagens da planilha do mês: a conta fecha, há justificativa quando o caixa desvia e o previsto não caiu."}
        })
in
    Tabela
