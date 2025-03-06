import cowsay
import shlex
from io import StringIO


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

print("<<< Welcome to Python-MUD 0.1 >>>")


def encounter(x, y):
    name, hello, hp = field[x][y]
    if name == "jgsbat":
        print(cowsay.cowsay(hello, cowfile=jgsbat_cow))
    else:
        print(cowsay.cowsay(hello, cow=name))


gridsize = 10
field = [["" for _ in range(gridsize)] for _ in range(gridsize)]
player = [0, 0]


while command := input(">> "):
    comm = shlex.split(command)
    stay = False
    match comm:
        case ["up"]:
            player[1] += 1
            player[1] %= gridsize
            print(f"Moved to ({player[0]}, {player[1]})")
        case ["right"]:
            player[0] += 1
            player[0] %= gridsize
            print(f"Moved to ({player[0]}, {player[1]})")
        case ["down"]:
            player[1] -= 1
            player[1] %= gridsize
            print(f"Moved to ({player[0]}, {player[1]})")
        case ["left"]:
            player[0] -= 1
            player[0] %= gridsize
            print(f"Moved to ({player[0]}, {player[1]})")
        case ["addmon", name, *args]:

            try:
                parsed = {}
                i = 0
                while i < len(args):
                    key = args[i]
                    if key == "coords":
                        parsed[key] = (int(args[i + 1]), int(args[i + 2]))
                        i += 3
                    else:
                        parsed[key] = args[i + 1]
                        i += 2
            except (IndexError, ValueError):
                print("Invalid command")
                continue

            if not all(k in parsed for k in ("coords", "hp", "hello")):
                print("Missing required parameters")
                continue

            x, y = parsed["coords"]
            hp = int(parsed["hp"])
            hello = parsed["hello"]

            if name not in cowsay.list_cows():
                print("Unknown monster name")
                continue

            if field[y][x]:
                print("Replaced the old monster")

            field[y][x] = name, hello, hp
            print(f"Added {name} at ({x},{y}) saying {hello}, HP: {hp}")

            stay = True
        case _:
            print("Invalid command")
            stay = True
    if stay:
        continue
    if field[player[1]][player[0]]:
        print("Moved to ...")
        encounter(player[1], player[0])
    pass
