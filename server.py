import threading
import socket
import datetime
import tkinter as tk
from tkinter import scrolledtext
from threading import Thread

PORT = 5050
SERVER = "10.10.60.140"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = set()
clients_lock = threading.Lock()


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

            # Send the message to all connected clients
            with clients_lock:
                for c in clients:
                    if c != conn:  # Don't send the message back to the sender
                        try:
                            c.sendall(f"{formatted_msg}".encode(FORMAT))
                        except socket.error as e:
                            text_area.config(state=tk.NORMAL)
                            text_area.insert(tk.END, f"Failed to send message to {addr}: {e}\n")
                            text_area.config(state=tk.DISABLED)
                            text_area.see(tk.END)

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


# Tkinter GUI setup
def run_server_gui():
    root = tk.Tk()
    root.title("Server Interface")

    # Text area to display server logs
    text_area = scrolledtext.ScrolledText(root, state=tk.DISABLED, wrap=tk.WORD, height=20)
    text_area.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

    # Button to start the server
    start_button = tk.Button(root, text="Start Server", command=lambda: Thread(target=start_server, args=(text_area,)).start())
    start_button.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    run_server_gui()
