"""Программа-клиент (клентская часть)"""

import argparse
import logging
import sys
import json
import socket
import time
import errors
import threading
import logs.configs.client_log_config
from initial_project.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, SENDER, MESSAGE, MESSAGE_TEXT, \
    DESTINATION, EXIT
from initial_project.utilities import get_message, send_message
from decorators import log_dec

''' Проводим инициализацию логера клиента '''
CLIENT_LOGGER = logging.getLogger('client_logger')


'''Функция создания словаря с сообщением о выходе'''
@log_dec
def create_exit_message(account_name):
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name
    }


'''Функция message_from_server обрабатывает сообщения других пользователей, поступающих с сервера'''
@log_dec
def message_from_server(sock, username):
    while True:
        try:
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and SENDER in message \
                    and MESSAGE_TEXT in message and DESTINATION in message and \
                    message[DESTINATION] == username:
                print(f'От пользователя {message[SENDER]} получено сообщение:\n'
                    f'{message[MESSAGE_TEXT]}\n')
                CLIENT_LOGGER.info(f'От пользователя {message[SENDER]} получено сообщение:\n'
                    f'{message[MESSAGE_TEXT]}')
            else:
                CLIENT_LOGGER.error(f'От сервера получено некорректное сообщение: {message}')
        except errors.IncorrectDataRecievedError:
            CLIENT_LOGGER.error(f'Не получилось выполнить декодирование полученного сообщения')
        except (json.JSONDecodeError, OSError, ConnectionError,
                ConnectionAbortedError, ConnectionResetError):
            CLIENT_LOGGER.critical(f'Соединение с сервером утрачено')
            break


'''Функция create_message производит запрос сообщения и его получателя, после отправляет данные на сервер'''
@log_dec
def create_message(sock, account_name='Guest'):


    recipient_user = input('Введите получателя сообщения: ')
    message = input('Введите сообщение. Для выхода введите \'!out!\': ')
    '''if message == '!out!' or message == '!OUT!':
        sock.close()
        CLIENT_LOGGER.info('Выход по команде пользователя')
        print('Thank you')
        sys.exit(0)'''
    message_dict = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: recipient_user,
        TIME: time.time(),
        MESSAGE_TEXT: message
    }
    CLIENT_LOGGER.debug(f'Создан словарь сообщения: {message_dict}')
    try:
        send_message(sock, message_dict)
        CLIENT_LOGGER.info(f'Сообщение отправлено пользователю {recipient_user}')
    except:
        CLIENT_LOGGER.critical('Соединение с сервером утрачено')
        sys.exit(1)


'''Функция для вывода справки по использованию чата'''
def print_help():
    print('Чат поддерживает следующие команды: ')
    print('message - отправить сообщение (получатель и текст запрашиваются отдельно')
    print('help - вывод справки')
    print('exit - выход из программы')


'''Функция для выполнения взаимодействия с пользователем (запрос команд, отправка сообщения)'''
@log_dec
def user_interactive(sock, username):
    print_help()
    while True:
        command = input('Для дальнейшей работы введите команду: ')
        if command == 'message' or command == 'MESSAGE' or command == 'ьуыыфпу':
            create_message(sock, username)
        elif command == 'help' or command == 'HELP' or command == 'рудз':
            print_help()
        elif command == 'exit' or command == 'EXIT' or command == 'учше':
            send_message(sock, create_exit_message(username))
            print('Завершение работы')
            CLIENT_LOGGER.info(f'Работа завершена по команде пользователя {username}')
            time.sleep(1)
            break
        else:
            print('Команда не распознана. Введите заново')


'''Функция create_presence генерирует запрос о присутствии клиент'''
@log_dec
def create_presence(account_name):
    # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
    output = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    CLIENT_LOGGER.debug(f'Для пользователя {account_name} сформировано {PRESENCE} сообщение')
    return output


