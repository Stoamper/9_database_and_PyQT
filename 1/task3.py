'''Написать функцию host_range_ping_tab(), возможности которой
основаны на функции из примера 2. Но в данном случае результат
должен быть итоговым по всем ip-адресам, представленным
в табличном формате (использовать модуль tabulate)'''

from tabulate import tabulate
from task2 import host_range_ping

# Функция запроса диапазона ip-адресов, проверки их доступности, вывода результата в табличном виде
def host_range_ping_tab():
    res_dict = host_range_ping(True)
    print()
    print(tabulate([res_dict], headers='keys', tablefmt='grid', stralign='left'))


if __name__ == '__main__':
    host_range_ping_tab()