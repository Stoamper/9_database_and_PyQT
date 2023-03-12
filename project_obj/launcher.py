''' Программа-лаунчер для запуска файлов сервера и клиента '''
''' Также предусмотрен выход и закрытие всех окон '''

import subprocess

PROCESS = []

while True:
    ACTION = input('Выберите дальнейшее действие:'
                   'q - выход, s - запуск сервера и клиентов, x - закрыть все окна: ')

    if ACTION == 'q':
        break
    elif ACTION == 's':

        clients_count = int(input('Введите количество тестовых клиентов для запуска: '))
        # Запускаем сервер!
        PROCESS.append(subprocess.Popen('python server_obj.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
        # Запускаем клиентов:
        for i in range(clients_count):
            PROCESS.append(
                subprocess.Popen(f'python client_obj.py -n test{i + 1}', creationflags=subprocess.CREATE_NEW_CONSOLE))
        '''
        PROCESS.append(subprocess.Popen('python server_obj.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
        PROCESS.append(subprocess.Popen('python client_obj.py -n test_user_1', creationflags=subprocess.CREATE_NEW_CONSOLE))
        PROCESS.append(subprocess.Popen('python client_obj.py -n test_user_2', creationflags=subprocess.CREATE_NEW_CONSOLE))
        '''
    elif ACTION == 'x':
        while PROCESS:
            VICTIM = PROCESS.pop()
            VICTIM.kill()