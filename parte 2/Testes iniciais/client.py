import socket
import tkinter as tk
from tkinter import messagebox

root = tk.Tk()  
root.title("Cliente - Login")

try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1' , 5000))
except Exception as e:
    messagebox.showerror("Erro", f"Não foi possível conectar ao servidor: {e}")
    root.destroy()

def sendToServer(data):
    try:
        client_socket.sendall(data.encode("utf-8"))
        response = client_socket.recv(1024).decode('utf-8')
        return response
    except Exception as e:
        return f"Erro ao conectar com o servidor: {e}"

def login():
    username = username_entry.get()
    password = password_entry.get()
    if not username or not password:
        messagebox.showerror("Por favor, preencha todos os campos.")
        return

    response = sendToServer(f"LOGIN {username} {password}")
    if ('Login bem sucedido') in response:
        messagebox.showinfo("Login realizado com sucesso")
        #inserir janela de chat
    else:
        messagebox.showerror("Login ou senha incorreto, tente novamente.")

def register(): 
    username = username_entry.get()
    password = password_entry.get()
    if not username or not password:
        messagebox.showerror("Por favor, preencha todos os campos.")
        return
    
    response = sendToServer(f'REGISTER {username} {password}')
    if "Usuário cadastrado" in response:
        messagebox.showinfo("Usuário cadastrado com sucesso")
    else:
        messagebox.showerror("O nome de usuário já está em uso.")

frame = tk.Frame(root)
frame.pack(pady=20, padx=20)

# Campos de entrada
tk.Label(frame, text="Nome de usuário:").grid(row=0, column=0, sticky="e")
username_entry = tk.Entry(frame)
username_entry.grid(row=0, column=1)

tk.Label(frame, text="Senha:").grid(row=1, column=0, sticky="e")
password_entry = tk.Entry(frame, show="*")
password_entry.grid(row=1, column=1)

# Botões
login_button = tk.Button(frame, text="Login", command=login)
login_button.grid(row=2, column=0, pady=10)

register_button = tk.Button(frame, text="Registrar", command=register)
register_button.grid(row=2, column=1, pady=10)

# Iniciar loop da interface
root.mainloop()