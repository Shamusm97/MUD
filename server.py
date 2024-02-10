import socket
import select

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

class Client:
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        self.user = self.receive_user()

    def receive_message(self):
        try:
            message_header = self.socket.recv(HEADER_LENGTH)
            if not len(message_header):
                return False
            message_length = int(message_header.decode('utf-8').strip())
            return {'header': message_header, 'data': self.socket.recv(message_length)}
        except:
            return False

    def receive_user(self):
        user = self.receive_message()
        if user is False:
            return None
        print('Accepted new connection from {}:{}'.format(*self.address))
        return user

    def send_message(self, client, message):
        self.socket.send(client.user['header'] + client.user['data'] + message['header'] + message['data'])

    def cleanup(self):
        print('Closed connection from: {}'.format(self.address))
        self.socket.close()

class ConnectionsHandler:
    def __init__(self, IP, PORT):
        self.IP = IP
        self.PORT = PORT
        self.server_socket = None
        self.all_connections = []
        self.setup_server()

    def setup_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.IP, self.PORT))
        self.server_socket.listen()

        print(f'Listening for connections on {self.IP}:{self.PORT}...')

    def accept_new_connection(self):
        client_socket, client_address = self.server_socket.accept()
        new_client = Client(client_socket, client_address)
        if new_client.user:
            self.all_connections.append(new_client)

    def receive_from_all(self):
        read_sockets, _, exception_sockets = select.select([self.server_socket] + [c.socket for c in self.all_connections], [], [c.socket for c in self.all_connections], 0)
        for notified_socket in read_sockets:
            if notified_socket == self.server_socket:
                self.accept_new_connection()
            else:
                client = next((c for c in self.all_connections if c.socket == notified_socket), None)
                if client:
                    message = client.receive_message()
                    if message:
                        print(f'Received message from {client.user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
                        # Here you can add custom logic for message handling and broadcasting
                        self.broadcast(client, message)
                    else:
                        client.cleanup()
                        self.all_connections.remove(client)

        for notified_socket in exception_sockets:
            client = next((c for c in self.all_connections if c.socket == notified_socket), None)
            if client:
                client.cleanup()
                self.all_connections.remove(client)

    def broadcast(self, client, message):
        for connection in self.all_connections:
            if connection != client:
                connection.send_message(client, message)

    def run(self):
        while True:
            self.receive_from_all()

if __name__ == "__main__":
    connection_handler = ConnectionsHandler(IP, PORT)
    connection_handler.run()
