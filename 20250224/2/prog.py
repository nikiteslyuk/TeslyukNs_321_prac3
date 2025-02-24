import cowsay


def encounter(x, y):
    name, hello = field[x][y]
    print(cowsay.cowsay(hello, cow=name))


gridsize = 10
field = [["" for _ in range(gridsize)] for _ in range(gridsize)]
player = [0, 0]


while command := input(">> "):
    comm = command.split()
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
        case ["addmon", x, y, name, hello]:
            if not x.isdigit() or not y.isdigit() or name not in cowsay.list_cows():
                print("Invalid arguments")
                continue
            crds = [int(x), int(y)]
            print(f"Added monster {name} to ({crds[0]}, {crds[1]}) saying {hello}")
            if field[crds[1]][crds[0]]:
                print("Replaced the old monster")
            field[crds[1]][crds[0]] = name, hello
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
