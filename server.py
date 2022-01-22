import os
import sys
import configparser

from select import select
from threading import Thread, Lock
from logging import getLogger
from PyQt5.QtCore import QTimer
from argparse import ArgumentParser
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR


from common.variables import *
from server.descriptors import Port
from decorators import log_decorator
from logs import server_logger_config
from metaclasses import ServerVerifier
from common.utils import get_message, send_message
from server.server_db_storage import ServerDatabaseStorage
from server.server_gui import MainWindow, gui_create_model, \
                              UsersActivityHistoryWindow, \
                              create_statistic_model, ServerConfigWindow


LOG = getLogger('server_logger')

new_connection = False
conflag_lock = Lock()


@log_decorator
def args_parser(default_port, default_address):
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

            clients_senders = []
            clients_addressees = []
            errors_list = []

            try:
                if self.clients:
                    clients_senders, clients_addressees, errors_list = select(self.clients, self.clients, [], 0)
            except OSError:
                print('Socket error')

            if clients_senders:
                for client_with_message in clients_senders:
                    try:
                        self.processing_message(get_message(client_with_message), client_with_message)
                    except OSError:
                        LOG.info(
                            f'Client {client_with_message.getpeername()} disconnected from the server.'
                        )
                        for name in self.names:
                            if self.names[name] == client_with_message:
                                self.database.user_logout(name)
                                del self.names[name]
                                break
                        self.clients.remove(client_with_message)
            for message in self.messages:
                try:
                    self.message_handler(message, clients_addressees)
                except Exception:
                    LOG.info(f'Client {message[RECIPIENT]} disconnected from the server.')
                    self.clients.remove(self.names[message[RECIPIENT]])
                    self.database.user_logout(message[RECIPIENT])
                    del self.names[message[RECIPIENT]]
            self.messages.clear()

    def processing_message(self, message, client):
        global new_connection
        LOG.debug(f'Handle client message - {message}')

        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            if message[USER] not in self.names.keys():
                self.names[message[USER]] = client
                client_ip, client_port = client.getpeername()
                self.database.user_login(message[USER], client_ip, client_port)
                send_message(client, RESPONSE_200)
                with conflag_lock:
                    new_connection = True
            else:
                response = RESPONSE_400
                response[ERROR] = 'Username is not available.'
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        elif ACTION in message and message[ACTION] == MESSAGE and TIME in message \
                and SENDER in message and RECIPIENT in message \
                and MESSAGE_TEXT in message and self.names[message[SENDER]] == client:
            self.messages.append(message)
            self.database.process_message(message[SENDER], message[RECIPIENT])
            return
        elif ACTION in message and message[ACTION] == EXIT  and USER in message \
                and self.names[message[USER]] == client:
            LOG.info(
                f'Client {client.getpeername()} disconnected from the server.'
            )
            self.database.user_logout(message[USER])
            self.clients.remove(self.names[message[USER]])
            self.names[message[USER]].close()
            del self.names[message[USER]]
            with conflag_lock:
                new_connection = True
            return
        elif ACTION in message and message[ACTION] == GET_CONTACTS and USER in message \
                and self.names[message[USER]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = self.database.users_contacts_list(message[USER])
            send_message(client, response)
        elif ACTION in message and message[ACTION] == ADD_CONTACT and USER in message \
                and self.names[message[USER]] == client:
            self.database.add_contact(message[USER], message[CONTACT])
            send_message(client, RESPONSE_200)
        elif ACTION in message and message[ACTION] == REMOVE_CONTACT and USER in message \
                and self.names[message[USER]] == client:
            self.database.remove_contact(message[USER], message[CONTACT])
            send_message(client, RESPONSE_200)
        elif ACTION in message and message[ACTION] == USERS_REQUEST and USER in message \
                and self.names[message[USER]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = [user[0] for user in self.database.all_users_list()]
            send_message(client, response)
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
            LOG.error(f'User {message[RECIPIENT]} is not registered on the server, sending message is impossible')

def main():
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f'{dir_path}/server/{"server.ini"}')

    listen_address, listen_port = args_parser(
        config['SETTINGS']['Default_port'], config['SETTINGS']['Listen_address']
    )
    database = ServerDatabaseStorage(
        os.path.join(
            config['SETTINGS']['Database_path'],
            config['SETTINGS']['Database_file']))

    server = Server(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    server_app = QApplication(sys.argv)
    main_window = MainWindow()

    main_window.statusBar().showMessage('Server Working')
    main_window.active_users_table.setModel(gui_create_model(database))
    main_window.active_users_table.resizeColumnsToContents()
    main_window.active_users_table.resizeRowsToContents()

    def list_update():
        global new_connection
        if new_connection:
            main_window.active_users_table.setModel(gui_create_model(database))
            main_window.active_users_table.resizeColumnsToContents()
            main_window.active_users_table.resizeRowsToContents()
            with conflag_lock:
                new_connection = False

    def show_statistics():
        global statistic_window
        statistic_window = UsersActivityHistoryWindow()
        statistic_window.users_activity_history_table.setModel(create_statistic_model(database))
        statistic_window.users_activity_history_table.resizeColumnsToContents()
        statistic_window.users_activity_history_table.resizeRowsToContents()
        statistic_window.show()

    def server_config():
        global config_window
        config_window = ServerConfigWindow()
        config_window.db_path.insert(config['SETTINGS']['Database_path'])
        config_window.db_file.insert(config['SETTINGS']['Database_file'])
        config_window.port.insert(config['SETTINGS']['Default_port'])
        config_window.ip_address.insert(config['SETTINGS']['Listen_address'])
        config_window.save_button.clicked.connect(save_server_config)

    def save_server_config():
        global config_window
        message = QMessageBox()
        config['SETTINGS']['Database_path'] = config_window.db_path.text()
        config['SETTINGS']['Database_file'] = config_window.db_file.text()
        try:
            port = int(config_window.port.text())
        except ValueError:
            message.warning(config_window, 'ERROR', 'Port should be an integer')
        else:
            config['SETTINGS']['Listen_address'] = config_window.ip_address.text()
            if 1023 < port < 65536:
                config['SETTINGS']['Default_port'] = str(port)
                with open('server.ini', 'w') as file:
                    config.write(file)
                    message.information(config_window, 'OK', 'Settings succesfully saved')
            else:
                message.warning(config_window, 'ERROR', 'Port should in interval from 1024 to 65536')

    timer = QTimer()
    timer.timeout.connect(list_update)
    timer.start(1000)

    main_window.refresh_button.triggered.connect(list_update)
    main_window.clients_activity_history_button.triggered.connect(show_statistics)
    main_window.server_config_button.triggered.connect(server_config)

    server_app.exec_()


if __name__ == '__main__':
    main()
