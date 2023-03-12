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

class ClientSender(threading.Thread):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    # Функция создания словаря с сообщением о выходе
    def create_exit_message(self):
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }

    # Функция запроса адресата сообщения и текста сообщения
    def create_message(self):

        recipient_user = input('Введите получателя сообщения: ')
        message = input('Введите сообщение. Для выхода введите \'!out!\': ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: recipient_user,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        CLIENT_LOGGER.debug(f'Создан словарь сообщения: {message_dict}')
        try:
            send_message(self.sock, message_dict)
            CLIENT_LOGGER.info(f'Сообщение отправлено пользователю {recipient_user}')
        except:
            CLIENT_LOGGER.critical('Соединение с сервером утрачено')
            sys.exit(1)

    # Функция для выполнения взаимодействия с пользователем (запрос команд, отправка сообщения)
    def run(self):
        self.print_help()
        while True:
            command = input('Для дальнейшей работы введите команду: ')
            if command == 'message':
                self.create_message()
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                try:
                    send_message(self.sock, self.create_exit_message())
                except:
                    pass
                print('Завершение работы')
                CLIENT_LOGGER.info(f'Работа завершена по команде пользователя')
                time.sleep(1)
                break
            else:
                print('Команда не распознана. Введите заново')

    # Функция для вывода справки по использованию чата
    def print_help(self):
        print('Чат поддерживает следующие команды: ')
        print('message - отправить сообщение (получатель и текст запрашиваются отдельно')
        print('help - вывод справки')
        print('exit - выход из программы')

# Класс, принимающий сообщения с сервера (прием сообщений, вывод в консоль)
class ClientReader(threading.Thread):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    # Основной цикл приемника сообщений
    def run(self):
        while True:
            try:
                message = get_message(self.sock)
                if ACTION in message and message[ACTION] == MESSAGE and SENDER in message \
                        and MESSAGE_TEXT in message and DESTINATION in message and \
                        message[DESTINATION] == self.account_name:
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

# Функция create_presence генерирует запрос о присутствии клиент
@log_dec
def create_presence(account_name):
    output = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    CLIENT_LOGGER.debug(f'Для пользователя {account_name} сформировано {PRESENCE} сообщение')
    return output

# Функция server_answer разбирает ответ сервера (ОК - 200, НЕ ОК - 400)
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

    return server_address, server_port, client_name

def main():
    # Загрузка параметров командной строки
    server_address, server_port, client_name = create_arguments_parser()

    # Запрос имени пользователя при его отсутствии
    if not client_name:
        client_name = input('Пожалуйста укажите имя пользователя: ')
    else:
        print(f'Клиентский модуль запущен с именем {client_name}')

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
        reciever = ClientReader(client_name, transport)
        reciever.daemon = True
        reciever.start()

        # Запуск отправки сообщений и взаимодействия с пользователем
        user_interface = ClientSender(client_name, transport)
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


if __name__ == '__main__':
    main()


