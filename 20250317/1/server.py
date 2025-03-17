import asyncio


class MUDServer:
    field = [[None for _ in range(10)] for _ in range(10)]
    position = [0, 0]

    async def process(self):
        server = await asyncio.start_server(self.handle_connection, "0.0.0.0", 1337)
        async with server:
            await server.serve_forever()

    async def handle_connection(self, reader, writer):
        print("New player connected")
        while data := await reader.readline():
            data = data.decode()[:-1]
            print(f"Received: {data}")
            if data.startswith("move "):
                data = data.split()
                x, y = map(int, [data[1], data[2]])
                self.position = x, y
                if self.field[y][x]:
                    hp, name, message = self.field[y][x]
                    data = f"{name} {message}"
                else:
                    data = "nothing"
                print(f"Received: {data}")
                writer.write(bytes(data.encode()))
            elif data == "position":
                data = f"{self.position[0]} {self.position[1]}"
                print(f"Received: {data}")
                writer.write(bytes(data.encode()))
            elif data.startswith("add "):
                add, name, hp, y, x, *message = data.split()
                added = 0
                y, x, hp = map(int, [y, x, hp])
                if self.field[y][x]:
                    added = 1
                self.field[y][x] = hp, name, " ".join(message)
                data = f"{added}"
                print(f"Received: {data}")
                writer.write(bytes(data.encode()))
            else:
                print("Unknown command", data)
        print("Player disconnected")
        writer.close()
        await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(MUDServer().process())
