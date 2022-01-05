import sys
from threading import Thread
from select import select
from logging import getLogger
from argparse import ArgumentParser
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

from logs import server_logger_config
from decorators import log_decorator
from common.variables import DEFAULT_IP_ADDRESS, DEFAULT_PORT, \
    DEFAULT_MAX_QUEUE_LENGTH, ACTION, PRESENCE, TIME, \
    ERROR, USER, MESSAGE, MESSAGE_TEXT, SENDER, \
    RESPONSE_200, RESPONSE_300, RESPONSE_400, \
    EXIT, RECIPIENT

from descriptors import Port
from metaclasses import ServerVerifier
from server_db_storage import ServerDatabaseStorage
from common.utils import get_message, send_message


LOG = getLogger('server_logger')


@log_decorator
def args_parser():
    parser = ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int)
    parser.add_argument('-a', default=DEFAULT_IP_ADDRESS)
    namespace = parser.parse_args(sys.argv[1:])
    return namespace.a, namespace.p


class Server(Thread, metaclass=ServerVerifier):
    port = Port()

    def __init__(self, listen_address, listen_port, database):
        self.socket = None
        self.addr = listen_address
        self.port = listen_port
        self.database = database

        self.clients = []
        self.messages = []
        self.names = dict()

        super().__init__()

    def init_socket(self):
        LOG.info(
            f'Server ran with parameters - {self.addr}:{self.port}'
        )

        server_sock = socket(AF_INET, SOCK_STREAM)
        server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server_sock.bind((self.addr, self.port))
        server_sock.settimeout(0.5)

        self.socket = server_sock
        self.socket.listen(DEFAULT_MAX_QUEUE_LENGTH)

    def run(self):
        self.init_socket()

        while True:
            try:
                client_sock, client_address = self.socket.accept()
            except OSError:
                pass
            else:
                LOG.info(f'Connection with client {client_address} established.')
                self.clients.append(client_sock)
                print(self.clients)

            clients_senders = []
            clients_addressees = []
            errors_list = []

            try:
                if self.clients:
                    clients_senders, clients_addressees, errors_list = select(self.clients, self.clients, [], 0)
            except OSError:
                print('Exception OSError - line 75')

            if clients_senders:
                for client_with_message in clients_senders:
                    try:
                        self.processing_message(get_message(client_with_message), client_with_message)
                    except Exception:
                        LOG.info(
                            f'Client {client_with_message.getpeername()} disconnected from the server.'
                        )
                        self.clients.remove(client_with_message)
            for message in self.messages:
                try:
                    self.message_handler(message, clients_addressees)
                except Exception:
                    LOG.info(f'Client {message[RECIPIENT]} disconnected from the server.')
                    self.clients.remove(self.names[message[RECIPIENT]])
                    del self.names[message[RECIPIENT]]
            self.messages.clear()

    def processing_message(self, data, client):
        LOG.debug(f'Handle client message - {data}')

        if ACTION in data and data[ACTION] == PRESENCE and TIME in data and USER in data:
            if data[USER] not in self.names.keys():
                self.names[data[USER]] = client
                client_ip, client_port = client.getpeername()
                self.database.user_login(data[USER], client_ip, client_port)
                send_message(client, RESPONSE_200)
                LOG.info(
                    f'Client {client.getpeername()} connected. '
                    f'Response sended {RESPONSE_200}'
                )
            else:
                response = RESPONSE_400
                response[ERROR] = 'Username is not available.'
                send_message(client, response)
                LOG.error(
                    f'Attempt connection user {client.getpeername()} with '
                    f'not available username. Sended response {RESPONSE_400}'
                )
                self.clients.remove(client)
                client.close()
            return
        elif ACTION in data and data[ACTION] == MESSAGE and TIME in data and SENDER in data and RECIPIENT in data \
                and MESSAGE_TEXT in data:
            self.messages.append(data)
            return
        elif ACTION in data and data[ACTION] == EXIT and TIME in data and USER in data:
            LOG.info(
                f'Client {client.getpeername()} disconnected from the server.'
            )
            self.database.user_logout(data[USER])
            self.clients.remove(self.names[data[USER]])
            self.names[data[USER]].close()
            del self.names[data[USER]]
            return
        else:
            response = RESPONSE_400
            response[ERROR] = 'Bad request.'
            LOG.debug(
                f'Have got incorrect request from the client {client.getpeername()}, '
                f'sended response {response}'
            )
            send_message(client, response)
            return

    def message_handler(self, message, listen_socks):
        if message[RECIPIENT] in self.names and self.names[message[RECIPIENT]] in listen_socks:
            send_message(self.names[message[RECIPIENT]], message)
            LOG.info(
                f'Message from the client {message[SENDER]} '
                f'sended to adressee {message[RECIPIENT]}.'
            )
        elif message[RECIPIENT] in self.names and self.names[message[RECIPIENT]] not in listen_socks:
            raise ConnectionError
        else:
            no_user_dict = RESPONSE_300
            no_user_dict[ERROR] = f'User with name {message[RECIPIENT]} ' \
                                  f'not registered on the server.'
            send_message(self.names[message[SENDER]], no_user_dict)
            LOG.error(f'{no_user_dict[ERROR]} Sending message is not available.')
            LOG.debug(f'User {message[SENDER]} get the response {no_user_dict}')


def main():
    listen_address, listen_port = args_parser()
    database = ServerDatabaseStorage()

    server = Server(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    while True:
        print('Commands:')
        print('1 - Stop server')
        print('2 - Show all users')
        print('3 - Show active users')
        print('4 - Show login history')

        user_command = int(input('Make your choice: '))
        try:
            user_command = int(user_command)
        except ValueError:
            print('Please enter an integer!')

        if user_command == 1:
            break
        elif user_command == 2:
            print(database.all_users_list())
        elif user_command == 3:
            print(database.active_users_list())
        elif user_command == 4:
            print(database.users_login_history_list())
        else:
            print('Invalid command!')


if __name__ == '__main__':
    main()
