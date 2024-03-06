#!/usr/bin/env python3

from socket import socket
from socket import AF_INET
from socket import SOCK_STREAM
from socket import SOL_SOCKET
from socket import SO_REUSEADDR

from lib.scheduler import Scheduler
from lib.systemcall import ReadWait
from lib.systemcall import WriteWait
from lib.systemcall import NewTask
from lib.systemcall import Sleep
from lib.systemcall import NullSystemCall


def handle_client(client:socket, address):
    if not isinstance(client, socket):
        raise TypeError(f'client must be of type socket, not {type(socket)}')
    print(f'connection from address {address}')

    fd = client.fileno()

    while True:
        yield ReadWait(fd)

        data = client.recv(65536)

        if not data:
            break

        yield WriteWait(fd)
        client.send(data)

    client.close()
    print(f'client closed: address {address}')


def server(port):
    print(f'Server starting')

    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind(('', port))
    server_socket.listen()

    while True:
        print(f'waiting for read')
        print(f'fileno: {server_socket.fileno()}')
        yield ReadWait(server_socket.fileno())
        client, address = server_socket.accept()
        print(f'accept: {address}')
        yield NewTask(f'handle_client_{address[1]}', handle_client(client, address))


def print_alive():
    yield NullSystemCall
    print(f'alive')


def alive():
    while True:
        yield NewTask('print alive', print_alive())
        yield Sleep(10.0)


def main():

    scheduler = Scheduler()
    scheduler.new_task('alive function (task)', alive())
    scheduler.new_task('server main thread', server(45000))
    scheduler.run()


if __name__ == '__main__':
    main()
