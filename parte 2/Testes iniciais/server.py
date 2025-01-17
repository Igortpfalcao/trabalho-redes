import socket
import threading
import logging
import hashlib
import json
import os

logging.basicConfig(filename= 'server.log', level = logging.INFO, format= '%(asctime)s - %(message)s')

def logEvent(message):
    logging.info(message)

messagesFile = 'messages.json'
usersFile = 'users.json'
connectedClients = {}

def loadMessages():
    if not os.path.exists(messagesFile):
        return {}
    with open(messagesFile, 'r') as file:
        return json.load(file)
    
def saveMessages(messages):
    with open(messagesFile, 'w') as file:
        json.dump(messages, file)

messages = loadMessages()

def saveMessage(sender, recipient, content):
    if recipient not in messages:
        messages[recipient] = []
    messages[recipient].append({"sender": sender, "content": content})
    saveMessages(messages)

def getMessagesForUser(username):
    userMessages = messages.get(username, [])
    saveMessages(messages)
    return userMessages

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
            
            elif command == "GET_MESSAGES":
                if len(args) == 1:
                    username = args[0]
                    userMessages = getMessagesForUser(username)
                    response = json.dumps(userMessages)
                else:
                    response = "Erro: Número de argumentos inválido para este processo."

            elif command == "GET_USERS":
                if len(args) == 1:
                    username = args[0]
                    response = loadUsers()
                    usernames = list(response.keys())
                    usernamesString = " ".join(usernames)
                    response = usernamesString
                else:
                    response = "Erro: Número de argumentos inválidos para este processo"

            elif command == "MESSAGE":
                if len(args) >= 3:
                    sender = args[0]
                    recipient = args[1]
                    content = " ".join(args[2:])
                    saveMessage(sender, recipient, content) 
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
            
            client_socket.sendall(response.encode('utf-8'))

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