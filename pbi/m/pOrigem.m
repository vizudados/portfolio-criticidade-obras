/*
@tipo: parametro
@descricao: De onde o painel lê os dados. Na entrega é sempre "Embutido": os arquivos de dados/ (análise crítica, bases complementares, cronograma e cadastro) dentro do próprio modelo, em fxDadosEmbutidos; o serviço atualiza sem fonte externa, sem credencial nem gateway. As outras origens existem só no perfil local do gerador (pbi/m/_local, gerar_modelo.py --perfil local).
*/
"Embutido" meta [IsParameterQuery = true, List = {"Embutido"}, DefaultValue = "Embutido", Type = "Text", IsParameterQueryRequired = true]
