# mood/client/__main__.py
"""MUD client entrypoint: запускает клиента."""

import cmd
import cowsay
import shlex
import sys
import socket
import threading
import time
import argparse
import re


class MUDclient(cmd.Cmd):
    """Реализация клиента."""

    prompt = ">> "
    running = True

    def __init__(self, soc=None):
        super().__init__()
        self.soc = soc or socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def do_up(self, arg):
        """Ход вверх."""
        self.soc.sendall(b"move 0 1\n")

    def do_down(self, arg):
        """Ход вниз."""
        self.soc.sendall(b"move 0 -1\n")

    def do_left(self, arg):
        """Ход влево."""
        self.soc.sendall(b"move -1 0\n")

    def do_right(self, arg):
        """Ход вправо."""
        self.soc.sendall(b"move 1 0\n")

    def do_locale(self, arg):
        """locale <locale_name> — установить языковую локаль (en_US или ru_RU)."""
        if arg not in ("en_US", "ru_RU"):
            print("Unsupported locale. Available: en_US, ru_RU.UTF-8")
            return
        self.soc.sendall(f"locale {arg}\n".encode())


    def complete_locale(self, text, line, begidx, endidx):
        """Автодополнение локали."""
        return [l for l in ("en_US", "ru_RU") if l.startswith(text)]


    def do_addmon(self, arg):
        """
        Addmon <monster_name> hello <hello_string>.

        hp <hitpoints> coords <x> <y>.
        """
        tokens = shlex.split(arg)
        if len(tokens) != 8:
            print("Invalid arguments")
            return
        name, *pars = tokens
        try:
            i_hello = pars.index("hello")
            hello = pars[i_hello + 1]
            i_hp = pars.index("hp")
            hp_str = pars[i_hp + 1]
            i_coords = pars.index("coords")
            x_str, y_str = pars[i_coords + 1], pars[i_coords + 2]
        except (ValueError, IndexError):
            print("Invalid arguments")
            return
        if not (hp_str.isdigit() and x_str.isdigit() and y_str.isdigit()):
            print("Invalid arguments")
            return
        hp, x, y = int(hp_str), int(x_str), int(y_str)
        if hp <= 0:
            print("Invalid arguments")
            return
        valid_cows = cowsay.list_cows() + ["jgsbat"]
        if name not in valid_cows:
            print("Invalid arguments")
            return
        message = f"addmon {name} {hp} {y} {x} '{hello}'\n"
        self.soc.sendall(message.encode())

    def do_attack(self, arg):
        """Attack <имя монстра> with <имя оружия>."""
        parts = arg.split()
        if len(parts) < 1 or len(parts) == 2:
            print("Invalid arguments")
            return
        if len(parts) > 3:
            print("Invalid arguments")
            return
        name = parts[0]
        if len(parts) > 1 and parts[1] != "with":
            print("Invalid arguments")
            return
        if len(parts) == 1:
            weapon, damage = "sword", 10
        else:
            weapons = {"sword": 10, "spear": 15, "axe": 20}
            weapon = parts[2]
            if weapon not in weapons:
                print("Unknown weapon")
                return
            damage = weapons[weapon]
        message = f"attack {name} {damage} {weapon}\n"
        self.soc.sendall(message.encode())

    def do_help(self, arg):
        """Показать справку."""
        self.soc.sendall(b"help\n")

    def do_quit(self, arg):
        """Выход из игры."""
        try:
            self.soc.sendall(b"quit\n")
        except OSError:
            pass
        self.running = False
        return True

    def do_EOF(self, arg):
        """Выход из игры (Ctrl-D)."""
        try:
            self.soc.sendall(b"quit\n")
        except OSError:
            pass
        self.running = False
        return True

    def do_movemonsters(self, arg):
        """movemonsters [on|off] — включить/выключить режим бродячих монстров."""
        if arg not in ("on", "off"):
            print("Usage: movemonsters [on|off]")
            return
        self.soc.sendall(f"movemonsters {arg}\n".encode())

    def complete_movemonsters(self, text, line, begidx, endidx):
        """Автодополнение для movemonsters."""
        opts = ["on", "off"]
        return [o for o in opts if o.startswith(text)]
 

    def complete_addmon(self, text, line, begidx, endidx):
        """Автодополнение для имени монстра."""
        words = (line[:endidx] + ".").split()
        d = []
        if len(words) > 2:
            if "hello" in words:
                words[words.index("hello") + 1] = "-"
            if "hp" not in words:
                d.append("hp")
            if "hello" not in words:
                d.append("hello")
            if "coords" not in words:
                d.append("coords")
        if len(words) == 2:
            d.extend(["jgsbat"] + cowsay.list_cows())
        return [c for c in d if c.startswith(text)]

    def complete_attack(self, text, line, begidx, endidx):
        """Автодополнение для атаки."""
        words = (line[:endidx] + ".").split()
        cows = ["jgsbat"] + cowsay.list_cows()
        weapons = ["sword", "spear", "axe"]
        if len(words) == 2 and words[-1][:-1] in cows:
            return [cows[(cows.index(words[-1][:-1]) + 1) % len(cows)]]
        if len(words) == 2:
            return [c for c in cows if c.startswith(text)]
        if len(words) == 3:
            return [w for w in ["with"] if w.startswith(text)]
        if len(words) == 4 and "with" in words:
            return [w for w in weapons if w.startswith(text)]
        return []

    def do_sayall(self, arg):
        """Чат между игроками."""
        message = f"sayall {arg}\n"
        self.soc.sendall(bytes(message.encode()))


def spam(cmdline, timeout):
    """Связь с сервером."""
    while cmdline.running:
        try:
            data = soc.recv(1024)
            if not data:
                break
            sys.stdout.write("\r\n")
            print(data.decode().rstrip())
            sys.stdout.write(cmdline.prompt)
            sys.stdout.flush()
        except (ConnectionResetError, OSError):
            break
        time.sleep(timeout)
    cmdline.running = False


def run_script_mode(filename, cmdline):
    """
    Читает файл строка за строкой, убирает номера и вызывает cmdline.onecmd().
    Между вызовами ждёт 1 сек, а при quit — выходит сразу.
    """

    with open(filename, encoding='utf-8') as f:
        for line in f:
            raw = line.strip()
            if not raw or raw.startswith('#'):
                continue
            cmd = re.sub(r'^\s*\d+\s+', '', raw)
            stop = cmdline.onecmd(cmd)
            if stop:
                return
            time.sleep(2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MUD client: interactive or script mode.")
    parser.add_argument('nickname', help='Your player nickname')
    parser.add_argument('--file', '-f', metavar='FILE', help='Script file with commands (.mood)')
    args = parser.parse_args()

    host = "localhost"
    port = 1337
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect((host, port))
    soc.sendall(f"{args.nickname}\n".encode())
    greeting = soc.recv(4096).decode().rstrip()
    print(greeting)
    if greeting == "User already registered":
        soc.close()
        sys.exit(1)

    cmdline = MUDclient(soc)
    reader = threading.Thread(target=spam, args=(cmdline, 0.1), daemon=True)
     
    reader.start()

    if args.file:
        run_script_mode(args.file, cmdline)
    else:
        cmdline.cmdloop()

    soc.close()

