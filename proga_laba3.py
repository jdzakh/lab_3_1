import socket
import json
import struct

# Устанавливаем хост и порт для соединения
server_address = ('127.0.0.1', 12345)

# Создаем сокет и устанавливаем соединение с сервером
#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# Основной цикл программы для взаимодействия с сервером
while True:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)
    command = input("Введите команду (построение бинарного дерева, запросить файл or q): ")
    client_socket.send(command.encode())


    if command == 'построение бинарного дерева':
        client_socket.send(
            "send_numbers".encode())  # программа отправляет на сервер сообщение "send_numbers", предварительно закодированное в байты для передачи по сети
        numbers_input = input("Введите числа для построения бинарного дерева (разделите пробелом): ")
        client_socket.send(numbers_input.encode())  # веденные числа отправляются на сервер

        response = client_socket.recv(
            1024).decode()  # ожидается ответ от сервера, ответ размером до 1024 байт декодируется его в строку
        print("Результат обхода бинарного дерева:", response)

    elif command == 'запросить файл':

        client_socket.send("request_file".encode())
        launch_number = input("Введите номер запуска программы: ")
        tree_number = input("Введите номер дерева: ")

        client_socket.send(launch_number.encode())
        client_socket.send(tree_number.encode())

        response = b""  # Создаем пустой байтовый объект для хранения ответа от сервера
        while True:
            data = client_socket.recv(4096)  # Получаем данные от сервера
            response += data  # Добавляем полученные данные к ответу
            if len(data) < 4096:  # Проверяем, были ли получены все данные
                break

    elif command == 'q':
        client_socket.close()
        print("Разрыв соединения с сервером")
        s = input("Хотите ли вы подключиться к серверу снова? Напишите да/нет: ")
        if s == "yes":
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # создается новый объект клиентского сокета
            client_socket.connect(server_address)  # устанавливается соединение с сервером, используя адрес server_address
        elif s == "no":
            client_socket.close()  # используется для закрытия сокета после завершения работы с ним.
            # после вызова этого метода, сокет перестает прослушивать входящие соединения
            break
        else:
            print("Вы ввели некорректные данные!")
            client_socket.close()
            break

    else:
        print("Вы ввели некорректную  команду! Попробуйте заново!")