import socket
import threading
import logging
import hashlib
import json
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64

KEY = b'Sixteen byte key'

def encryptMessage(message):
    cipher = AES.new(KEY, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(message.encode(), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    ct = base64.b64encode(ct_bytes).decode('utf-8')
    return iv, ct

def decryptMessage(iv, ct):
    iv = base64.b64decode(iv)
    ct = base64.b64decode(ct)
    cipher = AES.new(KEY, AES.MODE_CBC, iv=iv)
    decrypted = unpad(cipher.decrypt(ct), AES.block_size).decode('utf-8')
    return decrypted

logging.basicConfig(filename= 'server.log', level = logging.INFO, format= '%(asctime)s - %(message)s')

def logEvent(message):
    logging.info(message)

usersFile = 'users.json'
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

def handleClient(client_socket, client_address):
    try:
        username = None
        while True:
            encryptedRequest = client_socket.recv(1024).decode('utf-8').strip()
            logEvent(encryptedRequest)
            if encryptedRequest.split()[0] == "GET_USERS":
                logEvent("entrou aqui")
                logEvent
                username = args[0]
                response = loadUsers()
                usernames = list(response.keys())
                usernamesString = " ".join(usernames)
                response = usernamesString
                logEvent(response)
                client_socket.sendall(response.encode('utf-8'))
            else:
                if not encryptedRequest:
                    logEvent(f"Cliente desconectado: {client_address}")
                    break
                iv, ct = encryptedRequest.split()
                decryptedRequest = decryptMessage(iv, ct)
                request = decryptedRequest.split()
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

                elif command == "MESSAGE":
                    if len(args) >= 3:
                        sender = args[0]
                        recipient = args[1]
                        content = " ".join(args[2:])
                        try:
                            client_socket.sendall(f"Você: {content}".encode('utf-8'))  
                        except Exception as e:
                            logEvent(f"Erro ao enviar confirmação ao remetente {sender}: {e}")

                        if recipient in connectedClients:
                            recipientSocket = connectedClients[recipient]
                            try:
                                recipientSocket.sendall(f"Nova mensagem de {sender}: {content}".encode('utf-8'))
                            except Exception as e:
                                logEvent(f"Erro ao enviar mensagem para {recipient}: {e}")
                        else:

                            logEvent(f"Destinatário offline: {recipient}")
                    else:
                        response = "Erro: Argumentos insuficientes para enviar mensagem"
                iv, ct = encryptMessage(response)
                client_socket.sendall(f"{iv} {ct}".encode('utf-8'))

    except Exception as e:
        logEvent(f"Erro com o cliente {client_address}: {e}")
    finally:
        if username in connectedClients:
            del connectedClients[username]
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
            thread = threading.Thread(target=handleClient, args=(client_socket, client_address))
            thread.start()
            logEvent(f"Conexões ativas: {threading.active_count() - 1}")


    except Exception as e:
        logEvent(f"Erro no servidor: {e}")
    finally:
        server_socket.close()
        logEvent("Servidor encerrado.")

if __name__ == "__main__":
    start_server()