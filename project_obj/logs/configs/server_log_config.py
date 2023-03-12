''' Конфигурация логгера для сервера '''

import sys
import os
import logging
import logging.handlers
from initial_project.variables import LOGGING_LEVEL
sys.path.append('../')

# Создание формировщика логов (formatter)
SERVER_FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

# Создание имени файла, в который будет осуществляться запись лога
FILE_PATH = os.path.dirname(os.path.abspath(os.path.join(__file__, "..")))
FILE_PATH = os.path.join(FILE_PATH, 'logfiles', 'server.log')

# Создание потоков вывода логов
STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(SERVER_FORMATTER)
STREAM_HANDLER.setLevel(logging.DEBUG)
LOG_FILE = logging.handlers.TimedRotatingFileHandler(FILE_PATH, encoding='utf-8', interval=1, when='D', backupCount=1)
LOG_FILE.setFormatter(SERVER_FORMATTER)

# Создание регистратора и его настройка
LOGGER = logging.getLogger('server_logger')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(LOGGING_LEVEL)

# Часть кода для выполнения отладки
if __name__ == '__main__':
    LOGGER.critical('critical error')
    LOGGER.error('error')
    LOGGER.warning('warning')
    LOGGER.info('info')
    LOGGER.debug('debug')
    # print(FILE_PATH)
