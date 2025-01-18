import json
import os
import socket

messagesFile = 'messages.json'

def loadMessages():
    if not os.path.exists(messagesFile):
        return {}
    with open(messagesFile, 'r') as file:
        return json.load(file)

def format_messages(userName, selectedUser, data):
    messages = []

    # Verifica as mensagens onde o 'sender' é 'userName' e o 'receiver' é 'selectedUser'
    if selectedUser in data:
        for msg in data[selectedUser]:
            if msg['sender'] == userName:
                messages.append(f"Você: {msg['content']}")

    # Verifica as mensagens onde o 'sender' é 'selectedUser' e o 'receiver' é 'userName'
    if userName in data:
        for msg in data[userName]:
            if msg['sender'] == selectedUser:
                messages.append(f"{selectedUser}: {msg['content']}")

    return messages


data = loadMessages()
userName = "Pedro"
selectedUser = "Igor"
messages = format_messages(userName, selectedUser, data)

# Exibe as mensagens
for msg in messages:
    print(msg)

# Exemplo de teste
print(format_messages("Lucas", "Pedro", data))

