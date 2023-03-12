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

# Функция-парсер аргументов командной строки
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

# Основной класс сервера
class Server:
    def __init__(self, listen_address, listen_port):
        # Параметры подключения
        self.addr = listen_address
        self.port = listen_port

        # Список подключенных клиентов
        self.clients = []

        # Список сообщений на отправку
        self.messages = []

        # Словарь с именами и соответствующие им сокетами
        self.names = dict()

    def init_socket(self):
        SERVER_LOGGER.info(
            f'Сервер запущен, порт для подключений: {self.port},\n '
            f'Адрес с которого принимаются подключения: {self.addr}.\n '
            f'Если адрес не указан, принимаются соединения с любых адресов.')

        # Готовим сокет
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.addr, self.port))
        transport.settimeout(1)

        # Начинаем слушать сокет.
        self.sock = transport
        self.sock.listen()

    def main_loop(self):
        # Инициализация Сокета
        self.init_socket()

        # Основной цикл программы сервера
        while True:
            # Ждём подключения, если таймаут вышел, ловим исключение.
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                SERVER_LOGGER.info(f'Установлено соедение с ПК {client_address}')
                self.clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []

            # Проверка на наличие ждущих клиентов
            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            # Прием сообщения (если ошибка, то исключаем клиента).
            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process_client_message(get_message(client_with_message), client_with_message)
                    except:
                        SERVER_LOGGER.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        self.clients.remove(client_with_message)

            # Если есть сообщения, обрабатываем каждое.
            for message in self.messages:
                try:
                    self.process_message(message, send_data_lst)
                except Exception as e:
                    SERVER_LOGGER.info(f'Связь с клиентом с именем '
                                f'{message[DESTINATION]} была потеряна, '
                                f' ошибка {e}')
                    self.clients.remove(self.names[message[DESTINATION]])
                    del self.names[message[DESTINATION]]
            self.messages.clear()

    # Функция адресной отправки сообщения определенному клиенту. Принимает словарь сообщение, список зарег. пользователей
    # слушающие сокеты. Ничего обратно не возвращает
    def process_message(self, message, listen_socks):
        if message[DESTINATION] in self.names and self.names[message[DESTINATION]] in listen_socks:
            send_message(self.names[message[DESTINATION]], message)
            SERVER_LOGGER.info(
                f'Пользователю {message[DESTINATION]} отправлено сообщение от пользователя {message[SENDER]}')
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            SERVER_LOGGER.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере. Отправка сообщения невозможна')

    # Функция process_client_message является обработчиком сообщений от клиентов
    # Принимает сообщение от клиента (словарь), проверяет его валидность, возвращает ответ для клиента (также словарь)
    def process_client_message(self, message, client):
        SERVER_LOGGER.debug(f'Выполнение разбора сообщения от клиента: {message}')
        # Проверка: если сообщение о присутствии, то принимаем его и отвечаем
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message:
            # Регистрируем пользователя, если его нет. Если он есть, то отправляем ответ и завершаем соединение
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято. Выберите другое'
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        # Проверка: если это текстовое сообщение с содержанием, то добавляем его в очередь сообщений (ответ не требуется)
        elif ACTION in message and message[ACTION] == MESSAGE and \
                TIME in message and MESSAGE_TEXT in message and \
                DESTINATION in message and SENDER in message:
            self.messages.append(message)
            return
        elif ACTION in message and message[ACTION] == EXIT and \
                ACCOUNT_NAME in message:
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            return
        # Если ничего не подошло, то выводим ошибку 400 "Bad request"
        else:
            response = RESPONSE_400
            response[ERROR] = 'Некорретный запрос'
            send_message(client, response)
            return

def main():
    # Загрузка параметров командной строки, если нет параметров,
    # то задаём значения по умолчанию.
    listen_address, listen_port = create_arg_parser()

    # Создание экземпляра класса - сервера.
    server = Server(listen_address, listen_port)
    server.main_loop()


if __name__ == '__main__':
    main()
