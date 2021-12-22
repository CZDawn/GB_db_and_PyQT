'''
Написать функцию host_ping(), в которой с помощью утилиты ping будет
проверяться доступность сетевых узлов. Аргументом функции является список,
в котором каждый сетевой узел должен быть представлен именем хоста или ip-адресом.
В функции необходимо перебирать ip-адреса и проверять их доступность с выводом
соответствующего сообщения («Узел доступен», «Узел недоступен»).
При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().
'''


import os
import subprocess
import platform
from subprocess import Popen, PIPE
from ipaddress import ip_address


def host_ping(hosts: list) -> None:
    '''Функция проверяет доступность каждого сетевого узла в списке.

    param hosts: список проверяемых сетевых узлов (ip-адреса и имена хостов)
    return: словарь сетевых узлов со значениями их доступности
    '''

    AVAILABLE = 'Узел доступен'
    UNAVAILABLE = 'Узел недоступен'

    # Параметр прерывания выполнения команды ping
    param = '-n' if platform.system().lower() == 'windows' else '-c'

    ping_process = Popen(['ping', param, '1', str(host)], stdout=PIPE)
    if ping_process.wait() == 0:
        result = f'{host} - {AVAILABLE}'
    else:
        result = f'{host} - {UNAVAILABLE}'

    print(result)


if __name__ == '__main__':
    hosts = [
        '192.168.8.1',
        '8.8.8.8',
        'yandex.ru'
    ]

    for host in hosts:
        try:
            host = ip_address(host)
        except Exception:
            host = host
        host_ping(hosts)

