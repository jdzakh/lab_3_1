import socket    #предоставляет возможность работать с сетевыми сокетами, что позволяет создавать клиент-серверные сетевые приложения
import threading     #предоставляет инструменты для работы с потоками (threads) в многопоточных программах
import json
import os
import struct
from datetime import datetime



# класс для представления узлов бинарного дерева
class Node:
    def __init__(self, key):
        self.key = key  # значение, хранимое в данном узле.
        self.left = None  # ссылка на левого потомка узла
        self.right = None  # ссылка на правого потомка узла


def insert_node(root, key):  # функция для вставки узла в бинарное дерево
    if root is None:
        return Node(
            key)  # если корень пуст, создается новый узел со значением key, и этот узел становится корнем поддерева
    if key < root.key:
        root.left = insert_node(root.left, key)  # рекурсивно вставляем новый узел в левую ветвь дерева
    else:
        root.right = insert_node(root.right, key)
    return root  # корень поддерева


def inorder_traversal(root, result):  # обход дерева по порядку
    if root:  # если узел существует
        inorder_traversal(root.left, result)  # обходим все узлы левого поддерева перед текущим узлом
        result.append(root.key)  # добавление значения текущего узла в итоговый список
        inorder_traversal(root.right, result)


def create_binary_tree(numbers):  # функция для создания бинарного дерева из списка чисел
    root = None  # пустой корень в начале
    for num in numbers:
        root = insert_node(root, num)  # вставка числа в бинарное дерево
    result = []
    inorder_traversal(root, result)  # построение дерева по списку чисел
    return result


def get_file_info(path):
    if os.path.isfile(path):  # Проверяем, является ли путь файлом
        file_info = {  # Создаем словарь с информацией о файле
            'name': os.path.basename(path),  # Получаем имя файла
            'size': os.path.getsize(path),  # Получаем размер файла
            'modified': os.path.getmtime(path)  # Получаем время последнего изменения
        }
        return file_info
    elif os.path.isdir(path):  # Если путь является директорией
        dir_info = {  # Создаем словарь с информацией о директории
            'name': os.path.basename(path),  # Получаем имя директории
            'type': 'directory',
            'contents': []  # Создаем пустой список для содержимого директории
        }
        for filename in os.listdir(path):  # Итерируем по содержимому директории
            file_path = os.path.join(path, filename)  # Получаем полный путь к файлу
            file_info = get_file_info(file_path)  # Рекурсивно вызываем функцию для файла внутри директории
            dir_info['contents'].append(file_info)  # Добавляем информацию о файле в содержимое директории
        return dir_info

# Функция для сохранения информации о файлах и папках в формате JSON
def save_to_json(file_info, output_dir):
    with open(os.path.join(output_dir, 'files_info.json'), 'w', encoding='utf-8') as file:
        json.dump(file_info, file, indent=4, ensure_ascii=False)

current_path = os.getcwd()
output_dir = current_path
files_info = get_file_info(current_path)
save_to_json(files_info, output_dir)
def handle_client(client_socket, addr):
    output_dir = current_path
    current_time = datetime.now()
    folder_name = current_time.strftime("%d-%m-%Y_%H-%M-%S")
    result = []
    while True:
        try:
            command = client_socket.recv(1024).decode()
        except ConnectionResetError:
            print("Соединение с клиентом разорвано.")
            break

        if command == "send_numbers":
            numbers_string = client_socket.recv(1024).decode()
            numbers = [int(num) for num in numbers_string.split()]

            current_time = datetime.now()  # получаем текущую дату и время
            folder_name = current_time.strftime("%d-%m-%Y_%H-%M-%S")  # форматируем название папки

            os.makedirs(folder_name)  # создаем новую папку с текущим временем

            root = None  # для начала нового бинарного дерева
            for i, num in enumerate(numbers, 1):
                root = insert_node(root,
                                   num)  # на каждой итерации вставляем новый узел с ключом num в текущее бинарное дерево, начиная с корня root
                result = []
                inorder_traversal(root, result)  # построение дерева по списку чисел

                file_name = f"{i}.json"
                with open(os.path.join(folder_name, file_name), "w") as file:
                    json.dump(result, file)  # сохраняем файл в формате json

            response = json.dumps(result)  # преобразует результат в формат json
            client_socket.send(response.encode())  # используется для отправки этих байтов через сетевое соединение


        elif command == "request_file":
            launch_number = client_socket.recv(1024).decode()
            tree_number = client_socket.recv(1024).decode()

            file_name = f"{tree_number}.json"  # создает имя файла, используя значение tree_number и расширение файла .json
            file_path = os.path.join(folder_name, file_name)  # создает полный путь к файлу

            with open(file_path, "r") as file:  # открывает файл по указанному пути для чтения
                data = file.read()
                client_socket.send(data.encode())

        if command == 'set_root_folder':
            # Установка новой корневой директории
            new_folder = client_socket.recv(2048).decode()
            if os.path.exists(new_folder):  # Проверяем существование папки
                os.chdir(new_folder)  # Меняем рабочую директорию
                output_dir = new_folder
                files_info = get_file_info(new_folder)
                save_to_json(files_info, output_dir)
                client_socket.send(f"Корневая папка установлена на {new_folder}".encode())  # Отправляем ответ клиенту
            else:
                client_socket.send("Ошибка: Папка не существует.".encode())  # Отправляем ошибку клиенту

        # Отправка JSON-содержимого информации о файлах и папках клиенту
        # Получение JSON данных о файлах и директориях от клиента
        elif command == 'get_file_info':
            with open(os.path.join(output_dir, 'files_info.json'), 'r', encoding='utf-8') as file:
                files_info = json.load(file)
                json_data = json.dumps(files_info, ensure_ascii=False)
                json_data_bytes = json_data.encode()  # Преобразуем JSON данные в байты
                json_data_length = len(json_data_bytes)

                # Отправляем длину JSON данных клиенту
                client_socket.send(struct.pack('I', json_data_length))

                # Отправляем JSON данные клиенту фрагментами
                sent = 0
                while sent < json_data_length:
                    remaining = json_data_length - sent
                    send_size = min(4096, remaining)
                    sent += client_socket.send(json_data_bytes[sent:sent + send_size])
# Создание TCP-сервера
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    #создание нового объекта сокета для работы с сетью
                                                                     #первый аргумент socket.AF_INET указывает на используемый адресный семейство,
                                                                     #в данном случае IPv4. Второй аргумент socket.SOCK_STREAM указывает на тип сокета,
                                                                     #в данном случае потоковый сокет (TCP)
server_socket.bind(('127.0.0.1', 12345))     #привязка сокета к заданному хосту и порту
server_socket.listen(5)    #используется для установки сокета в режим прослушивания входящих подключений
                           #аргумент 5 обозначает максимальную длину очереди ожидающих подключений.
                           #это значит, что сервер будет принимать до 5 запросов на соединение в ожидании обработки
print("Запуск сервера")

while True:
    client_socket, addr = server_socket.accept()    #эта строка принимает входящее соединение от клиента и создает новый сокет client_socket
                                                    #для взаимодействия с этим клиентом,а также сохраняет адрес клиента в переменной addr
    client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))    #создается новый объект типа Thread из модуля threading.
                                                                                          #этот объект предназначен для выполнения функции handle_client в отдельном потоке
    client_thread.start()    #запуск нового потока

server_socket.close()    #используется для закрытия сокета после завершения работы с ним
print("Остановка сервера")
