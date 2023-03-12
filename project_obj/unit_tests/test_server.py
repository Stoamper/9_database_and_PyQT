'''Unit-тесты для сервера (server.py)'''

import sys
import os
import unittest
sys.path.append(os.path.join(os.getcwd(), '..'))
from initial_project.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE
from server import process_client_message

'''Создаем класс с тестами'''
class TestServer(unittest.TestCase):
    '''В сервере есть только одна функция для тестирования'''
    err_dict = {
        RESPONSE: 400,
        ERROR: 'Bad request'
    }
    ok_dict = {RESPONSE: 200}

    '''Тест №1: тестируем на отсутствие действия (нет действия - ошибка)'''
    def test_without_action(self):
        self.assertEqual(process_client_message(
            {TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)

    '''Тест №2: тестируем по неизвестному действию'''
    def test_unknown_action(self):
        self.assertEqual(process_client_message(
            {ACTION: 'Unknown', TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)

    '''Тест №3: тестируем на предмет содержания штампа времени (нет штампа - ошибка)'''
    def test_without_time(self):
        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)

    '''Тест №4: тестируем отсутствие пользователя (нет пользователя - ошибка)'''
    def test_without_user(self):
        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, TIME: '1.1'}), self.err_dict)

    '''Тест №5: тестируем на предмет неизвестного пользователя'''
    def test_unknown_user(self):
        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest_1'}}), self.err_dict)

    '''Тест №6: тестируем на корректность запроса'''
    def test_ok_request(self):
        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}), self.ok_dict)


if __name__ == '__main__':
    unittest.main()