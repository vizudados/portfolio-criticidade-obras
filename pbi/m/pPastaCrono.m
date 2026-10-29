/*
@tipo: parametro
@descricao: Pasta da cronograma físico-financeiro, relativa à raiz dos dados (pOrigem). Deve ter um só arquivo, a PLANILHA DE FLUXO FINANCEIRO com ATUALIZADO EM MMAAAA no nome; a leitura pega o de versão mais recente, só da raiz da pasta. Só leitura. Pasta ausente: a cronograma fica vazia e o aviso vai para fConferencia (a atualização segue).
*/
"cronograma" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]
