import socket
import time
import tkinter as tk
from tkinter import scrolledtext
from threading import Thread
import datetime

PORT = 5050
SERVER = "10.10.60.140"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"


def connect():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        return client
    except ConnectionAbortedError:
        print("Connection failed. Is the server running?")
    except socket.error as e:
        print(f"Socket error: {e}")
    return None


def send(client, msg, text_area):
    try:
        message = msg.encode(FORMAT)
        client.send(message)
        # Display sent message in text area
        text_area.config(state=tk.NORMAL)
        text_area.insert(tk.END, f"You: {msg}\n")
        text_area.config(state=tk.DISABLED)
        text_area.see(tk.END)
    except socket.error as e:
        print(f"Failed to send a message: {e}")


def receive(client, text_area):
    while True:
        try:
            msg = client.recv(1024).decode(FORMAT)
            if msg:
                # Display received message in text area
                text_area.config(state=tk.NORMAL)
                text_area.insert(tk.END, f"{msg}\n")
                text_area.config(state=tk.DISABLED)
                text_area.see(tk.END)
        except socket.error as e:
            print(f"Error receiving message: {e}")
            break


# Tkinter GUI setup
def run_gui():
    client = connect()
    if client is None:
        return

    root = tk.Tk()
    root.title("Chat Client")

    # Text area to display messages
    text_area = scrolledtext.ScrolledText(root, state=tk.DISABLED, wrap=tk.WORD, height=20)
    text_area.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

    # Entry box for typing messages
    msg_entry = tk.Entry(root, width=50)
    msg_entry.pack(padx=20, pady=5, fill=tk.X)

    # Button to send messages
    send_button = tk.Button(root, text="Send", command=lambda: send(client, msg_entry.get(), text_area))
    send_button.pack(pady=10)

    # Thread to receive messages
    receive_thread = Thread(target=receive, args=(client, text_area))
    receive_thread.daemon = True
    receive_thread.start()

    # Bind "Enter" key to send messages
    def on_enter(event):
        send(client, msg_entry.get(), text_area)
        msg_entry.delete(0, tk.END)
    
    root.bind('<Return>', on_enter)

    root.mainloop()

    # Send disconnect message when closing the app
    send(client, DISCONNECT_MESSAGE, text_area)
    time.sleep(1)
    print("Disconnected")


if __name__ == "__main__":
    run_gui()
