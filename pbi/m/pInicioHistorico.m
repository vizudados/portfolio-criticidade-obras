/*
@tipo: parametro
@descricao: Primeiro mês do histórico do painel: out/25, para mostrar 12 meses fechados (out/25 a set/26) dos dados fictícios. As abas anteriores continuam sendo lidas, mas só para o "mês anterior" do primeiro mês.
*/
#date(2025, 10, 1) meta [IsParameterQuery = true, Type = "Date", IsParameterQueryRequired = true]
