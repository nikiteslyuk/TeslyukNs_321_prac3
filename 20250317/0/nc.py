import sys
import readline
import cmd
import socket


class CmdNetCat(cmd.Cmd):
    promt = "cmdnetcat>>> "

    def __init__(self, *ap, socket=None, **kwargs):
        self.opened_socket = socket
        super().__init__(*ap, **kwargs)

    def response(self):
        print(self.opened_socket.recv(1024).rstrip().decode())

    def do_print(self, args):
        self.opened_socket.sendall(f"print (args)\n".encode())
        self.response()

    def do_info(self, args):
        self.opened_socket.sendall(f"info (args)\n".enconde())
        self.response()

    def complete_info(self, text, line, begindx, endixd):
        args = "host", "port"


host = "localhost" if len(sys.argv) < 2 else sys.argv[1]
port = 1337 if len(sys.argv) < 3 else int(sys.argv[2])
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
with sock as s:
    s.connect((host, port))
    while msg := sys.stdin.buffer.readline():
        s.sendall(msg)
        print(s.recv(1024).rstrip().decode())
