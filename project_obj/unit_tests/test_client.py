'''Unit-тесты для клиента (client.py)'''

import sys
import os
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from initial_project.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE
from client import create_presence, server_answer

'''Создаем класс с тестами'''
class TestClass(unittest.TestCase):
    '''Тест №1: тестируем корректный запрос'''
    def test_def_presence(self):
        test = create_presence()
        # приравниваем время, иначе тест никогда не будет пройден
        test[TIME] = 1.1
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}})

    '''Тест №2: тестируем корректный разбор ответа 200 (ОК)'''
    def test_answer_200(self):
        self.assertEqual(server_answer({RESPONSE: 200}), 'The HTTP 200 OK')

    '''Тест №3: тестируем корректный разбор ответа 400 (Bad request)'''
    def test_answer_400(self):
        self.assertEqual(server_answer({RESPONSE: 400, ERROR: 'Bad request'}), '400 : Bad request')

    '''Тест №4: тестируем исключение без поля RESPONSE'''
    def test_without_response(self):
        self.assertRaises(ValueError, server_answer, {ERROR: 'Bad request'})


if __name__ == '__maim__':
    unittest.main()