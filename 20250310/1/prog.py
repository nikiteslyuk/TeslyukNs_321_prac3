import cmd
import cowsay
import shlex
from io import StringIO


class MudGame(cmd.Cmd):
    prompt = ">> "

    def encounter(self, x, y):
        """обработка встречи с монстром"""
        name, hello, hp = field[x][y]
        if name == "jgsbat":
            print(cowsay.cowsay(hello, cowfile=jgsbat_cow))
        else:
            print(cowsay.cowsay(hello, cow=name))

    def move_player(self, dx, dy):
        """перемещение игрока и проверка на встречу с монстром"""
        player[0] = (player[0] + dx) % gridsize
        player[1] = (player[1] + dy) % gridsize

        if field[player[1]][player[0]]:
            print("moved to ...")
            self.encounter(player[1], player[0])
        else:
            print(f"moved to ({player[0]}, {player[1]})")

    def do_up(self, arg):
        """move up"""
        self.move_player(0, 1)

    def do_right(self, arg):
        """move right"""
        self.move_player(1, 0)

    def do_down(self, arg):
        """move down"""
        self.move_player(0, -1)

    def do_left(self, arg):
        """move left"""
        self.move_player(-1, 0)

    def do_addmon(self, arg):
        """add monster"""
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
        """атака монстра по имени"""
        args = shlex.split(arg)
        if len(args) != 1:
            print("invalid attack command")
            return

        monster_name = args[0]
        x, y = player
        if not field[y][x] or field[y][x][0] != monster_name:
            print(f"no {monster_name} here")
            return

        name, hello, hp = field[y][x]
        damage = min(10, hp)
        hp -= damage
        print(f"attacked {name}, damage {damage} hp")

        if hp <= 0:
            print(f"{name} died")
            field[y][x] = ""
        else:
            field[y][x] = (name, hello, hp)
            print(f"{name} now has {hp} hp")

    def complete_attack(self, text, line, begidx, endidx):
        """Автодополнение имен монстров с циклическим пролистыванием"""
        tokens = line.split()
        cows = ["jgsbat"] + cowsay.list_cows()

        if len(tokens) <= 1 or text == "":
            return cows

        if text in cows:
            idx = cows.index(text)
            next_idx = (idx + 1) % len(cows)
            return [cows[next_idx]]

        return [name for name in cows if name.startswith(text)]


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

    print("<<< Welcome to Python-MUD 0.1 >>>")
    MudGame().cmdloop()
