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
connectedClients = {}

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
        logEvent(f"Usuário não registrado (usuário já existente): {username}")
        return False
    hashedPassword = hashlib.sha512(password.encode()).hexdigest()
    users[username] = hashedPassword  
    saveUsers(users)
    logEvent(f"Novo usuário registrado: {username}")
    return True 

def authenticateUser(username, password):
    users = loadUsers()
    hashedPassword = hashlib.sha512(password.encode()).hexdigest()
    return username in users and users[username] == hashedPassword

def handleLoginAndRegister(client_socket, client_address):
    try:
        while True:
            request = client_socket.recv(1024).decode('utf-8').strip()
            if not request:
                logEvent(f"Cliente desconectado: {client_address}")
                break

            request = request.split()
            command = request[0]
            args = request[1:]

            if command == "LOGIN":
                if len(args) == 2:
                    username, password = args
                    if authenticateUser(username, password):
                        response = 'Login bem sucedido'
                        logEvent(f"Novo login do usuário {username} a partir do endereço {client_address}")
                        connectedClients[username] = client_socket
                    else:
                        response = "Erro: Login ou senha incorretos"
                        logEvent(f"tentativa falha de login a partir do endereço {client_address}") 
                else:
                    response = "Erro: Número de argumentos inválido para login"

            elif command == "REGISTER":
                if len(args) == 2:
                    username, password = args
                    if registerUser(username, password):
                        response = "Usuário cadastrado com sucesso."
                    else:
                        response = "Erro: Usuário já está em uso"
                else:
                    response = "Erro: Número de argumentos inválido para login"
            
            client_socket.sendall(response.encode('utf-8'))

    except Exception as e:
        logEvent(f"Erro com o cliente {client_address}: {e}")
    finally:
        client_socket.close()

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
            thread = threading.Thread(target=handleLoginAndRegister, args=(client_socket, client_address))
            thread.start()
            logEvent(f"Conexões ativas: {threading.active_count() - 1}")

    except Exception as e:
        logEvent(f"Erro no servidor: {e}")
    finally:
        server_socket.close()
        logEvent("Servidor encerrado.")

if __name__ == "__main__":
    start_server()
