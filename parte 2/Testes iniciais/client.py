import socket

def start_client(server_host='127.0.0.1', server_port=5000):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_host, server_port))

    try:
        while True:
            server_message = client_socket.recv(1024).decode()
            if not server_message:
                break
            print(server_message, end="")
            client_input = input()
            client_socket.sendall(client_input.encode())
    except KeyboardInterrupt:
        print("\nEncerrando cliente.")
    finally:
        client_socket.close()

if __name__ == "__main__":
    start_client()
