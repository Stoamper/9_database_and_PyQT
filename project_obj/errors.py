''' Описание ошибок, которые добавляем в server.py и client.py'''

''' Ошибка по некорректным данным, полученным от сокета '''


class IncorrectDataRecievedError(Exception):
    def __str__(self):
        return 'Ошибка: получено некорректное сообщение от удаленного компьютера'


''' Ошибка, если аргумент функции не является словарем '''


class NonDictInputError(Exception):
    def __str__(self):
        return 'Ошибка: аргумент функции не является словарем'


''' Ошибка при отсутствии обязательного поля в принятом словаре '''


class ReqFieldMissingError(Exception):
    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'Ошибка: в принятом словаре отсутствует обязательное поле {self.missing_field}'


''' Ошибка если нет соединения с сервером '''


class ServerError(Exception):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text
