import socket

def start_client( host = '127.0.0.1', port = 5000):
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((host, port))
    print(f"Conectado ao servidor: host: {host}, porta: {port}")

    try:
        while True:
            message = input(f"Digite uma mensagem (ou \"sair\" para encerrar): ")
            if message.lower() == 'sair':
                break
            clientSocket.send(message.encode('utf-8'))
            response = clientSocket.recv(1024).decode('utf-8')
            print(f"Resposta do servidor: {response}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        clientSocket.close()
        print("Conexão encerrada")

if __name__ == '__main__':
    start_client()
