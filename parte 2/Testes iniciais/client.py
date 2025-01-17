import socket
import tkinter as tk
from tkinter import messagebox
import json
import threading

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
                chatText.after(0, lambda: updateChatText(chatText, message))
        except Exception as e:
            print(f"Erro ao ouvir mensagens: {e}")
            break  

def updateChatText(chatText, message):
    chatText.configure(state='normal')
    chatText.insert('end', message + '\n')
    chatText.configure(state='disabled')

def sendMessage(sender, recipientEntry, messageEntry):
    recipient = recipientEntry.get().strip()
    message = messageEntry.get().strip()

    if not recipient or not message:
        messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
        return

    def send_message_thread():
        sendToServer(f"MESSAGE {sender} {recipient} {message}")
        messageEntry.delete(0, 'end')

    threading.Thread(target=send_message_thread, daemon=True).start()

def loadPreviousMessages(username, chat_text):
    response = sendToServer(f"GET_MESSAGES {username}")
    if response.strip() == "[]":  
        messagebox.showinfo("Informação", "Nenhuma mensagem encontrada.")
        return
    
    try:
        messages = json.loads(response)  
        chat_text.configure(state='normal')
        for message in messages:
            chat_text.insert('end', f"{message['sender']}: {message['content']}\n")
        chat_text.configure(state='disabled')
    except json.JSONDecodeError:
        messagebox.showerror("Erro", f"Resposta do servidor inválida: {response}")

def listChats(username):
    response = sendToServer(f"LIST_CHATS {username}")
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        messagebox.showerror("Erro", f"Resposta do servidor inválida: {response}")
        return []
    
def openChatWindow(username):
    chatWindow = tk.Tk()
    chatWindow.title(f"Chat - {username}")
    chatWindow.geometry("400x400")
    
    chatListFrame = tk.Frame(chatWindow)
    chatListFrame.pack(side='left', fill='y', padx=10, pady=10)
    chatListLabel = tk.Label(chatListFrame, text="Conversas:")
    chatListLabel.pack()
    chatListBox = tk.Listbox(chatListFrame)
    chatListBox.pack(fill='both', expand=True)

    # Atualizar lista de chats
    def updateChatList():
        chats = listChats(username)
        chatListBox.delete(0, 'end')
        for chat in chats:
            chatListBox.insert('end', chat)

    def populateChatList(username):
        response = sendToServer(f"LIST_CHATS {username}")
        try:
            chat_users = json.loads(response)
            chatListBox.delete(0, 'end')  # Limpa a lista de chats
            for user in chat_users:
                chatListBox.insert('end', user)
        except json.JSONDecodeError:
            messagebox.showerror("Erro", f"Resposta do servidor inválida: {response}")
    
    updateChatList()

    chatFrame = tk.Frame(chatWindow)
    chatFrame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
    
    recipient_label = tk.Label(chatFrame, text="Destinatário:")
    recipient_label.pack(pady=(10, 0))
    recipientEntry = tk.Entry(chatFrame)
    recipientEntry.pack(padx=10, pady=5, fill='x')
    
    chatText = tk.Text(chatFrame, state='disabled', wrap='word', bg='lightgray', fg='black')
    chatText.pack(padx=10, pady=10, fill='both', expand=True)
    
    messageEntry = tk.Entry(chatFrame)
    messageEntry.pack(padx=10, pady=(0, 10), fill='x', side='left', expand=True)
    
    sendButton = tk.Button(chatFrame, text="Enviar", command=lambda: sendMessage(username, recipientEntry, messageEntry))
    sendButton.pack(padx=10, pady=(0, 10), side='right')
    loadPreviousMessages(username, chatText)

    def loadChat(event):
        try:
            # Verifica se há um item selecionado na lista
            selected_index = chatListBox.curselection()
            if not selected_index:
                return  # Nenhum item selecionado, não faz nada

            selectedUser = chatListBox.get(selected_index)
            chatText.configure(state='normal')
            chatText.delete('1.0', 'end')  # Limpa o texto antigo

            # Solicita mensagens do servidor
            response = sendToServer(f"GET_CHAT {username} {selectedUser}")
            messages = json.loads(response)

            # Exibe as mensagens no campo de texto
            for message in messages:
                chatText.insert('end', f"{message['sender']}: {message['content']}\n")
            chatText.configure(state='disabled')

            # Atualiza o destinatário no campo de entrada
            recipientEntry.delete(0, 'end')
            recipientEntry.insert(0, selectedUser)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar chat: {e}")


    chatListBox.bind('<<ListboxSelect>>', loadChat)
    populateChatList(username)

    threading.Thread(target=listenForMessages, args=(chatText,) , daemon=True).start()

    chatWindow.mainloop()

root.mainloop()

