import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import datetime

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("🟢 WhatsApp-Style LAN Chat")
        self.root.geometry("700x500")
        self.root.configure(bg="#ece5dd")

        self.username = ""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.muted = False

        self.setup_login()
        self.connect_to_server()
        self.setup_ui()
        self.load_history()

        # Start message receive thread
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def setup_login(self):
        self.username = simpledialog.askstring("Login", "Enter your username:", parent=self.root)
        if not self.username:
            messagebox.showerror("Error", "Username required!")
            self.root.destroy()

    def connect_to_server(self):
        host = '127.0.0.1'
        port = 12345
        self.socket.connect((host, port))
        self.socket.recv(1024)  # "USERNAME:"
        self.socket.send(self.username.encode())

    def setup_ui(self):
        # --- Sidebar ---
        self.sidebar = tk.Frame(self.root, width=150, bg="#075e54")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.name_label = tk.Label(self.sidebar, text=self.username, bg="#075e54", fg="white", font=("Helvetica", 14, "bold"))
        self.name_label.pack(pady=20)

        # --- Main Chat Area ---
        self.chat_area = tk.Canvas(self.root, bg="#ece5dd")
        self.chat_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.chat_frame = tk.Frame(self.chat_area, bg="#ece5dd")
        self.chat_area.create_window((0, 0), window=self.chat_frame, anchor="nw")

        self.scrollbar = tk.Scrollbar(self.root, command=self.chat_area.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_area.config(yscrollcommand=self.scrollbar.set)
        self.chat_frame.bind("<Configure>", lambda e: self.chat_area.configure(scrollregion=self.chat_area.bbox("all")))

        # --- Bottom Input ---
        self.input_frame = tk.Frame(self.root, bg="#ffffff", height=50)
        self.input_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.entry = tk.Entry(self.input_frame, font=("Helvetica", 13), bd=0, relief=tk.FLAT)
        self.entry.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self.send_message)

        self.send_btn = tk.Button(self.input_frame, text="Send", bg="#25d366", fg="white", command=self.send_message)
        self.send_btn.pack(side=tk.RIGHT, padx=10, pady=10)

    def load_history(self):
        try:
            with open("chat_logs.txt", "r") as f:
                for line in f.readlines():
                    self.display_message(line.strip(), own=(line.startswith(self.username)))
        except:
            pass

    def receive_messages(self):
        while True:
            try:
                msg = self.socket.recv(1024).decode()
                if not self.muted:
                    self.display_message(msg, own=msg.startswith(self.username + ":"))
            except:
                break

    def display_message(self, message, own=False):
        msg_frame = tk.Frame(self.chat_frame, bg="#ece5dd")

        # Timestamp
        timestamp = datetime.now().strftime("%I:%M %p")
        text = message + f"\n{timestamp}"

        if own:
            bubble = tk.Label(msg_frame, text=text, bg="#dcf8c6", fg="black", justify='left',
                              font=("Helvetica", 11), wraplength=350, padx=10, pady=5, anchor='e')
            bubble.pack(anchor='e', padx=10, pady=5)
            # Add delete button
            del_btn = tk.Button(msg_frame, text="❌", command=lambda: self.delete_message(msg_frame), bg="#ece5dd", bd=0)
            del_btn.pack(anchor='e', padx=10)
        else:
            bubble = tk.Label(msg_frame, text=text, bg="white", fg="black", justify='left',
                              font=("Helvetica", 11), wraplength=350, padx=10, pady=5, anchor='w')
            bubble.pack(anchor='w', padx=10, pady=5)

        msg_frame.pack(fill=tk.X, padx=5)
        self.chat_area.yview_moveto(1.0)

    def delete_message(self, frame):
        frame.destroy()

    def send_message(self, event=None):
        msg = self.entry.get().strip()
        if msg:
            if msg == "/exit":
                self.root.quit()
            elif msg == "/mute":
                self.muted = True
            elif msg == "/unmute":
                self.muted = False
            else:
                full_msg = f"{self.username}: {msg}"
                self.socket.send(msg.encode())
                self.display_message(full_msg, own=True)
            self.entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.mainloop()

 