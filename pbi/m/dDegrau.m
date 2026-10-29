/*
@tipo: tabela
@descricao: Degraus da cascata "Como o resultado se forma" (Tela 02, F3 · docs/08 §5): valor agregado (crédito pelo executado), custo aplicado (o que já virou obra, com a dívida), resultado aplicado (VA − custo), a realizar (saldo de contrato e equipamentos: a planilha conta como ganho e ainda não aconteceu) e o resultado da planilha. Desconectada: as contas leem o degrau da linha (tooltip do degrau).
@coluna: Degrau | texto | chave | Código do degrau.
@coluna: Ordem | inteiro | formato=0 | Posição na cascata.
@coluna: Rotulo | texto | ordenar=Ordem | Nome do degrau.
@coluna: Sinal | inteiro | formato=0 | +1 soma no resultado; −1 desconta; 0 é um resultado (parcial ou o da planilha).
*/
let
    Tabela = #table(type table [Degrau = text, Ordem = Int64.Type, Rotulo = text, Sinal = Int64.Type], {
        {"ValorAgregado", 1, "Valor agregado", 1},
        {"CustoAplicado", 2, "Custo aplicado", -1},
        {"ResultadoAplicado", 3, "Resultado aplicado", 0},
        {"ARealizar", 4, "A realizar", 1},
        {"Resultado", 5, "Resultado da planilha", 0}
    })
in
    Tabela
