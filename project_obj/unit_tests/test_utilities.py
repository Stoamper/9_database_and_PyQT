"""Unit-тесты для утилит (utilities.py)"""

import sys
import os
import unittest
import json

sys.path.append(os.path.join(os.getcwd(), '..'))
from initial_project.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE, ENCODING
from initial_project.utilities import get_message, send_message

'''Создаем тестовый класс с тестами для отправки и получения'''
'''При создании требует словарь, который будет прогоняться через тестовую функцию'''


class TestSocket:
    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.recieved_message = None

    '''Тест №1: тестируем отправку (корректно кодируем сообщение и сохраняем что должно быть отправлено в сокет'''
    '''message_to_send - то, что отправляем в сокет'''

    def send(self, message_to_send):
        json_test_message = json.dumps(self.test_dict)
        # Кодируем сообщение
        self.encoded_message = json_test_message.encode(ENCODING)
        # Сохраняем то, что должно было отправиться в сокет
        self.recieved_message = message_to_send

    '''Получение данных из сокета'''

    def recv(self, max_len):
        json_test_message = json.dumps(self.test_dict)
        return json_test_message.encode(ENCODING)


'''Создаем тестовый класс, который будет выполнять тестирование'''


class Tests(unittest.TestCase):
    test_dict_send = {
        ACTION: PRESENCE,
        TIME: '111111.111111',
        USER: {
            ACCOUNT_NAME: 'test_user'
        }
    }
    test_dict_recieve_ok = {RESPONSE: 200}
    test_dict_recieve_err = {
        RESPONSE: 400,
        ERROR: 'Bad request'
    }

    '''Тест №1: тестируем корректность работы функции отправки'''
    '''Создаем тестовый сокет и проверяем корректность отправки словаря'''

    def test_send_message(self):
        # Экземпляр тестового словаря хранит сам тестовый словарь
        test_socket = TestSocket(self.test_dict_send)
        # Вызов тестируемой функции (результаты сохраняются в тестовом сокете)
        send_message(test_socket, self.test_dict_send)
        # Проверим корректность кодирования словаря
        # Сравним результат закодированного ранее сообщения и результат тестируемой функции
        self.assertEqual(test_socket.encoded_message, test_socket.recieved_message)
        # Также проверим генерацию исключения в том случае, если на входе оказался не словарь
        with self.assertRaises(Exception):
            send_message(test_socket, test_socket)

    '''Тест №2: тестируем функцию приема сообщения'''

    def test_get_message(self):
        test_socket_ok = TestSocket(self.test_dict_recieve_ok)
        test_socket_err = TestSocket(self.test_dict_recieve_err)
        # Выполяем тест корректной расшифровки словаря без ошибок
        self.assertEqual(get_message(test_socket_ok), self.test_dict_recieve_ok)
        # Выполняем тест корректной расшифровки словаря с ошибкой
        self.assertEqual(get_message(test_socket_err), self.test_dict_recieve_err)


if __name__ == '__main__':
    unittest.main()
