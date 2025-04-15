# mood/server/__main__.py
"""
MUD Server module.

Здесь описано:
- запуск asyncio-сервера,
- команды move/addmon/attack/sayall/quit,
- бродячие монстры (_roam_monsters).
"""

import asyncio
import cowsay
import shlex
from io import StringIO
import random, asyncio
import gettext
import locale
import os


locales_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locales")
LOCALES = {
    "en_US": gettext.translation("MOOD", locales_dir, ["en"], fallback=True),
    "ru_RU": gettext.translation("MOOD", locales_dir, ["ru"], fallback=True),
}


class MUDServer:
    """
    Класс MUDServer — основной сервер.

    Attributes:
        clients (Dict[str, asyncio.Queue]): очереди сообщений клиентов.
        names (Set[str]): имена подключенных игроков.
        positions (Dict[str, Tuple[int,int]]): их координаты.
        field (List[List[Union[int,list]]]): игровое поле 10×10.
    """


    def __init__(self):
        locale.setlocale(locale.LC_ALL, '')
        self.client_locales = {}
        self.clients = {}
        self.names = set()
        self.positions = {}
        self.field = [[0]*10 for _ in range(10)]
        self.roaming_enabled = True
        self.locales_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locales")
        self.LOCALES = LOCALES
        asyncio.create_task(self._roam_monsters())

    def _(self, text, locale):
        """Локализация."""
        return self.LOCALES[locale].gettext(text)

    def ngettext(self, text, ntext, n, locale):
        """Локализация, множественное число."""
        return self.LOCALES[locale].ngettext(text, ntext, n)

    def encounter(self, y, x):
        """Встреча с монстром."""
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
        hp, name, message = self.field[y][x]
        if name == "jgsbat":
            return cowsay.cowsay(message, cowfile=jgsbat)
        else:
            return cowsay.cowsay(message, cow=name)



    async def _roam_monsters(self):
        """Каждые 30 сек выбираем рандомного монстра и двигаем."""
        dirs = {
            "up":    (1, 0),
            "down":  (-1,0),
            "right":(0, 1),
            "left": (0,-1),
        }
        while True:
            await asyncio.sleep(30)
            if not self.roaming_enabled:
                continue
            mons = [(y,x, self.field[y][x]) 
                    for y in range(10) for x in range(10) 
                    if self.field[y][x]]
            if not mons:
                continue
            while True:
                y, x, cell = random.choice(mons)
                name = cell[1]
                direction, (dy,dx) = random.choice(list(dirs.items()))
                ny = (y+dy) % 10
                nx = (x+dx) % 10
                if self.field[ny][nx]:
                    continue
                self.field[ny][nx] = cell
                self.field[y][x] = 0
                break
            for other, q in self.clients.items():
                loc = self.client_locales.get(other, "en_US")
                roaming_msg = self._("{} moved one cell {}", loc).format(name, direction)
                print(f"Multisended: {roaming_msg}")
                await q.put(roaming_msg)
            for player, pos in self.positions.items():
                if pos == (ny,nx):
                    text = self.encounter(ny, nx)
                    await self.clients[player].put(text)

    async def server(self, reader, writer):
        """Асинхронный сервер."""
        me = None
        queue = asyncio.Queue()
        send_task = asyncio.create_task(reader.readline())
        recv_task = asyncio.create_task(queue.get())

        while not reader.at_eof():
            done, _ = await asyncio.wait(
                [send_task, recv_task], return_when=asyncio.FIRST_COMPLETED
            )

            for task in done:
                if task is send_task:
                    send_task = asyncio.create_task(reader.readline())
                    message = task.result().decode().strip()
                    print(f"Received: {message}")
                    if not message:
                        continue
                    if not me:
                        if message in self.names:
                            loc = "en_US"
                            ans = self._("User already registered", loc)
                            print(f"Sended: {ans}")
                            writer.write(ans.encode())
                            break
                        me = message
                        self.client_locales[me] = "en_US"
                        self.clients[me] = queue
                        self.names.add(me)
                        self.positions[me] = (0, 0)
                        loc = self.client_locales[me]
                        ans = self._("Welcome, {}!", loc).format(me)
                        print(f"Sended: {ans}")
                        writer.write(ans.encode())
                        await writer.drain()
                        for other, q in self.clients.items():
                            if other == me:
                                continue
                            loc = self.client_locales[other]
                            notice = self._("{} has connected", loc).format(me)
                            print(f"Multisended: {notice}")
                            await q.put(notice)
                    elif message.startswith("move "):
                        _, dx_str, dy_str = shlex.split(message)
                        dx, dy = int(dx_str), int(dy_str)
                        old_x, old_y = self.positions.get(me, (0, 0))
                        new_x = (old_x + dx) % 10
                        new_y = (old_y + dy) % 10
                        self.positions[me] = (new_x, new_y)
                        loc = self.client_locales[me]
                        ans = self._("Moved to {} {}", loc).format(new_x, new_y)
                        if self.field[new_y][new_x]:
                            ans += "\n" + self.encounter(new_y, new_x)
                        print(f"Sended: {ans}")
                        writer.write(ans.encode())
                        await writer.drain()
                    elif message.startswith("addmon "):
                        _, name, hp_str, y_str, x_str, hello = (
                            shlex.split(message)
                        )
                        y, x = int(y_str), int(x_str)
                        loc = self.client_locales[me]
                        ans = self._(
                            "Added monster {} to ({}, {}) saying {}. ",
                            loc,
                        ).format(name, x, y, hello)
                        if self.field[y][x]:
                            loc = self.client_locales[me]
                            ans += self._("Replaced the old monster", loc)
                        self.field[y][x] = [int(hp_str), name, hello]
                        print(f"Sended: {ans}")
                        writer.write(ans.encode())
                        await writer.drain()
                        for other, q in self.clients.items():
                            if other == me:
                                continue
                            loc = self.client_locales[other]
                            msg = self._(
                                "Monster {} was added by player {} at ({},{}) saying '{}'",
                                loc
                            ).format(name, me, x, y, hello)
                            print(f"Multisended: {msg}")
                            await q.put(msg)
                    elif message.startswith("attack "):
                        _, target_name, damage_str, weapon = (
                            shlex.split(message)
                        )
                        damage = int(damage_str)
                        x, y = self.positions.get(me, (0, 0))
                        cell = self.field[y][x]
                        if not cell or cell[1] != target_name:
                            loc = self.client_locales[me]
                            ans = self._("No {} here", loc).format(target_name)
                            print(f"Sended: {ans}")
                            writer.write(ans.encode())
                            await writer.drain()
                        else:
                            hp_old = cell[0]
                            hp_new = max(hp_old - damage, 0)
                            cell[0] = hp_new

                            if hp_new > 0:
                                loc = self.client_locales[me]
                                ans = self.ngettext(
                                    "Attacked {} with {}, damage {} hitpoint",
                                    "Attacked {} with {}, damage {} hitpoints",
                                    damage,
                                    loc,
                                ).format(target_name, weapon, damage)
                            else:
                                loc = self.client_locales[me]
                                ans = self._(
                                    "Attacked {} with {}, {} died",
                                    loc,
                                ).format(target_name, weapon, target_name)
                                self.field[y][x] = 0

                            print(f"Sended: {ans}")
                            writer.write(ans.encode())
                            await writer.drain()

                            for other, q in self.clients.items():
                                if other == me:
                                    continue
                                loc_other = self.client_locales[other]
                                if hp_new > 0:
                                    msg = self._(
                                        "Monster {} was attacked by player {} using {} and has {} hp",
                                        loc_other
                                    ).format(target_name, me, weapon, hp_new)
                                else:
                                    msg = self._(
                                        "Monster {} was killed by player {} using {}",
                                        loc_other
                                    ).format(target_name, me, weapon)
                                print(f"Multisended: {msg}")
                                await q.put(msg)
                    elif message.startswith("sayall "):
                        sayall, *msg = shlex.split(message)
                        ans = f"{me}: {msg[0]}"
                        for out in self.clients.values():
                            print('Multisended: ', ans)
                            await out.put(ans)
                    elif message == "quit":
                        loc = self.client_locales[me]
                        ans = self._("Goodbye!", loc)
                        print(f"Sended: {ans}")
                        writer.write(ans.encode())
                        await writer.drain()
                        for other, q in self.clients.items():
                            if other == me:
                                continue
                            loc = self.client_locales[other]
                            notice = self._("User {} disconnected", loc).format(me)
                            print(f"Multisended: {notice}")
                            await q.put(notice)
                        del self.clients[me]
                        self.names.remove(me)
                        me = None
                    elif message == "help":
                        loc = self.client_locales[me]
                        ans = self._(
                            "Commands:\nup/down/left/right — move\nattack — attack a monster\naddmon — add a monster\nquit — quit the game",
                            loc,
                        )
                        print(f"Sended: {ans}")
                        writer.write(ans.encode())
                        await writer.drain()
                    elif message.startswith("movemonsters"):
                        parts = shlex.split(message)
                        loc_self = self.client_locales[me]
                        if len(parts) == 2 and parts[1] in ("on", "off"):
                            self.roaming_enabled = (parts[1] == "on")
                            ans = self._("Moving monsters: {}", loc_self).format(parts[1])
                        else:
                            ans = self._("Usage: movemonsters [on|off]", loc_self)
                        print(f"Sended: {ans}")
                        writer.write(ans.encode())
                        await writer.drain()
                        for other, q in self.clients.items():
                            if other == me:
                                continue
                            loc_other = self.client_locales[other]
                            msg = self._("Moving monsters: {}", loc_other).format(parts[1])
                            print(f"Multisended: {msg}")
                            await q.put(msg)

                    elif message.startswith("locale"):
                        parts = shlex.split(message)
                        loc = parts[1]
                        if loc in LOCALES:
                            self.client_locales[me] = loc
                            ans = self._("Set up locale: {}", loc).format(loc)
                        else:
                            ans = "Unsupported locale"
                        print(f"Sended: {ans}")
                        writer.write(ans.encode())
                        await writer.drain()
                    else:
                        loc = self.client_locales[me]
                        ans = self._("Unknown command. Type 'help'.", loc)
                        print(f"Sended: {ans}")
                        writer.write(ans.encode())
                        await writer.drain()
                elif task is recv_task:
                    recv_task = asyncio.create_task(queue.get())
                    notice = task.result()
                    writer.write(f"{notice}\n".encode())
                    await writer.drain()
        send_task.cancel()
        recv_task.cancel()
        if me:
            del self.clients[me]
            self.names.remove(me)
        writer.close()
        await writer.wait_closed()


async def process():
    """Главный цикл сервера."""
    m = MUDServer()
    server = await asyncio.start_server(m.server, "0.0.0.0", 1337)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(process())
