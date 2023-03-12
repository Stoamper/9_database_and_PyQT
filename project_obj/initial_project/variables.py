'''Константы в проекте'''
import logging

'''Для удобства редактирования помещаем их в одно место'''

# Порт по умолчанию (для сетевого взаимодействия)
DEFAULT_PORT = 7777
# DEFAULT_PORT = 1000

# IP-адрес по умолчанию (для подключения клиента)
DEFAULT_IP_ADDRESS = '127.0.0.1'

# Максимальная очередь подключений (ограничиваем исходя из имеющихся ресурсов)
MAX_CONNECTIONS = 5

# Максимальная длина сообщения в байтах (чтобы сообщение дошло полностью)
MAX_MESSAGE_LENGTH = 1024

# Кодировка проекта (используем универсальную)
ENCODING = 'utf-8'

# Текущий уровень логирования
LOGGING_LEVEL = logging.DEBUG

# Протокол JIM (основные ключи)
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'sender'
DESTINATION = 'to'

# Прочие ключие в протоколе
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'message_text'
EXIT = 'exit'

# Словари-ответы сервера
RESPONSE_200 = {RESPONSE: 200}
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}
