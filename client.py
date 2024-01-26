import socket
import errno
import sys
import threading
import tkinter as tk

HEADER_LENGTH = 10

class Client:
    def __init__(self, IP, PORT, USERNAME, chat_screen):
        self.chat_screen = chat_screen
        self.IP = IP
        self.PORT = PORT
        self.USERNAME = USERNAME
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_thread = threading.Thread(target=self.connect_to_server)
        self.listen_thread = threading.Thread(target=self.listen_to_server)
        self.connected = threading.Event()
        self.connect_thread.start()
        self.connect_thread.join()  # Wait for connect_to_server to finish
        self.listen_thread.start()

    def connect_to_server(self):
        self.client_socket.connect((self.IP, self.PORT))
        self.client_socket.setblocking(False)
        username = self.USERNAME.encode('utf-8')
        username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
        self.client_socket.send(username_header + username)
        self.connected.set()  # Signal that the connection is established

    def listen_to_server(self):
        self.connected.wait()  # Wait for the connection to be established
        while True:
            try:
                while True:
                    username_header = self.client_socket.recv(HEADER_LENGTH)
                    if not len(username_header):
                        print('Connection closed by the server')
                        sys.exit()
                    username_length = int(username_header.decode('utf-8').strip())
                    username = self.client_socket.recv(username_length).decode('utf-8')
                    message_header = self.client_socket.recv(HEADER_LENGTH)
                    message_length = int(message_header.decode('utf-8').strip())
                    message = self.client_socket.recv(message_length).decode('utf-8')
                    print(f'{username} > {message}')
                    self.update_gui(f'{username} > {message}')

            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('Reading error: {}'.format(str(e)))
                    sys.exit()
                continue

            except Exception as e:
                print('Reading error: {}'.format(str(e)))
                sys.exit()

    def send_to_server(self, message):
        if message:
            message = message.encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            self.client_socket.send(message_header + message)
            self.update_gui(f"You > {message.decode('utf-8')}")

    def update_gui(self, message):
        if self.chat_screen:
            self.chat_screen.chat.config(state="normal")
            self.chat_screen.chat.insert(tk.END, message + "\n")
            self.chat_screen.chat.config(state="disabled")
