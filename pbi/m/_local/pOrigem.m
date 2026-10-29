/*
@tipo: parametro
@descricao: PERFIL LOCAL (gerar_modelo.py --perfil local). De onde o painel lê os dados neste computador: "Pasta" (Folder.Files a partir de pPastaDados), "SharePoint" (o site pSiteSharePoint, a partir de pPastaSharePoint) ou "Embutido" (os arquivos de dados/ dentro do modelo). O perfil padrão (a entrega) só tem "Embutido".
*/
"Pasta" meta [IsParameterQuery = true, List = {"Pasta", "SharePoint", "Embutido"}, DefaultValue = "Pasta", Type = "Text", IsParameterQueryRequired = true]
