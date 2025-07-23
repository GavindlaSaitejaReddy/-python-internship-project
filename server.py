import socket
import threading

# Server configuration
host = '127.0.0.1'
port = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
usernames = []

print(f"[STARTED] Server running on {host}:{port}")

def broadcast(message, sender_conn=None):
    """Send message to all connected clients"""
    for client in clients:
        if client != sender_conn:
            try:
                client.send(message.encode())
            except:
                remove_client(client)

def handle_client(client):
    """Handle messages from a client"""
    while True:
        try:
            msg = client.recv(1024).decode()
            if msg.strip() == "/exit":
                remove_client(client)
                break
            else:
                index = clients.index(client)
                username = usernames[index]
                full_msg = f"{username}: {msg}"
                print(full_msg)

                # Save to log
                with open("chat_logs.txt", "a") as log_file:
                    log_file.write(full_msg + "\n")

                broadcast(full_msg, sender_conn=client)
        except:
            remove_client(client)
            break

def receive_connections():
    """Accept new connections"""
    while True:
        client, addr = server.accept()
        print(f"[NEW CONNECTION] {addr} connected.")

        client.send("USERNAME:".encode())
        username = client.recv(1024).decode()

        usernames.append(username)
        clients.append(client)

        welcome_msg = f"{username} joined the chat."
        print(welcome_msg)
        broadcast(welcome_msg)
        with open("chat_logs.txt", "a") as log_file:
            log_file.write(welcome_msg + "\n")

        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

def remove_client(client):
    """Remove client from active lists"""
    if client in clients:
        index = clients.index(client)
        username = usernames[index]
        print(f"[DISCONNECTED] {username} left.")
        broadcast(f"{username} left the chat.")
        with open("chat_logs.txt", "a") as log_file:
            log_file.write(f"{username} left the chat.\n")
        clients.remove(client)
        usernames.remove(username)
        client.close()

# Start the server
receive_connections()

