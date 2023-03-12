'''Программа с декораторами'''

import sys
import logging
import logs.configs.client_log_config
import logs.configs.server_log_config
import traceback
import inspect

# Создадим метод определения модуля, источника запуска
# Метод find() возвращает индекс первого вхождения искомой подстроки
# Если ничего не найдено, то возвращается -1

if sys.argv[0].find('client_logger') == -1:
    # -1, то есть если не клиент, то выбираем сервер
    LOGGER = logging.getLogger('server_logger')
else:
    LOGGER = logging.getLogger('client_logger')

# Реализация декоратора в виде функции
def log_dec(user_function):
    def log_saver(*args, **kwargs):
        # Обертка
        ret = user_function(*args, **kwargs)
        LOGGER.debug(f'Вызвана функция {user_function.__name__} с параметрами {args}, {kwargs}'
                     f'Вызов осуществлен из модуля {user_function.__module__}'
                     f'Вызов модуля осуществен из функции {traceback.format_stack()[0].strip().split()[-1]}'
                     f'Вызов осуществлен из функции {inspect.stack()[1][3]}', stacklevel=2)
        return ret
    return log_saver

