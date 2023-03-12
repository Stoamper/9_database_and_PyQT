'''Утилиты в проекте'''
'''Испольуются для осуществления вспомогательных операций'''

import json
import sys
from initial_project.variables import MAX_MESSAGE_LENGTH, ENCODING
from errors import IncorrectDataRecievedError, NonDictInputError
from decorators import log_dec
sys.path.append('../')


'''Утилита get_message. Назначение: прием и декодирование сообщения'''
'''Принимает байты, возвращает словарь. Если на входе не байты, то ошибка ValueError'''
@log_dec
def get_message(client):
    encoded_response = client.recv(MAX_MESSAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        else:
            raise IncorrectDataRecievedError
    else:
        raise IncorrectDataRecievedError


'''Утилита send_message. Назначение: кодирование и отправка сообщения'''
'''Принимает словарь, отправляет его'''
@log_dec
def send_message(sock, message):
    if not isinstance(message, dict):
        raise NonDictInputError
    json_message = json.dumps(message)
    encoded_message = json_message.encode(ENCODING)
    sock.send(encoded_message)


