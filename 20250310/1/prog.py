import cmd
import cowsay
import shlex
from io import StringIO


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
        """Move up"""
        self.move_player(0, 1)

    def do_right(self, arg):
        """Move right"""
        self.move_player(1, 0)

    def do_down(self, arg):
        """Move down"""
        self.move_player(0, -1)

    def do_left(self, arg):
        """Move left"""
        self.move_player(-1, 0)

    def do_addmon(self, arg):
        """Add monster"""
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
        """Attack the monster in the same position"""
        x, y = player
        if not field[y][x]:
            print("No monster here")
            return

        name, hello, hp = field[y][x]
        damage = min(10, hp)
        hp -= damage
        print(f"Attacked {name}, damage {damage} hp")

        if hp <= 0:
            print(f"{name} died")
            field[y][x] = ""
        else:
            field[y][x] = (name, hello, hp)
            print(f"{name} now has {hp} hp")


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
