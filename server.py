import sys
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

from common.utils import get_message, send_message


LOG = getLogger('server_logger')


@log_decorator
def processing_message(data, client, message_list, clients, names):
    LOG.debug(f'Handle client message - {data}')

    if ACTION in data and data[ACTION] == PRESENCE and TIME in data \
        and USER in data:
        if data[USER] not in names.keys():
            names[data[USER]] = client
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
            clients.remove(client)
            client.close()
        return
    elif ACTION in data and data[ACTION] == MESSAGE and TIME in data and SENDER in data and RECIPIENT in data and MESSAGE_TEXT in data:
        message_list.append(data)
        return
    elif ACTION in data and data[ACTION] == EXIT and TIME in data and USER in data:
        LOG.info(
            f'Client {client.getpeername()} disconnected from the server.'
        )
        clients.remove(names[data[USER]])
        names[data[USER]].close()
        del names[data[USER]]
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


@log_decorator
def message_handler(message, names, listen_sock):

    if message[RECIPIENT] in names and names[message[RECIPIENT]] in listen_sock:
        send_message(names[message[RECIPIENT]], message)
        LOG.info(
            f'Message from the client {message[SENDER]} '
            f'sended to adressee {message[RECIPIENT]}.'
        )
    elif message[RECIPIENT] in names and names[message[RECIPIENT]] not in listen_sock:
        raise ConnectionError
    else:
        no_user_dict = RESPONSE_300
        no_user_dict[ERROR] = f'User with name {message[RECIPIENT]} ' \
                              f'not registered on the server.'
        send_message(names[message[SENDER]], no_user_dict)
        LOG.error(f'{no_user_dict[ERROR]} Sending message is not available.')
        LOG.debug(f'User {message[SENDER]} get the response {no_user_dict}')


@log_decorator
def args_parser():
    parser = ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int)
    parser.add_argument('-a', default=DEFAULT_IP_ADDRESS)
    namespace = parser.parse_args(sys.argv[1:])
    if not 1023 < namespace.p < 65536:
        LOGG.critical(
            f'Incorrect enttered port "{namespace.p}".'
        )
        sys.exit(1)
    return namespace.a, namespace.p


def main():
    listen_address, listen_port = args_parser()
    LOG.info(
        f'Server ran with parameters - {listen_address}:{listen_port}'
    )

    server_sock = socket(AF_INET, SOCK_STREAM)
    server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_sock.bind((listen_address, listen_port))
    server_sock.settimeout(0.5)
    server_sock.listen(DEFAULT_MAX_QUEUE_LENGTH)

    clients = []
    messages = []
    names = dict()

    while True:
        try:
            client_sock, client_address = server_sock.accept()
        except OSError:
            pass
        else:
            LOG.info(f'Connection with client {client_address} established.')
            clients.append(client_sock)

        clients_senders = []
        clients_addressees = []
        errors_list = []

        try:
            if clients:
                clients_senders, clients_addressees, errors_list = select(clients, clients, [], 0)
        except OSError:
            print('Exception OSError - line 116')

        if clients_senders:
            for client_with_message in clients_senders:
                try:
                    processing_message(get_message(client_with_message), client_with_message, messages, clients, names)
                except Exception:
                    LOG.info(
                        f'Client {client_with_message.getpeername()} disconnected from the server.'
                    )
                    clients.remove(client_with_message)
        for message in messages:
            try:
                message_handler(message, names, clients_addressees)
            except Exception:
                LOG.info(f'Client {message[RECIPIENT]} disconnected from the server.')
                no_user_dict = RESPONSE_300
                no_user_dict[ERROR] = f'Client {message[RECIPIENT]} disconnected from the server.'
                send_message(names[message[SENDER]], no_user_dict)
                clients.remove(names[message[RESIPIENT]])
                del names[message[RECIPIENT]]
        messages.clear()


if __name__ == '__main__':
    main()

