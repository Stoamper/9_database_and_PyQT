'''Программа-сервер (серверная часть)'''

import sys
import json
import socket
import argparse
import logging
import logs.configs.server_log_config
import errors
import select
import time
from initial_project.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, SENDER, MESSAGE, MESSAGE_TEXT, RESPONSE_200, \
    RESPONSE_400, DESTINATION, EXIT
from initial_project.utilities import get_message, send_message
from decorators import log_dec

# Инициализация логирования сервера
SERVER_LOGGER = logging.getLogger('server_logger')


'''Функция process_client_message является обработчиком сообщений от клиентов'''
'''Принимает сообщение от клиента (словарь), проверяет его валидность, возвращает ответ для клиента (также словарь)'''

@log_dec
def process_client_message(message, messages_list, client, clients, names):
    SERVER_LOGGER.debug(f'Выполнение разбора сообщения от клиента: {message}')
    # Проверка: если сообщение о присутствии, то принимаем его и отвечаем
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message:
        # Регистрируем пользователя, если его нет. Если он есть, то отправляем ответ и завершаем соединение
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, RESPONSE_200)
        else:
            responce = RESPONSE_400
            responce[ERROR] = 'Имя пользователя уже занято. Выберите другое'
            send_message(client, responce)
            clients.remove(client)
            client.close()
        return
    # Проверка: если это текстовое сообщение с содержанием, то добавляем его в очередь сообщений (ответ не требуется)
    elif ACTION in message and message[ACTION] == MESSAGE and \
        TIME in message and MESSAGE_TEXT in message and \
            DESTINATION in message and SENDER in message:
        messages_list.append(message)
        return
    elif ACTION in message and message[ACTION] == EXIT and \
        ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
    # Если ничего не подошло, то выводим ошибку 400 "Bad request"
    else:
        response = RESPONSE_400
        response[ERROR] = 'Некорретный запрос'
        send_message(client, response)
        return


'''Функция адресной отправки сообщения определенному клиенту. Принимает словарь сообщение, список зарег. пользователей 
слушающие сокеты. Ничего обратно не возвращает'''
@log_dec
def process_message(message, names, listen_socks):
    if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
        send_message(names[message[DESTINATION]], message)
        SERVER_LOGGER.info(f'Пользователю {message[DESTINATION]} отправлено сообщение от пользователя {message[SENDER]}')
    elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
        raise ConnectionError
    else:
        SERVER_LOGGER.error(f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере. Отправка сообщения невозможна')


''' Функция-парсер аргументов командной строки '''
@log_dec
def create_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    # Проверка является ли указанный номер порта подходящим (в диапазоне от 1024 до 65535)
    if not 1023 < listen_port < 65536:
        SERVER_LOGGER.critical(f'Выполнена попытка запуска сервера с указанием неподходящего порта {listen_port}' 
                               f'Допустимые номера порта с 1024 по 65535 включительно')
        sys.exit(1)
    return listen_address, listen_port


'''Функция main используется для загрузки параметров командной строки'''
'''Если нет параметров, то задаем значения по умолчанию (DEFAULT_PORT)'''
'''Первоначально обрабатываем порт: server.py -p 8079 -a 192.168.1.2'''


def main():
    # Загрузка параметров командной строки (если их нет, то задаем дефолтные)
    listen_address, listen_port = create_arg_parser()

    SERVER_LOGGER.info(
        f'Сервер запущен'
        f'Адрес, с которого принимаются подключени: {listen_address}'
        f'Порт для подключений: {listen_port}'
        f'При отсутствии адреса принимаются соединения с любых адресов'
    )

    # Выполнение подготвоки сокета
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))
    transport.settimeout(1)

    # Подготовка списка клиентов и очереди сообщений
    clients = []
    messages = []

    # Подготовка словаря, содержащего имена пользователей и соответствующие им сокеты
    names = dict()

    # Прослушивание порта
    transport.listen(MAX_CONNECTIONS)
    # Основной цикл программы сервера (ожидаем подключения; если время вышло, то выводим исключение)
    while True:
        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            SERVER_LOGGER.info(f'Установлено соединение с ПК {client_address}')
            clients.append(client)

        recieve_data_list = []
        send_data_list = []
        errors_list = []

        # Выполнение проверки на ждущих клиентов
        try:
            if clients:
                recieve_data_list, send_data_list, errors_list = select.select(clients, clients, [], 0)
        except OSError:
            pass

        # При приеме сообщений и наличии в них содержания добавляем в словарь. При ошибке удаляем клиента
        if recieve_data_list:
            for client_with_message in recieve_data_list:
                try:
                    process_client_message(get_message(client_with_message), messages, client_with_message, clients, names)
                except Exception:
                    SERVER_LOGGER.info(f'Клиент {client_with_message.getpeername()} отключился от сервера')
                    clients.remove(client_with_message)

        # При наличии сообщений обрабатываем каждое из них
        for i in messages:
            try:
                process_message(i, names, send_data_list)
            except Exception:
                SERVER_LOGGER.info(f'Связь с клиентом {i[DESTINATION]} потеряна')
                clients.remove(names[i[DESTINATION]])
                del names[i[DESTINATION]]
        messages.clear()

'''
    # До 5 урока
    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError('Значение порта вне допустимого диапазона (должно быть от 1024 до 65535)')
    except IndexError:
        print('После параметра -\'p\' следует указать номер порта')
        sys.exit(1)
    except ValueError:
        print('Значение порта вне допустимого диапазона (должно быть от 1024 до 65535)')
        sys.exit(1)

    # Загружаем адрес, который будем слушать

    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = ''
    except IndexError:
        print('После параметра -\'a\' необходимо указать адрес, который будет слушать сервер')
        sys.exit(1)

    # Готовим сокет

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))

    # Слушаем порт

    transport.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport.accept()
        try:
            message_from_client = get_message(client)
            print(message_from_client)
            # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
            response = process_client_message(message_from_client)
            send_message(client, response)
            client.close()
        except (ValueError, json.JSONDecodeError):
            print('Получено некорректное сообщение от клиента')
            client.close()
'''
if __name__ == '__main__':
    main()
