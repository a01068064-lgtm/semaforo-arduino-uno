# SEMAFORO servidor Windows sin dependencias
param([int]$Puerto = 8000)
Add-Type -AssemblyName System.IO.Ports 2>$null
$base = Split-Path -Parent $MyInvocation.MyCommand.Path
$htmlPath = Join-Path (Split-Path -Parent $base) 'web\index.html'
$global:st = $null; $global:stTime = [DateTime]::MinValue; $global:serial = $null
try {
  $ports = [System.IO.Ports.SerialPort]::GetPortNames() | Sort-Object
  foreach ($p in $ports) {
    try { $s = New-Object System.IO.Ports.SerialPort($p,9600,'None',8,'one'); $s.ReadTimeout=200; $s.Open(); $global:serial=$s; break } catch {}
  }
} catch {}
function Get-Sim() {
  $t=[int]([DateTime]::UtcNow-[DateTime]::new(2026,1,1)).TotalSeconds; $c=$t%50
  if($c -lt 20){ return @{light='RED';pin=2;remaining=(20-$c)} }
  elseif($c -lt 45){ return @{light='GREEN';pin=4;remaining=(45-$c)} }
  else{ return @{light='YELLOW';pin=3;remaining=(50-$c)} }
}
function Get-State() {
  if($global:serial -and $global:serial.IsOpen){
    try{
      while($global:serial.BytesToRead -gt 0){
        $l=$global:serial.ReadLine().Trim().ToUpper() -replace '^STATE:',''
        if($l -match '^(RED|GREEN|YELLOW)[\s:,]+(\d+)'){
          $global:st=@{light=$Matches[1];pin=@{RED=2;YELLOW=3;GREEN=4}[$Matches[1]];remaining=[int]$Matches[2]}; $global:stTime=Get-Date
        }
      }
      if($global:st -and ((Get-Date)-$global:stTime).TotalSeconds -lt 3){
        return @{light=$global:st.light;pin=$global:st.pin;remaining=$global:st.remaining;durations=@{RED=20;YELLOW=5;GREEN=25};source='arduino';port=$global:serial.PortName}
      }
    }catch{}
  }
  $s=Get-Sim; return @{light=$s.light;pin=$s.pin;remaining=$s.remaining;durations=@{RED=20;YELLOW=5;GREEN=25};source='simulacion';port=$(if($global:serial){$global:serial.PortName}else{$null})}
}
$l=New-Object System.Net.HttpListener; $l.Prefixes.Add("http://localhost:$Puerto/"); $l.Start()
Write-Host "Web en http://localhost:$Puerto"
while($l.IsListening){
  $c=$l.GetContext(); $q=$c.Request; $r=$c.Response
  try{
    if($q.Url.AbsolutePath -eq '/api/status'){
      $b=[Text.Encoding]::UTF8.GetBytes((Get-State | ConvertTo-Json -Compress)); $r.ContentType='application/json'
      $r.ContentLength64=$b.Length; $r.OutputStream.Write($b,0,$b.Length)
    } else {
      $b=[IO.File]::ReadAllBytes($htmlPath); $r.ContentType='text/html; charset=utf-8'
      $r.ContentLength64=$b.Length; $r.OutputStream.Write($b,0,$b.Length)
    }
  }catch{} finally{$r.OutputStream.Close()}
}
