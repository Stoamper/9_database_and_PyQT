"""Тесты нескольких функций с первого курса Python через assert"""


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


'''Тест №1: проверяем правильность работы функции вывода разделителей'''


def test_sep():
    assert print_sep(2) == '--', 'Неверное количество разделителей'


'''Тест №2: проверяем правильность работы функции вывода разделителей'''


def test_hello():
    assert hello('Alex') == 'Hello, Alex', 'Неверный вывод функции'


'''Тест №3: проверяем правильность работы функции фильтрации списка'''


def test_filter():
    assert my_filter([1, 2, 3, 4]) == [2, 4], 'Неверное выполнение фильтрации списка'


test_sep()
test_hello()
test_filter()
