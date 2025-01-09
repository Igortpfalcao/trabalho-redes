import socket

def start_server( host = '127.0.0.1', port = 5000):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind(host, port)
    serverSocket.listen(5)

    while True:
        (clientSocket, clientAdress) = serverSocket.accept()

        while True:
            try:
                message = clientSocket.recv(1024).decode('utf-8')
                if not message:
                    print("Cliente desconectado")
                    break
                print(f"Mensagem Recebida: {message}")
                clientSocket.send(f"Echo: {message}".encode('utf-8'))
            except Exception as e:
                print(f"Erro: {e}")
                break
        clientSocket.close()

if __name__ == "__main__":
    start_server()




