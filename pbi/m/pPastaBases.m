/*
@tipo: parametro
@descricao: Pasta das bases complementares, relativa à raiz dos dados (pOrigem): um .xlsx por obra (Base complementar - <OBRA>.xlsx), uma aba por mês (MMM AAAA); o arquivo MODELO fica de fora e só vale a raiz da pasta. Pasta ausente: as obras ficam pendentes e o aviso vai para fConferencia (a atualização segue).
*/
"bases-complementares" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]
