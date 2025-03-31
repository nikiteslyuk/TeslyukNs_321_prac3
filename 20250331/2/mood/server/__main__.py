# mood/server/__main__.py
"""MUD server entrypoint: запускает asyncio-сервер для обработки клиентов."""

import asyncio
import cowsay
import shlex
from io import StringIO


class MUDServer:
    """MUD server."""

    clients = {}
    names = set()
    field = [[0 for _ in range(10)] for _ in range(10)]
    position = [0, 0]

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
                            ans = "Пользователь уже зарегистрирован"
                            print(f"Sended: {ans}")
                            writer.write(ans.encode())
                            break
                        me = message
                        self.clients[me] = queue
                        self.names.add(me)
                        ans = f"Добро пожаловать, {me}!"
                        print(f"Sended: {ans}")
                        writer.write(ans.encode())
                        await writer.drain()
                        for out in self.clients.values():
                            if out != me:
                                notice = f"{me} покдлючился"
                                print(f"Multisended: {notice}")
                                await out.put(notice)
                    elif message.startswith("move "):
                        _, x_str, y_str = shlex.split(message)
                        y, x = int(y_str), int(x_str)
                        self.position = [
                            (self.position[0] + x) % 10,
                            (self.position[1] + y) % 10,
                        ]
                        px, py = self.position
                        ans = f"Moved to {px} {py}"
                        if self.field[py][px]:
                            ans += "\nMoved to ...\n" + self.encounter(py, px)
                        print(f"Sended: {ans}")
                        writer.write(ans.encode())
                        await writer.drain()
                    elif message.startswith("addmon "):
                        _, name, hp_str, y_str, x_str, hello = (
                            shlex.split(message)
                        )
                        y, x = int(y_str), int(x_str)
                        ans = (
                            f"Added monster {name} to ({x}, {y}) "
                            f"saying {hello}"
                        )
                        if self.field[y][x]:
                            ans += "\nReplaced the old monster"
                        self.field[y][x] = [int(hp_str), name, hello]
                        print(f"Sended: {ans}")
                        writer.write(ans.encode())
                        await writer.drain()
                        broadcast = (
                            f"Monster {name} was added by"
                            f"player {me} at ({x},{y}) "
                            f"saying '{hello}'"
                        )
                        for out in self.clients.values():
                            if out != me:
                                print(f"Multisended: {broadcast}")
                                await out.put(broadcast)
                    elif message.startswith("attack "):
                        _, target_name, damage_str, weapon = (
                            shlex.split(message)
                        )
                        damage = int(damage_str)
                        px, py = self.position
                        cell = self.field[py][px]
                        if not cell or cell[1] != target_name:
                            ans = f"No {target_name} here"
                            print(f"Sended: {ans}")
                            writer.write(ans.encode())
                            await writer.drain()
                        else:
                            hp_old = cell[0]
                            hp_new = max(hp_old - damage, 0)
                            cell[0] = hp_new

                            if hp_new > 0:
                                ans = (
                                    f"Attacked {target_name} with {weapon},"
                                    f"now has {hp_new} hp"
                                )
                                broadcast = (
                                    f"Monster {target_name} was"
                                    f"attacked by player {me} "
                                    f"using {weapon} and has {hp_new} hp"
                                )
                            else:
                                ans = (
                                    f"Attacked {target_name} with {weapon},"
                                    f"{target_name} died"
                                )
                                self.field[py][px] = 0
                                broadcast = (
                                    f"Monster {target_name} was killed"
                                    f"by player {me} "
                                    f"using {weapon}"
                                )
                            print(f"Sended: {ans}")
                            writer.write(ans.encode())
                            await writer.drain()
                            for out in self.clients.values():
                                if out != me:
                                    print(f"Multisended: {broadcast}")
                                    await out.put(broadcast)
                    elif message.startswith("sayall "):
                        sayall, *msg = shlex.split(message)
                        ans = f"{me}: {msg[0]}"
                        for out in self.clients.values():
                            print('Multisended: ', ans)
                            await out.put(ans)
                    elif message == "quit":
                        ans = "До новых встреч!"
                        print(f"Sended: {ans}")
                        writer.write(ans.encode())
                        await writer.drain()
                        leave_notice = f"Пользователь {me} отключился"
                        for out in self.clients.values():
                            if out != me:
                                print(f"Multisended: {leave_notice}")
                                await out.put(leave_notice)
                        del self.clients[me]
                        self.names.remove(me)
                        me = None
                    elif message == "help":
                        ans = (
                            "Команды:\n"
                            "up/down/left/right — движение по фиелду\n"
                            "attack — атаковать монстра\n"
                            "addmon — добавить монстра\n"
                            "quit — выйти из игры"
                        )
                        print(f"Sended: {ans}")
                        writer.write(ans.encode())
                        await writer.drain()
                    else:
                        ans = "Неизвестная команда. Введите 'help'."
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
