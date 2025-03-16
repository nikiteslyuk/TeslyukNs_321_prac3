import cowsay
import cmd
from io import StringIO
import shlex
import readline

dungeon = [[0 for i in range(10)] for j in range(10)]


def encounter(y, x):
    jgsbat = cowsay.read_dot_cow(
        StringIO(
            """    ,_                    _,
    ) '-._  ,_    _,  _.-' (
    )  _.-'.|\\ \b\\--//|.'-._  (
     )'   .'\\/o\\/o\\/'.   `(
      ) .' . \\====/ . '. (
       )  / <<    >> \\  (
        '-._/``  ``\\_.-'
  jgs     __\\ \b\\'--'//__
         (((""`  `"")))"""
        )
    )
    hp, name, message = dungeon[y][x]
    if name == "jgsbat":
        print(cowsay.cowsay(message, cowfile=jgsbat))
    else:
        print(cowsay.cowsay(message, cow=name))


class MUD(cmd.Cmd):
    print("<<< Welcome to Python-MUD 0.1 >>>")
    prompt = ">>> "
    pos = [0, 0]

    def do_up(self, arg):
        """moves character up"""
        self.pos[1] = (self.pos[1] + 1) % 10
        pos = self.pos
        print(f"Moved to ({pos[0]}, {pos[1]})")
        if dungeon[pos[1]][pos[0]]:
            print(f"Moved to ...")
            encounter(pos[1], pos[0])

    def do_down(self, arg):
        """moves character down"""
        self.pos[1] = (self.pos[1] - 1) % 10
        pos = self.pos
        print(f"Moved to ({pos[0]}, {pos[1]})")
        if dungeon[pos[1]][pos[0]]:
            print(f"Moved to ...")
            encounter(pos[1], pos[0])

    def do_left(self, arg):
        """moves character left"""
        self.pos[0] = (self.pos[0] - 1) % 10
        pos = self.pos
        print(f"Moved to ({pos[0]}, {pos[1]})")
        if dungeon[pos[1]][pos[0]]:
            print(f"Moved to ...")
            encounter(pos[1], pos[0])

    def do_right(self, arg):
        """moves character right"""
        self.pos[0] = (self.pos[0] + 1) % 10
        pos = self.pos
        print(f"Moved to ({pos[0]}, {pos[1]})")
        if dungeon[pos[1]][pos[0]]:
            print(f"Moved to ...")
            encounter(pos[1], pos[0])

    def do_attack(self, arg):
        """attack <имя монстра> with <имя оружия>"""
        arg = arg.split()
        if len(arg) < 1 or len(arg) == 2:
            print("Invalid arguments")
            return
        name = arg[0]
        if len(arg) > 1 and arg[1] != "with":
            print("Invalid arguments")
            return
        if len(arg) == 1:
            ww = "sword"
            damage = 10
        else:
            weapons = ["sword", "spear", "axe"]
            if arg[2] in weapons:
                ww = arg[2]
            else:
                print("Unknown weapon")
                return
        if ww == "spear":
            damage = 15
        elif ww == "axe":
            damage = 20
        pos = self.pos
        if not dungeon[pos[1]][pos[0]] or dungeon[pos[1]][pos[0]][1] != name:
            print(f"No", name, "here")
        else:
            hp, name, _ = dungeon[pos[1]][pos[0]]
            print(f"Attacked {name}, damage {damage} hp")
            hp = max(hp - damage, 0)
            dungeon[pos[1]][pos[0]][0] = hp
            if hp:
                print(name, "now has", hp)
            else:
                print(name, "died")
                dungeon[pos[1]][pos[0]] = 0

    def do_addmon(self, arg):
        """addmon <monster_name> hello <hello_string> hp <hitpoints> coords <x> <y>"""
        err_parse = True
        name, *pars = shlex.split(arg)
        if len(pars) == 7:
            i = pars.index("hello")
            if -1 < i < 6:
                hello = pars[i + 1]
                pars[i + 1] = "-"
                i = pars.index("hp")
                if -1 < i < 6:
                    hp = pars[i + 1]
                    if hp.isdigit():
                        hp = int(hp)
                        if hp > 0:
                            i = pars.index("coords")
                            if -1 < i < 5:
                                x, y = pars[i + 1], pars[i + 2]
                                if x.isdigit() and y.isdigit():
                                    y, x = int(y), int(x)
                                    if name in cowsay.list_cows() + ["jgsbat"]:
                                        err_parse = False
                                        print(
                                            f"Added monster {name} to ({x}, {y}) saying {hello}"
                                        )
                                        if dungeon[y][x]:
                                            print("Replaced the old monster")
                                        dungeon[y][x] = [hp, name, hello]
        if err_parse:
            print("Invalid arguments")

    def do_EOF(self, arg):
        """End Of File AKA exit game"""
        return 1

    def complete_attack(self, text, line, begidx, endidx):
        words = (line[:endidx] + ".").split()
        DICT = []
        cows = ["jgsbat"] + cowsay.list_cows()
        weapons = ["sword", "spear", "axe"]
        if len(words) == 2 and words[-1][:-1] in cows:
            return [cows[(cows.index(words[-1][:-1]) + 1) % len(cows)]]
        elif len(words) == 2:
            DICT = cows
        elif len(words) == 3:
            DICT = ["with"]
        elif len(words) == 4 and words[-1][:-1] in weapons:
            return [weapons[(weapons.index(words[-1][:-1]) + 1) % len(weapons)]]
        elif len(words) == 4 and "with" in words:
            DICT = weapons
        return [c for c in DICT if c.startswith(text)]

    def complete_addmon(self, text, line, begidx, endidx):
        words = (line[:endidx] + ".").split()
        DICT = []
        if len(words) > 2:
            if "hello" in words:
                words[words.index("hello") + 1] = "-"
            if "hp" not in words:
                DICT.append("hp")
            if "hello" not in words:
                DICT.append("hello")
            if "coords" not in words:
                DICT.append("coords")
        if len(words) == 2:
            DICT.extend(["jgsbat"] + cowsay.list_cows())
        return [c for c in DICT if c.startswith(text)]


if __name__ == "__main__":
    MUD().cmdloop()
