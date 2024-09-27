import threading
import socket
import datetime
import tkinter as tk
from tkinter import scrolledtext
from threading import Thread

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"    
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = set()
clients_lock = threading.Lock()

def broadcast(message, sender_conn, text_area):
    """
    Sends a message to all connected clients except the sender (if any).
    If sender_conn is None, it means the message is from the server itself.
    """
    with clients_lock:
        for client in clients:
            if client != sender_conn:  # Avoid sending the message back to the sender
                try:
                    client.sendall(message.encode(FORMAT))
                except socket.error as e:
                    text_area.config(state=tk.NORMAL)
                    text_area.insert(tk.END, f"Error sending message to client: {e}\n")
                    text_area.config(state=tk.DISABLED)
                    text_area.see(tk.END)

def handle_client(conn, addr, text_area):
    text_area.config(state=tk.NORMAL)
    text_area.insert(tk.END, f"[NEW CONNECTION] {addr} Connected\n")
    text_area.config(state=tk.DISABLED)
    text_area.see(tk.END)

    try:
        connected = True
        while connected:
            try:
                msg = conn.recv(1024).decode(FORMAT)
                if not msg:
                    break
            except socket.error as e:
                text_area.config(state=tk.NORMAL)
                text_area.insert(tk.END, f"Error receiving message from {addr}: {e}\n")
                text_area.config(state=tk.DISABLED)
                text_area.see(tk.END)
                break

            if msg == DISCONNECT_MESSAGE:
                connected = False

            # Add timestamp when the message is sent or received
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            formatted_msg = f"[{timestamp}] [{addr}] {msg}"
            
            # Display received message in the text area
            text_area.config(state=tk.NORMAL)
            text_area.insert(tk.END, f"{formatted_msg}\n")
            text_area.config(state=tk.DISABLED)
            text_area.see(tk.END)

            # Broadcast the message to other clients
            broadcast(formatted_msg, conn, text_area)

    finally:
        with clients_lock:
            clients.remove(conn)
        
        conn.close()
        text_area.config(state=tk.NORMAL)
        text_area.insert(tk.END, f"[{addr}] Disconnected\n")
        text_area.config(state=tk.DISABLED)
        text_area.see(tk.END)


def start_server(text_area):
    text_area.config(state=tk.NORMAL)
    text_area.insert(tk.END, "[SERVER STARTED]!\n")
    text_area.config(state=tk.DISABLED)
    text_area.see(tk.END)

    server.listen()
    while True:
        conn, addr = server.accept()
        with clients_lock:
            clients.add(conn)

        # Start a new thread for handling the client
        thread = threading.Thread(target=handle_client, args=(conn, addr, text_area))
        thread.start()


def send_server_message(msg, text_area, msg_entry):
    """
    Function to send messages from the server itself to all connected clients.
    """
    if not msg.strip():
        return  # Do not send empty messages

    # Add timestamp to the message
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    formatted_msg = f"[{timestamp}] [SERVER]: {msg}"

    # Display message in the server's text area
    text_area.config(state=tk.NORMAL)
    text_area.insert(tk.END, f"{formatted_msg}\n")
    text_area.config(state=tk.DISABLED)
    text_area.see(tk.END)

    # Broadcast the message to all clients (since sender is None)
    broadcast(formatted_msg, None, text_area)

    # Clear the input field after sending
    msg_entry.delete(0, tk.END)

# Tkinter GUI setup
def run_server_gui():
    root = tk.Tk()
    root.title("Server Interface")

    # Text area to display server logs
    text_area = scrolledtext.ScrolledText(root, state=tk.DISABLED, wrap=tk.WORD, height=20)
    text_area.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

    # Entry box for server to type messages
    msg_entry = tk.Entry(root, width=50)
    msg_entry.pack(padx=20, pady=5, fill=tk.X)

    # Button to send messages from the server
    send_button = tk.Button(root, text="Send", command=lambda: send_server_message(msg_entry.get(), text_area, msg_entry))
    send_button.pack(pady=10)

    # Thread to start the server
    start_thread = Thread(target=start_server, args=(text_area,))
    start_thread.daemon = True
    start_thread.start()

    # Bind "Enter" key to send messages from the server
    def on_enter(event):
        send_server_message(msg_entry.get(), text_area, msg_entry)

    root.bind('<Return>', on_enter)

    root.mainloop()


if __name__ == "__main__":
    run_server_gui()
