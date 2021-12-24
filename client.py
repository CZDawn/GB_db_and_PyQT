import sys
from threading import Thread
from logging import getLogger
from json import JSONDecodeError
from argparse import ArgumentParser
from socket import socket, SOCK_STREAM, AF_INET
from time import strftime, strptime, ctime, time, sleep

from decorators import log_decorator
from logs import client_logger_config
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, \
                             PRESENCE, TIME, USER, RESPONSE, ERROR, MESSAGE, \
                             MESSAGE_TEXT, SENDER, RECIPIENT, EXIT
from common.utils import send_message, get_message
from errors import ServerError, ReqFieldMissingError, IncorrectDataReceivedError


LOG = getLogger('client_logger')


@log_decorator
def server_message_handler(sock, username):
    while True:
        try:
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and TIME in message and SENDER in message and RECIPIENT in message and MESSAGE_TEXT in message and message[RECIPIENT] == username:
                message_time = strftime("%d.%m.%Y %H:%m:%S", strptime(ctime(message[TIME])))
                print(f'{message_time} - {message[SENDER]}: {message[MESSAGE_TEXT]}')
                LOG.info(
                    f'User {username} obtain the message {message[MESSAGE_TEXT]} '
                    f'from the user {message[SENDER]}'
                )
            elif message[RESPONSE] == 300:
                LOG.debug(
                    f'Obtained answer "Response 300: {message[ERROR]}".'
                )
                print(f'{message[ERROR]}')
            else:
                LOG.error(
                    f'Incorrect message "{message}" obtained'
                )
        except IncorrectDataReceivedError:
            LOG.error('Decoding of obtained message failed.')
        except (ConnectionError, ConnectionRefusedError, ConnectionAbortedError, OSError, JSONDecodeError):
            LOG.critical(f'Lost connection with server')
            break


@log_decorator
def create_message(sock, username):
    addressee = input('Enter addressees username: ')
    message = input('Enter your message: ')
    dict_message = {
        ACTION: MESSAGE,
        TIME: time(),
        SENDER: username,
        RECIPIENT: addressee,
        MESSAGE_TEXT: message
    }
    LOG.debug(f'Created dict-message: {dict_message}')
    try:
        send_message(sock, dict_message)
        LOG.info(f'Message sended to user {addressee}')
    except:
        LOG.critical(f'Lost connection with server')
        sys.exit(1)


@log_decorator
def exit_message(username):
    return {
        ACTION: EXIT,
        TIME: time(),
        USER: username
    }


@log_decorator
def user_menu(sock, username):
    print('Commands:')
    print('1 - send message.')
    print('2 - exit.')

    while True:
        command = input('Make your choice: ')
        if command == '1':
            create_message(sock, username)
        elif command == '2':
            send_message(sock, exit_message(username))
            print('Program is finished.')
            LOG.info(f'Client {username} stop working.')
            sleep(0.5)
            break
        else:
            print('Unknown command.')


@log_decorator
def confirm_presence(username):
    message = {
        ACTION: PRESENCE,
        TIME: time(),
        USER: username
    }
    LOG.info(f'Created {PRESENCE} message for user {username}')
    return message


@log_decorator
def receive_message(message):
    LOG.debug(f'Handle server {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            LOG.info('Response 200: OK')
            return 'Response 200: OK'
        elif message[RESPONSE] == 400:
            LOG.error(f'Obtained response from server "Response 400: {message[ERROR]}".')
            raise ServerError(f' Response 400: {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


@log_decorator
def args_parser():
    parser = ArgumentParser()
    parser.add_argument('address', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    if not 1023 < namespace.port < 65536:
        LOG.critical(f'Port "{namespace.port}" was entered incorrect. ')
        sys.exit(1)
    return namespace.address, namespace.port, namespace.name


def main():
    server_ip, server_port, client_name = args_parser()
    if not client_name:
        client_name = input('Введите имя пользователя: ')
    LOG.info(
        f'Client app connected. Server IP-address: {server_ip}, '
        f'server port: {server_port}, username: {client_name}.'
    )

    try:
        client_sock = socket(AF_INET, SOCK_STREAM)
        client_sock.connect((server_ip, server_port))
        send_message(client_sock, confirm_presence(client_name))
        answer = receive_message(get_message(client_sock))
        LOG.info(
            f'Connection with server {server_ip}:{server_port}. '
            f'Server response: {answer}'
        )
        print('Connnected to server')
    except ServerError as error:
        LOG.error(f'Response with error: {error.text}')
        sys.exit(1)
    except ReqFieldMissingError as error:
        LOG.error(f'Response without required field: {error.missing_field}')
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        LOG.critical(f'Connection with server is lost {server_ip}:{server_port}')
        sys.exit(1)
    except JSONDecodeError:
        LOG.error(f'Failed decoding of JSON message.')
        sys.exit(1)
    else:
        receiver = Thread(target=server_message_handler, args=(client_sock, client_name))
        receiver.daemon = True
        receiver.start()

        sender = Thread(target=user_menu, args=(client_sock, client_name))
        sender.daemon = True
        sender.start()

        while True:
            sleep(1)
            if receiver.is_alive() and sender.is_alive():
                continue
            break


if __name__ == '__main__':
    main()

