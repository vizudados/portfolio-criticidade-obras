# ponte.ps1 - cliente minimo da Desktop Bridge (pipe \\.\pipe\pbi-desktop-bridge-<PID>, JSON-RPC com Content-Length).
# So conversa com a instancia que tem o PBIP deste projeto aberto (confere currentFilePath). Nao edita o relatorio.
# ASCII puro de proposito (console cp850).
#
# Uso:
#   pwsh -NoProfile -File ponte.ps1 -Acao estado
#   pwsh -NoProfile -File ponte.ps1 -Acao foto -Pagina T1 [-Escala 1] [-Saida ..\qa\desktop\t1.png] [-Espera 4]
#   pwsh -NoProfile -File ponte.ps1 -Acao recarregar          (file.reload/v1, so o relatorio)
# Codigos: 0 ok | 1 sem instancia/pipe | 2 erro da ponte.
param(
  [Parameter(Mandatory = $true)][ValidateSet('estado', 'foto', 'recarregar', 'manifesto')][string]$Acao,
  [string]$Pagina = 'T1',
  [int]$Escala = 1,
  [string]$Saida,
  [int]$Espera = 0
)
$ErrorActionPreference = 'Stop'
$Raiz = Split-Path -Parent $PSScriptRoot
$Alvo = (Get-ChildItem -LiteralPath (Join-Path $Raiz 'pbip') -Filter '*.pbip' | Select-Object -First 1).FullName

function Read-Frame($pipe) {
  $win = ''; $one = New-Object byte[] 1; $hdr = New-Object Text.StringBuilder
  while ($true) {
    if ($pipe.Read($one, 0, 1) -le 0) { throw 'pipe fechado' }
    $c = [char]$one[0]; [void]$hdr.Append($c)
    $win = ($win + $c); if ($win.Length -gt 4) { $win = $win.Substring(1) }
    if ($win -eq "`r`n`r`n") { break }
  }
  $len = [int]([regex]::Match($hdr.ToString(), 'Content-Length:\s*(\d+)').Groups[1].Value)
  $buf = New-Object byte[] $len; $off = 0
  while ($off -lt $len) { $n = $pipe.Read($buf, $off, $len - $off); if ($n -le 0) { throw 'eof' }; $off += $n }
  return ([Text.Encoding]::UTF8.GetString($buf) | ConvertFrom-Json)
}

function Invoke-Ponte($pipe, [int]$id, [string]$metodo, $params) {
  $json = @{ jsonrpc = '2.0'; id = $id; method = $metodo; params = @{ client = 'bev-ponte'; args = $params } } | ConvertTo-Json -Compress -Depth 10
  $corpo = [Text.Encoding]::UTF8.GetBytes($json)
  $cab = [Text.Encoding]::ASCII.GetBytes("Content-Length: $($corpo.Length)`r`n`r`n")
  $pipe.Write($cab, 0, $cab.Length); $pipe.Write($corpo, 0, $corpo.Length); $pipe.Flush()
  $r = Read-Frame $pipe
  if ($r.error) { throw ('ponte: ' + $r.error.message) }
  return $r.result
}

$pids = @([IO.Directory]::GetFiles('\\.\pipe\') | ForEach-Object { if ($_ -match 'pbi-desktop-bridge-(\d+)$') { [int]$matches[1] } })
if ($pids.Count -eq 0) { Write-Host 'nenhum pipe da ponte (Desktop fechado ou preview desligado)'; exit 1 }
$achou = $null
foreach ($p in $pids) {
  $pipe = New-Object System.IO.Pipes.NamedPipeClientStream('.', "pbi-desktop-bridge-$p", [System.IO.Pipes.PipeDirection]::InOut)
  try {
    $pipe.Connect(5000)
    $st = Invoke-Ponte $pipe 1 'application.state.get/v1' @{}
    if ([string]$st.currentFilePath -ieq $Alvo) { $achou = @{ Pipe = $pipe; Pid = $p; Estado = $st }; break }
    $pipe.Dispose()
  } catch { $pipe.Dispose() }
}
if (-not $achou) { Write-Host 'nenhuma instancia com o PBIP deste projeto aberto'; exit 1 }
$pipe = $achou.Pipe
try {
  switch ($Acao) {
    'manifesto' {
      $r = Invoke-Ponte $pipe 9 'bridge.manifest' @{}
      Write-Host ($r | ConvertTo-Json -Depth 12)
    }
    'estado' {
      Write-Host ('pid=' + $achou.Pid + ' naoSalvo=' + $achou.Estado.hasUnsavedChanges)
    }
    'recarregar' {
      $r = Invoke-Ponte $pipe 2 'file.reload/v1' @{ reloadModelDefinition = $false }
      Write-Host ('recarregado: ' + ($r | ConvertTo-Json -Compress))
    }
    'foto' {
      if (-not ('BevPonte.Api' -as [type])) {
        Add-Type -Namespace BevPonte -Name Api -MemberDefinition @"
[DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
[DllImport("user32.dll")] public static extern bool ShowWindowAsync(IntPtr h, int cmd);
[DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr depois, int x, int y, int cx, int cy, uint flags);
"@
      }
      $h = (Get-Process -Id $achou.Pid).MainWindowHandle
      $estavaMin = ($h -ne [IntPtr]::Zero) -and [BevPonte.Api]::IsIconic($h)
      if ($estavaMin) { [void][BevPonte.Api]::ShowWindowAsync($h, 4); Start-Sleep -Seconds 3 }   # SW_SHOWNOACTIVATE
      # janela coberta para as animacoes dos visuais HTML: traz para cima sem ativar (HWND_TOP; SWP_NOSIZE |
      # SWP_NOMOVE | SWP_NOACTIVATE | SWP_SHOWWINDOW); a rede de seguranca do JS termina tudo em 2,5 s
      if ($h -ne [IntPtr]::Zero) { [void][BevPonte.Api]::SetWindowPos($h, [IntPtr]::Zero, 0, 0, 0, 0, 0x53) }
      # a captura leva a pagina para a frente e fotografa na hora: os visuais personalizados ainda estao carregando.
      # Com -Espera, uma captura previa (descartada) abre a pagina e a foto sai depois da espera.
      if ($Espera -gt 0) { [void](Invoke-Ponte $pipe 4 'report.snapshot.capture/v1' @{ pageId = $Pagina; scale = 1 }); Start-Sleep -Seconds $Espera }
      if (-not $Saida) { $Saida = Join-Path $Raiz ('qa\desktop\' + $Pagina.ToLower() + '-' + (Get-Date -Format 'HHmmss') + '.png') }
      $Saida = [IO.Path]::GetFullPath($Saida)
      $r = Invoke-Ponte $pipe 3 'report.snapshot.capture/v1' @{ pageId = $Pagina; scale = $Escala }
      $pasta = Split-Path -Parent $Saida
      if (-not (Test-Path -LiteralPath $pasta)) { New-Item -ItemType Directory -Force -Path $pasta | Out-Null }
      [IO.File]::WriteAllBytes($Saida, [Convert]::FromBase64String($r.payload))
      Write-Host ('foto ' + $Saida + ' pagina=' + $r.pageId)
      if ($estavaMin) { [void][BevPonte.Api]::ShowWindowAsync($h, 6) }
    }
  }
} catch {
  Write-Host ('ERRO ' + $_.Exception.Message); exit 2
} finally { $pipe.Dispose() }
exit 0
