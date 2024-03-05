#!/usr/bin/env python3


from socket import socket
from socket import AF_INET
from socket import SOCK_STREAM
from socket import SOL_SOCKET
from socket import SO_REUSEADDR

import select

from systemcall import SystemCall
from systemcall import WaitForRead


flag_server_process_quit = False



def handle_server_function(accept_socket: socket):

    while True:
        fd = accept_socket.fileno()
        yield WaitForRead(fd)

        data = accept_socket.recv(1024)
        decoded_data = data.decode('utf-8')

        if len(data) < 1:
            print(f'server thread quit')
            break

        elif decoded_data[:4] == 'QUIT':
            print(f'QUIT')
            break

        else:
            print(f'{data}')

    flag_server_process_quit = True


def handle_server_accept(server_socket: socket):

    fd = server_socket.fileno()
    yield WaitForAccept(fd)

    accept_socket, incoming_address = server_socket.accept()
    print(f'connection from {incoming_address}')

    args = (accept_socket, )

    next_thread = Thread(
        target=server_thread_function,
        args=args,
    )

    all_threads.append(next_thread)

    next_thread.start()


def main():
    global flag_server_process_quit

    server_socket = socket(
        family=AF_INET,
        type=SOCK_STREAM,
    )

    server_socket.setsockopt(
        SOL_SOCKET, SO_REUSEADDR, 1
    )

    server_socket.bind(('localhost', 10001))
    server_socket.listen()

    all_threads = []

    while True:

        if flag_server_process_quit:
            print(f'server process quit signal')
            break

        _ = handle_server_accept(server_socket)

    #map(Thread.join(), all_threads)
    print(f'server process quit')


if __name__ == '__main__':
    main()
