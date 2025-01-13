import socket
import threading
import logging
import hashlib
import json
import os

logging.basicConfig(filename= 'server.log', level = logging.INFO, format= '%(asctime)s - %(message)s')

def logEvent(message):
    logging.info(message)

usersFile = 'users.json'
roomsFIle = 'salas.json'

def loadUsers():
    if not os.path.exists(usersFile ):
        return {}
    with open(usersFile, 'r') as file:
        return json.load(file)

def saveUsers(users):
    with open(usersFile, 'w') as file:
        json.dump(users, file)

def registerUser(username, password):
    users = loadUsers()
    if username in users:
        return False, "Login já existe"
    hashedPassword = hashlib.sha512(password.encode()).hexdigest()
    users[username] = hashedPassword  
    saveUsers(users)
    return True, "Usuário cadastrado com sucesso."  

def authenticateUser(username, password):
    users = loadUsers()
    hashedPassword = hashlib.sha512(password.encode()).hexdigest()
    return username in users and users[username] == hashedPassword

def loadRooms(roomsFIle):
    


def broadcastChat(client_socket, client_address):


def handle_client(client_socket, client_address, login):
    logEvent(f"Cliente conectado: {client_address}")
    try: 
        while True:
            client_socket.send(b"Você está conectado, por favor escolha uma opção\n\n1: Chat broadcast\n2: chat privado\n\n")
            option = client_socket.recv(1024).decode().strip()
            if option == "1":
                
            elif option == "2":

            else:
                client_socket.sendall(b"Credencial invalida, tente novamente")
                logEvent(f"Tentativa mal sucedida ao tratar o cliente {Login}")
    except Exception as e:
            logEvent(f"Erro ao lidar com o cliente {client_address}: {e}")


def boasVindas(client_socket, client_address):
    authenticated = False

    while not authenticated:
        try:
            client_socket.sendall(b"Boas vindas! Escolha uma opcao: \n1. Login\n2. Registrar\nEscolha: ")
            option = client_socket.recv(1024).decode().strip()

            if option == "1":
                client_socket.sendall(b"Login: ")
                username = client_socket.recv(1024).decode().strip()
                client_socket.sendall(b"Senha: ")
                password = client_socket.recv(1024).decode().strip()

                if authenticateUser(username, password):
                    client_socket.sendall(b"Login bem sucedido!\n")
                    logEvent(f"Usuário {username} autenticado de {client_address}")
                    authenticated = True

                else:
                    client_socket.sendall(b"Credencial invalida, tente novamente")
                    logEvent(f"Tentativa de login malsucedido para {username} partindo de {client_address}\n")

            elif option == "2":  
                client_socket.sendall(b"Escolha um nome de usuario: ")
                username = client_socket.recv(1024).decode().strip()
                client_socket.sendall(b"Escolha uma senha: ")
                password = client_socket.recv(1024).decode().strip()

                success, message = registerUser(username, password)
                client_socket.sendall(f"{message}\n".encode())
                logEvent(f"Tentativa de cadastro para {username}: {message}")   
            else:
                client_socket.sendall(b"Opcao invalida, tente novamente")

        except Exception as e:
            logEvent(f"Erro ao lidar com o cliente {client_address}: {e}")
   
    handle_client(client_socket, client_address, username)





def start_server(host='127.0.0.1', port=5000):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(5)
        logEvent(f"Servidor iniciado em {host}:{port}")

        while True:
            logEvent("Aguardando conexões...")
            client_socket, client_address = server_socket.accept()
            logEvent(f"Nova conexão: {client_address}")
            thread = threading.Thread(target=boasVindas, args=(client_socket, client_address))
            thread.start()
            logEvent(f"Conexões ativas: {threading.active_count() - 1}")

    except Exception as e:
        logEvent(f"Erro no servidor: {e}")
    finally:
        server_socket.close()
        logEvent("Servidor encerrado.")

if __name__ == "__main__":
    start_server()
