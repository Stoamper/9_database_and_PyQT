'''Написать функцию host_range_ping()
(возможности которой основаны на функции из примера 1)
для перебора ip-адресов из заданного диапазона.
Меняться должен только последний октет каждого адреса.
По результатам проверки должно выводиться соответствующее сообщение.'''

from task1 import check_ipaddress, host_ping

# Функция запроса первоначального аддреса и количества адресов
'''Если в последнем октете имеется возможность увеличивать адрес, то функция
возвращает список возможных адресов. После этого проверяет их доступность
с помощью host_ping 
'''
def host_range_ping(get_list=False):
    while True:
        start_ip = input('Введите первоначальный IP-адрес: ')
        try:
            ipv4_start = check_ipaddress(start_ip)
            last_oct = int(start_ip.split('.')[-1])
            break
        except Exception as e:
            print(e)

    while True:
        end_ip = input('Введите количество IP-адресов для проверки: ')
        if not end_ip.isnumeric():
            print('Требуется ввести число')
        else:
            if (last_oct + int(end_ip)) > 255 + 1:
                print(f'Возможно имзенить только последний октет.'
                      f'Максимальное число хостов равно {255 + 1 - last_oct}')
            else:
                break
    host_list = []
    # Формирование списка IP
    [host_list.append(str(ipv4_start + x)) for x in range (int(end_ip))]
    if not get_list:
        host_ping(host_list)
    else:
        return host_ping(host_list, True)


if __name__ == '__main__':
    host_range_ping()
