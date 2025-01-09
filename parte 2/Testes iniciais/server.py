import socket
import threading

def start_server( host = '127.0.0.1', port = 5000):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((host, port))
    serverSocket.listen(5)
    print(f"Servidor iniciado em: {host} {port}")   

    while True:
        (clientSocket, clientAdress) = serverSocket.accept()
        thread = threading.Thread(target=handleClient, args=(clientSocket, clientAdress,))
        thread.start
        print(f"Número de conexões ativas: {threading.active_count() - 1}")   

def handleClient(clientSocket, clientAdress):
        print(f"Cliente conectado: {clientAdress}")     
        while True:
             try:
                  message = clientSocket.recv(1024).decode('utf-8') 
                  if not message:
                       break
                  print(f"Mensagem de {clientAdress}: {message}")
                  clientSocket.send(f"Echo: {message}".encode('utf-8'))
             except:
                  print(f"Erro com o cliente: {clientAdress}")
                  break
        clientSocket.close()
        print(f"Cliente desconectado: {clientAdress}")
                  

if __name__ == "__main__":
    start_server()




