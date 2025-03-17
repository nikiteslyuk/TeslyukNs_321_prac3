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
            ans, *tail = ans.split()
            self.encounter(ans, ' '.join(tail), position[1], position[0])

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
            ans, *tail = ans.split()
            self.encounter(ans, ' '.join(tail), position[1], position[0])

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
            ans, *tail = ans.split()
            self.encounter(ans, ' '.join(tail), position[1], position[0])

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
            ans, *tail = ans.split()
            self.encounter(ans, ' '.join(tail), position[1], position[0])

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
        
    def do_addmon(self, arg):
        """
        Добавление монстра. Синтаксис команды:
            addmon <monster_name> hello <hello_string> hp <hitpoints> coords <x> <y>
        """
        if len(arg.split()) < 2:
            print("Invalid arguments")
            return

        name, *parsed = shlex.split(arg)
        if len(parsed) != 7:
            print("Invalid arguments")
            return

        i = parsed.index("hello") if "hello" in parsed else -1
        if i == -1 or not (0 <= i < 6):
            print("Invalid arguments")
            return
        hello = parsed[i + 1]
        parsed[i + 1] = "-"

        i = parsed.index("hp") if "hp" in parsed else -1
        if i == -1 or not (0 <= i < 6):
            print("Invalid arguments")
            return
        hp = parsed[i + 1]
        if not hp.isdigit() or int(hp) <= 0:
            print("Invalid arguments")
            return
        hp = int(hp)

        i = parsed.index("coords") if "coords" in parsed else -1
        if i == -1 or not (0 <= i < 5):
            print("Invalid arguments")
            return
        x, y = parsed[i + 1], parsed[i + 2]
        if not (x.isdigit() and y.isdigit()):
            print("Invalid arguments")
            return
        x, y = int(x), int(y)

        if name not in cowsay.list_cows() + ["jgsbat"]:
            print("Invalid arguments")
            return

        print(f"Added monster {name} to ({x}, {y}) saying {hello}")
        message = f"add {name} {hp} {y} {x} {hello}\n"
        soc.sendall(bytes(message.encode()))
        ans = soc.recv(1024).rstrip().decode()
        if int(ans):
            print("Replaced the old monster")
        
        
    def do_attack(self, arg):
        """
        Атака монстра. Синтаксис команды:
            attack <имя монстра> with <имя оружия>
        """
        arg = arg.split()
        if len(arg) < 1 or len(arg) == 2:
            print("Invalid arguments")
            return
        name = arg[0]
        if len(arg) > 1 and arg[1] != 'with':
            print("Invalid arguments")
            return
        if len(arg) == 1:
            ww = 'sword'
            damage = 10
        else:
            weapons = ['sword', 'spear', 'axe']
            if arg[2] in weapons:
                ww = arg[2]
            else:
                print("Unknown weapon")
                return
        if ww == 'sword':
            damage = 10
        elif ww == 'spear':
            damage = 15
        elif ww == 'axe':
            damage = 20
        message = f"attack {name} {damage}\n"
        soc.sendall(bytes(message.encode()))
        ans = soc.recv(1024).rstrip().decode()
        if ans == 'nothing':
            print(f"No", name, "here")
        else:
            damage, new_hp = map(int, ans.split())
            print(f"Attacked {name}, damage {damage} hp")
            if new_hp:
                print(name,"now has", new_hp)
            else:
                print(name, "died")


if __name__ == "__main__":
    host = "localhost" if len(sys.argv) < 2 else sys.argv[1]
    port = 1337 if len(sys.argv) < 3 else int(sys.argv[2])
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect((host, port))
    MUDClient().cmdloop()
