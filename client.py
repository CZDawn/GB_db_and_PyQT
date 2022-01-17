import sys
import argparse
from logging import getLogger
from PyQt5.QtWidgets import QApplication

from common.variables import *
from errors import ServerError
from decorators import log_decorator
from client.transport import ClientTransport
from client.main_window import ClientMainWindow
from client.client_db_storage import ClientDatabaseStorage
from client.start_window import StartUserNameEnteringWindow

LOG = getLogger('client_logger')


@log_decorator
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    if not 1023 < server_port < 65536:
        LOG.critical(
            f'Valid addresses are 1024 to 65535. The client finishes.')
        exit(1)
    return server_address, server_port, client_name


if __name__ == '__main__':
    server_address, server_port, client_name = arg_parser()
    client_app = QApplication(sys.argv)

    if not client_name:
        start_window = StartUserNameEnteringWindow()
        client_app.exec_()
        if start_window.ok_button_pressed:
            client_name = start_window.client_name.text()
            del start_window
        else:
            exit(0)

    LOG.info(
        f'Launched client with parameters: ip_address: {server_address} , port: {server_port}, username: {client_name}')

    database = ClientDatabaseStorage(client_name)

    try:
        transport = ClientTransport(server_port, server_address, database, client_name)
    except ServerError as error:
        print(error.text)
        exit(1)
    transport.setDaemon(True)
    transport.start()

    main_window = ClientMainWindow(database, transport)
    main_window.make_connection(transport)
    client_app.exec_()

    transport.transport_shutdown()
    transport.join()