'''Функция server_answer разбирает ответ сервера (ОК - 200, НЕ ОК - 400)'''
@log_dec
def server_answer(message):
    CLIENT_LOGGER.debug(f'Разбор сообщения сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return "The HTTP 200 OK"
        elif message[RESPONSE] == 400:
            raise errors.ServerError(f'400 : {message[ERROR]}')
    # return ValueError
    raise errors.ReqFieldMissingError(RESPONSE)


'''Парсер для аргументов командной строки'''
'''После работы парсера возвращается 3 параметра (адрес, порт, режим работы клиента)'''
@log_dec
def create_arguments_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    # Проверка является ли указанный номер порта подходящим (в диапазоне от 1024 до 65535)
    if not 1023 < server_port < 65536:
        CLIENT_LOGGER.critical(f'Запуск с неподходящим номером порта ({server_port}).'
                               f'Выберите порт от 1024 до 65535 включительно')
        sys.exit(1)

    # Проверка является ли указанный режим работы допустимым НЕ ТРЕБУЕТСЯ
    '''if client_mode not in ('listen', 'send'):
        CLIENT_LOGGER.critical(f'Указан недопустимый режим работы ({client_mode}).'
                               f'Выберите один из режимов (прослушивание или отправка): listen, send')
        sys.exit(1)'''

    return server_address, server_port, client_name


'''Функция main используется для загрузки параметров командной строки'''

def main():
    # Загрузка параметров командной строки
    server_address, server_port, client_name = create_arguments_parser()

    # Запрос имени пользователя при его отсутствии
    if not client_name:
        client_name = input('Пожалуйста укажите имя пользователя: ')

    CLIENT_LOGGER.info(f'Выполнен запуск клиента со следующими параметрами: адрес сервера {server_address}, '
                       f'порт: {server_port}, имя пользователя: {client_name}')

    # Инициализация сокета и обмен
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence(client_name))
        answer = server_answer(get_message(transport))
        CLIENT_LOGGER.info(f'Соединение с сервером установлено. Получен ответ от сервера: {answer}')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Не удалось декодировать принятую JSON-строку')
        sys.exit(1)
    except errors.ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(f'В ответе сервера нет поля {missing_error.missing_field}')
        sys.exit(1)
    except (ConnectionError, ConnectionRefusedError):
        CLIENT_LOGGER.critical(f'Не удалось подключиться к серверу {server_address}:{server_port}'
                               f'Конечный компьютер отверг запрос на подключение')
        sys.exit(1)
    except errors.ServerError as error:
        CLIENT_LOGGER.error(f'При попытке соединения сервер вернул ошибку: {error.text}')
        sys.exit(1)
    else:
        # При установке соединения начинаем клиентский процесс приема сообщений
        reciever = threading.Thread(target=message_from_server, args=(transport, client_name))
        reciever.daemon = True
        reciever.start()

        # Запуск отправки сообщений и взаимодействия с пользователем
        user_interface = threading.Thread(target=user_interactive, args=(transport, client_name))
        user_interface.daemon = True
        user_interface.start()
        CLIENT_LOGGER.debug('Процессы запущены')

        # Добавляем цикл, позволяющий отслеживать состояние пользователя (или вышел, или потерялось соединение)
        # При таком сценарии осуществляем остановку
        while True:
            time.sleep(1)
            if reciever.is_alive() and user_interface.is_alive():
                continue
            break

'''
# До 5 урока
    # client.py 192.168.0.24 8079
    # server.py -p 8079 192.168.0.24
    try:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
        if server_port < 1024 or server_port > 65535:
            raise ValueError('Номер порта не в диапазоне от 1024 до 65535')
    except IndexError:
        server_address = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT
    except ValueError:
        print('Номер порта не в диапазоне от 1024 до 65535')
        sys.exit(1)

    # Проводим инициализацию и обмен
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.connect((server_address, server_port))
    message_to_server = create_presence()
    send_message(transport, message_to_server)
    try:
        answer = server_answer(get_message(transport))
        print(answer)
    except (ValueError, json.JSONDecodeError):
        print('Не удается декодировать сообщение сервера')
'''

if __name__ == '__main__':
    main()
