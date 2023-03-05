'''1. Написать функцию host_ping(), в которой с помощью утилиты ping
будет проверяться доступность  сетевых узлов.
Аргументом функции является список, в котором каждый сетевой узел
должен быть  представлен именем хоста или ip-адресом.
В функции необходимо перебирать ip-адреса и проверять
их доступность с выводом соответствующего сообщения
(«Узел доступен», «Узел недоступен»).
При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().
(Внимание! Аргументом сабпроцесcа должен быть список, а не строка!!!
Для уменьшения времени работы скрипта при проверке нескольких ip-адресов,
решение необходимо выполнить с помощью потоков)'''

import os
import subprocess
import platform
import time
import threading
import ipaddress
from pprint import pprint

# Блокировка потока
lock = threading.Lock()

# Словарь с результатами
node_result = {'Доступные узлы': '', 'Недоступные узлы': ''}

# Заглушка (поток на экран не выводится)
DNull = open(os.devnull, 'w')

# Функция, которая проверяет валидность введенного IP-адреса
def check_ipaddress(user_ip):
    try:
        ipv4 = ipaddress.ip_address(user_ip)
    except ValueError:
        raise Exception('Введен некорректный ip-адрес')
    return ipv4

# Функция проверки доступности указанного узла
def ping(ipv4, node_result, get_list):
    # Поддержка мультиплатформенности
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    response = subprocess.Popen(['ping', param, '1', '-w', '1', str(ipv4)], stdout=subprocess.PIPE)

    if response.wait() == 0:
        with lock:
            node_result['Доступные узлы'] += f'{ipv4}\n'
            res = f'{str(ipv4)} - узел является доступным'
            if not get_list:
                # Отображение результата, если он не добавляется в словарь
                print(res)
            return res
    else:
        with lock:
            node_result['Недоступные узлы'] += f'{ipv4}\n'
            res = f'{str(ipv4)} - узел является недоступным'
            if not get_list:
                # Отображение результата, если он не добавляется в словарь
                print(res)
            return res

# Функция проверки доступности хостов
def host_ping(hosts_list, get_list=False):
    print('Начало проверки доступности узлов...')
    threads = []
    # Проверка, является ли значение ip-адресом
    for host in hosts_list:
        try:
            ipv4 = check_ipaddress(host)
        except Exception as e:
            print(f'Поданный {host} - {e} воспринимается как доменное имя')
            ipv4 = host

        thread = threading.Thread(target=ping, args=(ipv4, node_result, get_list),
                                  daemon=True)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    if get_list:
        return node_result

if __name__ == '__main__':
    hosts_list = ['8.8.8.8', 'ya.ru', '192.168.0.26',
                  '0.0.0.1', '0.0.0.2', '127.0.0.1']
    start = time.time()
    host_ping(hosts_list)
    end = time.time()
    print(f'Время выполнения составило: {int(end - start)} с')
    pprint(node_result)


