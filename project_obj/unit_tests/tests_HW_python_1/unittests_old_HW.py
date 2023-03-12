"""Unit-тесты нескольких функций с первого курса Python"""

import unittest


# 1. Функция простой разделитель

def print_sep(n):
    return '-' * n


# 2. Функция приветствия пользователя

def hello(who):
    return f'Hello, {who}'


# 3. Функция фильтрации списка чисел

def my_filter(numbers):
    result = []
    for number in numbers:
        if number % 2 == 0:
            result.append(number)
    return result


'''Создаем тестовый класс'''


class TestTranslate(unittest.TestCase):
    """Тест №1: тест вывода верного количества разделителей"""

    def test_sep(self):
        self.assertEqual(print_sep(2), '--')

    """Тест №2: тест приветствия пользователя"""

    def test_hello(self):
        self.assertEqual(hello('Vasya'), 'Hello, Vasya')

    """Тест №3: тест правильной фильтрации списка"""

    def test_filter(self):
        numbers = [1, 2, 3, 4, 5, 6]
        self.assertEqual(my_filter(numbers), [2, 4, 6])

    """Тест №4: тест вхождения числа в список после его фильтрации"""

    def test_in(self):
        numbers = [1, 2, 3, 4, 5, 6]
        self.assertIn(2, my_filter(numbers))


if __name__ == '__main__':
    unittest.main()
