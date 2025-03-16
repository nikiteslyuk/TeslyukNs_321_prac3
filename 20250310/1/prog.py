import cmd
import readline
import cowsay
import shlex
from io import StringIO

if "libedit" in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")


class MudGame(cmd.Cmd):
    prompt = ">> "

    def encounter(self, x, y):
        """Обработка встречи с монстром"""
        name, hello, hp = field[x][y]
        if name == "jgsbat":
            print(cowsay.cowsay(hello, cowfile=jgsbat_cow))
        else:
            print(cowsay.cowsay(hello, cow=name))

    def move_player(self, dx, dy):
        """Перемещение игрока и проверка на встречу с монстром"""
        player[0] = (player[0] + dx) % gridsize
        player[1] = (player[1] + dy) % gridsize

        if field[player[1]][player[0]]:
            print("moved to ...")
            self.encounter(player[1], player[0])
        else:
            print(f"moved to ({player[0]}, {player[1]})")

    def do_up(self, arg):
        self.move_player(0, 1)

    def do_right(self, arg):
        self.move_player(1, 0)

    def do_down(self, arg):
        self.move_player(0, -1)

    def do_left(self, arg):
        self.move_player(-1, 0)

    def do_EOF(self, arg):
        """Конец игры"""
        return True

    def do_exit(self, arg):
        """Конец игры"""
        return True

    def do_addmon(self, arg):
        """Добавление монстра
        Формат: addmon <name> <x> <y> <hp> <hello>
        """
        args = shlex.split(arg)
        if len(args) < 5:
            print("invalid command")
            return

        name, x, y, hp, hello = (
            args[0],
            int(args[1]),
            int(args[2]),
            int(args[3]),
            args[4],
        )

        if name != "jgsbat" and name not in cowsay.list_cows():
            print("unknown monster name")
            return

        if field[y][x]:
            print("replaced the old monster")

        field[y][x] = (name, hello, hp)
        print(f"added {name} at ({x},{y}) saying {hello}, HP: {hp}")

    def do_attack(self, arg):
        """
        Команда attack.
        Поддерживает:
          attack <monster_name>            # атака с оружием по умолчанию (sword)
          attack <monster_name> with <weapon>  # атака указанным оружием
        """
        args = shlex.split(arg)
        if not args:
            print("Invalid attack command")
            return

        if "with" in args:
            idx = args.index("with")
            monster_name = " ".join(args[:idx])
            if len(args) <= idx + 1:
                print("Weapon not specified")
                return
            weapon = args[idx + 1]
        else:
            monster_name = " ".join(args)
            weapon = "sword"

        if weapon not in weapon_damage:
            print("Unknown weapon")
            return

        x, y = player
        if not field[y][x] or field[y][x][0] != monster_name:
            print(f"no {monster_name} here")
            return

        name, hello, hp = field[y][x]
        damage = min(weapon_damage[weapon], hp)
        hp -= damage
        print(f"Attacked {name} with {weapon}, damage {damage} hp")
        if hp <= 0:
            print(f"{name} died")
            field[y][x] = ""
        else:
            field[y][x] = (name, hello, hp)
            print(f"{name} now has {hp} hp")

    def complete_attack(self, text, line, begidx, endidx):
        """
        Автодополнение для команды attack:
          - Если после "attack" не введено имя или оно частичное – возвращаются имена монстров.
          - Если имя монстра введено полностью, но после него не поставлен пробел, автодополнение
            возвращает кандидат, который включает имя монстра и автоматически добавляет " with ".
          - Если после имени введено "with" (или его начало), автодополняются имена оружия.
        """
        tokens = shlex.split(line)
        if line.endswith(" "):
            tokens.append("")

        cows = ["jgsbat"] + cowsay.list_cows()
        weapons = list(weapon_damage.keys())

        if len(tokens) == 1 or (len(tokens) == 2 and tokens[1] == ""):
            return [name for name in cows if name.startswith(text)]

        if len(tokens) == 2:
            if tokens[1] in cows:
                if not line.endswith(" "):
                    return [tokens[1] + " with "]
                else:
                    return ["with "]
            else:
                return [name for name in cows if name.startswith(text)]

        if len(tokens) == 3:
            if tokens[1] in cows:
                if tokens[2] == "":
                    return ["with "]
                else:
                    return [kw for kw in ["with"] if kw.startswith(text)]
            else:
                return []

        if len(tokens) >= 4:
            return [w for w in weapons if w.startswith(text)]

        return []


if __name__ == "__main__":
    jgsbat = r"""
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

    jgsbat_cow = cowsay.read_dot_cow(StringIO(jgsbat))

    gridsize = 10
    field = [["" for _ in range(gridsize)] for _ in range(gridsize)]
    player = [0, 0]
    weapon_damage = {"sword": 10, "spear": 15, "axe": 20}

    print("<<< Welcome to Python-MUD 0.1 >>>")
    MudGame().cmdloop()
