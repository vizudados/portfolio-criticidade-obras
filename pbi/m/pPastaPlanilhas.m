/*
@tipo: parametro
@descricao: Pasta da análise crítica, relativa à raiz dos dados (pOrigem). Cada obra é uma subpasta, com o nome que está na coluna pasta_analise_critica do cadastro; planilha fora de subpasta, ou marcada OBSOLETO, não é lida. Pasta ausente: as obras ficam sem análise crítica e o aviso vai para fConferencia (a atualização segue).
*/
"analise-critica" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]
