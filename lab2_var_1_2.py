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
    command = input("Введите команду (set_root_folder, get_file_info or q): ")
    client_socket.send(command.encode())

    # Обработка команды 'set_root_folder' и 'q'
    if command == 'set_root_folder':
        new_folder = input("Введите новую корневую папку: ")
        client_socket.send(new_folder.encode())
        print(client_socket.recv(2048).decode())

    elif command == 'get_file_info':
        response_length_data = client_socket.recv(4)  # Получаем длину JSON данных от сервера
        response_length = struct.unpack('I', response_length_data)[0]  # Распаковываем данные длины

        response = b""
        while len(response) < response_length:
            data = client_socket.recv(min(4096, response_length - len(response)))
            response += data

        files_info = json.loads(response.decode())
        for file_path, file_info in files_info.items():
            print(file_path, file_info)

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
