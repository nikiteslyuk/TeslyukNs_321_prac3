# mood/client/__main__.py
"""MUD client entrypoint: запускает клиента."""

import cmd
import cowsay
import shlex
import sys
import socket
import threading
import time


class MUDclient(cmd.Cmd):
    """Реализация клиента."""

    prompt = ">> "
    running = True

    def do_up(self, arg):
        """Ход вверх."""
        soc.sendall(b"move 0 1\n")

    def do_down(self, arg):
        """Ход вниз."""
        soc.sendall(b"move 0 -1\n")

    def do_left(self, arg):
        """Ход влево."""
        soc.sendall(b"move -1 0\n")

    def do_right(self, arg):
        """Ход вправо."""
        soc.sendall(b"move 1 0\n")

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
        soc.sendall(message.encode())

    def do_attack(self, arg):
        """Attack <имя монстра> with <имя оружия>."""
        parts = arg.split()
        if len(parts) < 1 or len(parts) == 2:
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
        soc.sendall(message.encode())

    def do_help(self, arg):
        """Показать справку."""
        soc.sendall(b"help\n")

    def do_quit(self, arg):
        """Выход из игры."""
        soc.sendall(b"quit\n")
        self.running = False
        return True

    def do_EOF(self, arg):
        """Выход из игры (Ctrl-D)."""
        soc.sendall(b"quit\n")
        self.running = False
        return True

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
        soc.sendall(bytes(message.encode()))


def spam(cmdline, timeout):
    """Связь с сервером."""
    while cmdline.running:
        try:
            data = soc.recv(1024)
            if not data:
                print("\nDisconnected from server.")
                break
            sys.stdout.write("\r\n")
            print(data.decode().rstrip())
            sys.stdout.write(cmdline.prompt)
            sys.stdout.flush()
        except ConnectionResetError:
            print("\nConnection closed by server.")
            break
        time.sleep(timeout)
    cmdline.running = False


if __name__ == "__main__":
    host = "localhost"
    port = 1337
    if len(sys.argv) < 2:
        print("Usage: python3 client.py",
              "<nickname>\nУкажите никнейм")
    else:
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.connect((host, port))
        soc.sendall(f"{sys.argv[1]}\n".encode())
        data = soc.recv(4096)
        print(data.decode().rstrip())
        if data.decode().rstrip() != "Пользователь уже зарегистрирован":
            cmdline = MUDclient()
            timer = threading.Thread(target=spam,
                                     args=(cmdline, 0.1), daemon=True)
            timer.start()
            cmdline.cmdloop()
        soc.close()
