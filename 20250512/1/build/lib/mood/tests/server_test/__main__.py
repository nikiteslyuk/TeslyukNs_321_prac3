#!/usr/bin/env python3
from mood.server.__main__ import start_server
import multiprocessing
import asyncio
import unittest
import socket
import os
import sys
import threading
import time

def setup():
    """Запуск сервера, подключение к сокету и вход под именем"""
    proc = multiprocessing.Process(target=start_server)
    proc.start()
    time.sleep(2)

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect(('localhost', 1337))
    message = f"TESTER\n"
    soc.sendall(bytes(message.encode()))
    ans = soc.recv(4096).rstrip().decode()

    message = f"movemonsters off\n"
    soc.sendall(bytes(message.encode()))
    ans = soc.recv(4096).rstrip().decode()
 
    return proc, soc

def terminate(proc):
    """Остановка сервера и закрытие сокета"""
    proc.terminate()

def testing(soc, arg):
    """Отправка команды на сервер и получение ответа"""
    message = f"{arg}\n"
    soc.sendall(bytes(message.encode()))
    ans = soc.recv(1024).rstrip().decode()
    return ans

if __name__ == '__main__':
    import doctest
    doctest.testfile("test.rst")
