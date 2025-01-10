import socket
import threading
import logging

logging.basicConfig(filename= 'server.log', level = logging.INFO, format= '%(asctime)s - %(message)s')

def logEvent(message):
    logging.info(message)

def handle_client(client_socket, client_address):
    logEvent(f"Cliente conectado: {client_address}")
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                logEvent(f"Cliente desconectado: {client_address}")
                break
            logEvent(f"Mensagem de {client_address}: {message}")
            client_socket.send(f"Echo: {message}".encode('utf-8'))
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
            thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            thread.start()
            logEvent(f"Conexões ativas: {threading.active_count() - 1}")

    except Exception as e:
        logEvent(f"Erro no servidor: {e}")
    finally:
        server_socket.close()
        logEvent("Servidor encerrado.")

if __name__ == "__main__":
    start_server()