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
            print("Moved to ...")
            self.encounter(player[1], player[0])
        else:
            print(f"Moved to ({player[0]}, {player[1]})")

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
        return 1

    def do_addmon(self, arg):
        """Добавление монстра"""
        args = shlex.split(arg)
        if len(args) < 5:
            print("Invalid command")
            return

        name, x, y, hp, hello = (
            args[0],
            int(args[1]),
            int(args[2]),
            int(args[3]),
            args[4],
        )

        if name != "jgsbat" and name not in cowsay.list_cows():
            print("Unknown monster name")
            return

        if field[y][x]:
            print("Replaced the old monster")

        field[y][x] = (name, hello, hp)
        print(f"Added {name} at ({x},{y}) saying {hello}, HP: {hp}")

    def do_attack(self, arg):
        """Атаковать монстра оружием"""
        args = shlex.split(arg)

        if len(args) == 0:
            weapon = "sword"
        elif len(args) == 2 and args[0] == "with":
            weapon = args[1]
        else:
            print("Invalid attack command")
            return

        if weapon not in weapon_damage:
            print("Unknown weapon")
            return

        x, y = player
        if not field[y][x]:
            print("No monster here")
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
        """Автодополнение имен доступного в игре оружия"""
        return [w for w in weapon_damage.keys() if w.startswith(text)]


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
