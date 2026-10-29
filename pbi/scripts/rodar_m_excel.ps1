# Bancada do Power Query: roda as consultas de pbi/m/ no motor do Power Query do Excel (o mesmo mashup do Power BI)
# e grava o resultado de cada tabela numa pasta de trabalho, para conferir contra o oráculo Python.
#
# Por que no Excel: o Power BI Desktop do usuário fica livre (L046) e a consulta M é a mesma.
#
#   pwsh -File pbi/scripts/rodar_m_excel.ps1 [-Tabelas fAnaliseCritica,fItens] [-Saida pbi/qa/m/saida.xlsx]
param(
    [string[]]$Tabelas = @("fAnaliseCritica", "fItens", "dItem", "dObra", "dMes", "dMesRef", "fConferencia"),
    [string]$Saida = (Join-Path $PSScriptRoot "..\qa\m\saida.xlsx"),
    [string]$PastaM = (Join-Path $PSScriptRoot "..\m")
)
# -File entrega "fAnaliseCritica,fItens" como um único nome; separa por vírgula aqui (também aceita array).
$Tabelas = @($Tabelas | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() } | Where-Object { $_ })
$ErrorActionPreference = "Stop"
$Saida = [IO.Path]::GetFullPath($Saida)
New-Item -ItemType Directory -Force -Path (Split-Path $Saida) | Out-Null

$xl = New-Object -ComObject Excel.Application
$relatorio = @()
try {
    $xl.Visible = $false
    $xl.DisplayAlerts = $false
    $wb = $xl.Workbooks.Add()
    foreach ($arq in Get-ChildItem -Path $PastaM -Filter "*.m") {
        $formula = [IO.File]::ReadAllText($arq.FullName, [Text.Encoding]::UTF8)
        [void]$wb.Queries.Add($arq.BaseName, $formula)
    }
    try { $wb.Queries.FastCombine = $true } catch { }
    foreach ($nome in $Tabelas) {
        if (-not ($wb.Queries | Where-Object { $_.Name -eq $nome })) { $relatorio += "$nome`tAUSENTE"; continue }
        $ws = $wb.Worksheets.Add()
        $ws.Name = $nome
        $conexao = "OLEDB;Provider=Microsoft.Mashup.OleDb.1;Data Source=`$Workbook`$;Location=$nome;Extended Properties=`"`""
        $lo = $ws.ListObjects.Add(0, $conexao, [Type]::Missing, 1, $ws.Range("A1"))
        $lo.QueryTable.CommandType = 2
        $lo.QueryTable.CommandText = "SELECT * FROM [$nome]"
        $lo.QueryTable.BackgroundQuery = $false
        $t0 = Get-Date
        try {
            [void]$lo.QueryTable.Refresh($false)
            $relatorio += ("{0}`tOK`t{1} linhas`t{2:n1} s" -f $nome, $lo.ListRows.Count, ((Get-Date) - $t0).TotalSeconds)
        }
        catch {
            $relatorio += ("{0}`tERRO`t{1}" -f $nome, $_.Exception.Message)
        }
    }
    if (Test-Path -LiteralPath $Saida) { Remove-Item -LiteralPath $Saida -Force }
    $wb.SaveAs($Saida, 51)
    $wb.Close($false)
}
finally {
    $xl.Quit()
    [void][Runtime.InteropServices.Marshal]::ReleaseComObject($xl)
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
$relatorio | ForEach-Object { Write-Output $_ }
