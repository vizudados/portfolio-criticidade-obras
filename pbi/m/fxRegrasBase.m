/*
@tipo: funcao
@descricao: Regras de leitura das bases complementares (modelo BC 2.0), GERADAS por pbi/scripts/contas_base.py a partir do dicionário NOTA (fonte única): a versão do modelo, o rótulo de cada campo na coluna B (normalizado, como fxNormaliza) com o rótulo para os avisos, e a faixa válida de cada campo numérico (fora dela, o campo fica sem dado e stgAbasBase avisa). Não edite à mão.
*/
() as record =>
    [
        Versao = "BC 2.0",
        Campos = {{"PPC", {"ppc do mes"}, "PPC do mês"}, {"ServicosVerificados", {"servicos verificados"}, "Serviços verificados"}, {"AprovadosPrimeira", {"aprovados na primeira inspecao"}, "Aprovados na primeira inspeção"}, {"HHT", {"horas-homem trabalhadas (hht)"}, "Horas-homem trabalhadas (HHT)"}, {"Acidentes", {"acidentes com afastamento"}, "Acidentes com afastamento"}, {"DiasPerdidos", {"dias perdidos"}, "Dias perdidos"}, {"NR18Aplicaveis", {"itens nr-18 aplicaveis"}, "Itens NR-18 aplicáveis"}, {"NR18Conformes", {"itens nr-18 conformes"}, "Itens NR-18 conformes"}, {"PedidosPrevistos", {"pedidos com entrega prevista"}, "Pedidos com entrega prevista"}, {"PedidosNoPrazo", {"pedidos entregues no prazo e completos"}, "Pedidos entregues no prazo e completos"}, {"DiasChuva", {"dias impraticaveis por chuva"}, "Dias impraticáveis por chuva"}},
        Faixas = [PPC = {0, 1}, ServicosVerificados = {0, 100000}, AprovadosPrimeira = {0, 100000}, HHT = {0, 10000000}, Acidentes = {0, 1000}, DiasPerdidos = {0, 100000}, NR18Aplicaveis = {0, 10000}, NR18Conformes = {0, 10000}, PedidosPrevistos = {0, 100000}, PedidosNoPrazo = {0, 100000}, DiasChuva = {0, 31}]
    ]
