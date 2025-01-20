import socket
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import json
import threading
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
import os

KEY = b'Sixteen byte key'

File_port = 5001

def send_file(recipient, host='127.0.0.1', port=File_port):
    filepath = tk.filedialog.askopenfilename(title="Selecione um arquivo")
    if not filepath:
        messagebox.showinfo("Cancelado", "Nenhum arquivo selecionado.")
        return

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))  

        file_size = os.path.getsize(filepath)
        filename = os.path.basename(filepath)


        metadata = f"{filename}|{file_size}|{recipient}".encode('utf-8')  
        client_socket.sendall(metadata)

        with open(filepath, 'rb') as f:
            while chunk := f.read(1024):
                client_socket.sendall(chunk)

        print(f"Arquivo {filename} enviado para {recipient}.")
    except Exception as e:
        print(f"Erro durante o envio do arquivo: {e}")
    finally:
        client_socket.close()

def receiveFile(host='127.0.0.1', port=File_port):
    try:
        file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        file_socket.connect((host, port))

        metadata = file_socket.recv(1024).decode('utf-8')
        filename, file_size = metadata.split('|')
        file_size = int(file_size)

        save_path = tk.filedialog.asksaveasfilename(initialfile=filename, title="Salvar arquivo")
        if not save_path:
            messagebox.showinfo("Cancelado", "Recebimento do arquivo foi cancelado.")
            file_socket.close()
            return

        with open(save_path, 'wb') as f:
            received = 0
            while received < file_size:
                chunk = file_socket.recv(1024)
                if not chunk:
                    break
                f.write(chunk)
                received += len(chunk)

        messagebox.showinfo("Sucesso", f"Arquivo {filename} recebido com sucesso e salvo em {save_path}.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao receber arquivo: {e}")
    finally:
        file_socket.close()

def startFileReception():
    threading.Thread(target=receiveFile, daemon=True).start()

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

root = tk.Tk()  
root.title("Cliente - Login")

try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1' , 5000))
except Exception as e:
    messagebox.showerror("Erro", f"Não foi possível conectar ao servidor: {e}")
    root.destroy()

def sendToServerDecrypted(data):
    try:
        client_socket.sendall(data.encode("utf-8"))
        response = client_socket.recv(1024).decode('utf-8')
        return response
    except Exception as e:
        return f"Erro ao conectar com o servidor: {e}"

def sendToServer(data):
    iv, ct = encryptMessage(data)
    try:
        client_socket.sendall(f"{iv} {ct}".encode("utf-8"))
        response = client_socket.recv(1024).decode('utf-8')
        iv, ct = response.split()
        decryptedResponse = decryptMessage(iv, ct)
        return decryptedResponse
    except Exception as e:
        return f"Erro ao conectar com o servidor: {e}"

def login():
    username = username_entry.get()
    password = password_entry.get()
    if not username or not password:
        messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
        return


    response = sendToServer(f"LOGIN {username} {password}")
    if ('Login bem sucedido') in response:
        messagebox.showinfo("Sucesso", "Login realizado com sucesso")
        root.destroy()
        openChatWindow(username)
    else:
        messagebox.showerror("Erro", "Login ou senha incorreto, tente novamente.")

def register(): 
    username = username_entry.get()
    password = password_entry.get()
    if not username or not password:
        messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
        return
    
    response = sendToServer(f'REGISTER {username} {password}')
    if "Usuário cadastrado" in response:
        messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso")
    else:
        messagebox.showerror("Erro", "O nome de usuário já está em uso.")

frame = tk.Frame(root)
frame.pack(pady=20, padx=20)


tk.Label(frame, text="Nome de usuário:").grid(row=0, column=0, sticky="e")
username_entry = tk.Entry(frame)
username_entry.grid(row=0, column=1)

tk.Label(frame, text="Senha:").grid(row=1, column=0, sticky="e")
password_entry = tk.Entry(frame, show="*")
password_entry.grid(row=1, column=1)


