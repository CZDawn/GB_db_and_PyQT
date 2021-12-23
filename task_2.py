'''
Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона.
Меняться должен только последний октет каждого адреса.
По результатам проверки должно выводиться соответствующее сообщение.
'''


from ipaddress import ip_address
from task_1 import host_ping


def host_range_ping() -> list:
    start_ip_address = input('Введите начальный ip-адрес: ')
    last_octet = int(start_ip_address.split('.')[3])
    quantity_of_addresses_for_check = int(input('Сколько адресов проверить: '))
    result = []
    if (last_octet + quantity_of_addresses_for_check) > 256:
        print('Допустимо изменение только последнего октета в адресе!')
    else:
        try:
            ipv4 = ip_address(start_ip_address)
        except ValueError:
            print(f'Введен некорректный адрес веб узла!')
            return

        for index in range(quantity_of_addresses_for_check):
            host = str(ipv4+index)
            status = host_ping(host)
            result.append({'Узел': host, 'Статус': status})

    return result


if __name__ == '__main__':
    host_range_ping()

