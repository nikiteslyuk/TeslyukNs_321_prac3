import cmd
import readline
import cowsay
import shlex
from io import StringIO
import sys
import socket


class MUDClient(cmd.Cmd):
    print("<<< Welcome to Python-MUD 0.1 >>>")
    prompt = ">> "

    def encounter(self, name, message, y, x):
        """Встреча с монстром"""
        jgsbat_paint = r"""
            ,_                    _,
            ) '-._  ,_    _,  _.-' (
            )  _.-'.|\\--//|.'-._  (
             )'   .'\/o\/o\/'.   `(
              ) .' . \====/ . '. (
               )  / <<    >> \  (
                '-._/``  ``\_.-'
          jgs     __\\'--'//__
                 (((""`  `"")))
        """
        jgsbat = cowsay.read_dot_cow(StringIO(jgsbat_paint))
        if name == "jgsbat":
            print(cowsay.cowsay(message, cowfile=jgsbat))
        else:
            print(cowsay.cowsay(message, cow=name))

    def do_up(self, arg):
        """Ход вверх"""
        position = self.position()
        position[1] = (position[1] + 1) % 10
        print(f"Moved to ({position[0]}, {position[1]})")
        message = f"move {position[0]} {position[1]}\n"
        soc.sendall(bytes(message.encode()))
        ans = soc.recv(1024).rstrip().decode()
        if ans != "nothing":
            print(f"Moved to ...")
            ans = ans.split()
            self.encounter(ans[0], ans[1], position[1], position[0])

    def do_down(self, arg):
        """Ход вниз"""
        position= self.position()
        position[1] = (position[1] - 1) % 10
        print(f"Moved to ({position[0]}, {position[1]})")
        message = f"move {position[0]} {position[1]}\n"
        soc.sendall(bytes(message.encode()))
        ans = soc.recv(1024).rstrip().decode()
        if ans != "nothing":
            print(f"Moved to ...")
            ans = ans.split()
            self.encounter(ans[0], ans[1], position[1], position[0])

    def do_left(self, arg):
        """Ход налево"""
        position= self.position()
        position[0] = (position[0] - 1) % 10
        print(f"Moved to ({position[0]}, {position[1]})")
        message = f"move {position[0]} {position[1]}\n"
        soc.sendall(bytes(message.encode()))
        ans = soc.recv(1024).rstrip().decode()
        if ans != "nothing":
            print(f"Moved to ...")
            ans = ans.split()
            self.encounter(ans[0], ans[1], position[1], position[0])

    def do_right(self, arg):
        """Ход направо"""
        position= self.position()
        position[0] = (position[0] + 1) % 10
        print(f"Moved to ({position[0]}, {position[1]})")
        message = f"move {position[0]} {position[1]}\n"
        soc.sendall(bytes(message.encode()))
        ans = soc.recv(1024).rstrip().decode()
        if ans != "nothing":
            print(f"Moved to ...")
            ans = ans.split()
            self.encounter(ans[0], ans[1], position[1], position[0])

    def do_EOF(self, arg):
        """Выход из игры"""
        return 1

    def complete_addmon(self, text, line, begidx, endidx):
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
        """Атака"""
        words = (line[:endidx] + ".").split()
        d = []
        cows = ["jgsbat"] + cowsay.list_cows()
        weapons = ["sword", "spear", "axe"]
        if len(words) == 2 and words[-1][:-1] in cows:
            return [cows[(cows.index(words[-1][:-1]) + 1) % len(cows)]]
        elif len(words) == 2:
            d = cows
        elif len(words) == 3:
            d = ["with"]
        elif len(words) == 4 and words[-1][:-1] in weapons:
            return [weapons[(weapons.index(words[-1][:-1]) + 1) % len(weapons)]]
        elif len(words) == 4 and "with" in words:
            d = weapons
        return [c for c in d if c.startswith(text)]

    def position(self):
        message = f"position\n"
        soc.sendall(bytes(message.encode()))
        ans = soc.recv(1024).rstrip().decode()
        return [int(i) for i in ans.split()]


if __name__ == "__main__":
    host = "localhost" if len(sys.argv) < 2 else sys.argv[1]
    port = 1337 if len(sys.argv) < 3 else int(sys.argv[2])
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect((host, port))
    MUDClient().cmdloop()