login_button = tk.Button(frame, text="Login", command=login)
login_button.grid(row=2, column=0, pady=10)

register_button = tk.Button(frame, text="Registrar", command=register)
register_button.grid(row=2, column=1, pady=10)

def listenForMessages(chatText):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                if message.startswith("GAMBIARRA12345"):
                    continue
                chatText.after(0, lambda: updateChatText(chatText, message))
        except Exception as e:
            print(f"Erro ao ouvir mensagens: {e}")
            break  

def updateChatText(chatText, message):
    chatText.configure(state='normal')
    chatText.insert('end', message + '\n')
    chatText.configure(state='disabled')

def sendMessage(sender, selectedUser, messageEntry):
    message = messageEntry.get().strip()

    if not selectedUser or not message:
        messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
        return

    def send_message_thread():
        sendToServer(f"MESSAGE {sender} {selectedUser} {message}")
        messageEntry.delete(0, 'end')   

    threading.Thread(target=send_message_thread, daemon=True).start()


def updateUserList(userListbox, username):
    def updateUserListThread():
        response = sendToServerDecrypted(f"GET_USERS {username}")
        try:
            users = response.split(" ")
            userListbox.delete(0, 'end')  
            for user in users:
                if user != username and user != "GAMBIARRA12345":
                    userListbox.insert('end', user)
        except:
            messagebox.showerror("Erro", f"Resposta inválida do servidor: {response}")
    threading.Thread(target=updateUserListThread,daemon=True).start()
    
def cleanChatBox(chatText):
    chatText.configure(state='normal')
    chatText.delete('1.0', 'end')
    chatText.configure(state='disabled')
  

def openChatWindow(username):
    chatWindow = tk.Tk()
    chatWindow.title(f"Chat - {username}")
    chatWindow.geometry("500x500")

    userFrame = tk.Frame(chatWindow, width=150)
    userFrame.pack(side='left', fill='y')

    userListBox = tk.Listbox(userFrame)
    userListBox.pack(fill='both', expand=True)

    tk.Button(userFrame, text="Atualizar", command=lambda: updateUserList(userListBox, username)).pack(pady=5)

    chatFrame = tk.Frame(chatWindow)
    chatFrame.pack(side='right', fill='both', expand=True)
    
    recipient_label = tk.Label(chatFrame, text="Conversa com:")
    recipient_label.pack(pady=(10, 0))
    
    chatText = tk.Text(chatFrame, state='disabled', wrap='word', bg='lightgray', fg='black')
    chatText.pack(padx=10, pady=10, fill='both', expand=True)
    
    messageEntry = tk.Entry(chatFrame)
    messageEntry.pack(padx=10, pady=(0, 10), fill='x', side='left', expand=True)
    
    sendButton = tk.Button(chatFrame, text="Enviar", state='disabled')
    sendButton.pack(padx=10, pady=(0, 10), side='right')

    sendFileButton = tk.Button(chatFrame, text="Enviar Arquivo", command=send_file)
    sendFileButton.pack(padx=10, pady=(0, 10), side='right')

    receiveFileButton = tk.Button(chatFrame, text="Receber Arquivo", command=startFileReception)
    receiveFileButton.pack(padx=10, pady=(0, 10), side='right')
    
    def onUserSelect(event):
        try:
            selectedUser = userListBox.get(userListBox.curselection())
            recipient_label.config(text=f"Conversa com: {selectedUser}")
            sendButton.config(state='normal', command=lambda: sendMessage(username, selectedUser, messageEntry))
            sendFileButton.config(state='normal', command=lambda: send_file(selectedUser))
            threading.Thread(target=cleanChatBox, args=(chatText,) , daemon=True).start()     
        except tk.TclError:
            pass

    userListBox.bind('<<ListboxSelect>>', onUserSelect)

    updateUserList(userListBox, username)
    
    threading.Thread(target=listenForMessages, args=(chatText,) , daemon=True).start()

    chatWindow.mainloop()

root.mainloop()
