import socket
import select

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

class server():
    def __init__(self, IP, PORT):
        self.IP = IP
        self.PORT = PORT
        self.HEADER_LENGTH = 10
        self.clients = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sockets_list = [self.server_socket]

        self.bind_and_listen()

        self.main_loop()

    def bind_and_listen(self):
        self.server_socket.bind((self.IP, self.PORT))
        self.server_socket.listen()
        print(f'Listening for connections on {self.IP}:{self.PORT}...')

    # Handles message receiving
    def receive_message(self, client_socket):

        try:

            # Receive our "header" containing message length, it's size is defined and constant
            message_header = client_socket.recv(HEADER_LENGTH)

            # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
            if not len(message_header):
                return False

            # Convert header to int value
            message_length = int(message_header.decode('utf-8').strip())

            # Return an object of message header and message data
            return {'header': message_header, 'data': client_socket.recv(message_length)}

        except:

            # If we are here, client closed connection violently, for example by pressing ctrl+c on his script
            # or just lost his connection
            # socket.close() also invokes socket.shutdown(socket.SHUT_RDWR) what sends information about closing the socket (shutdown read/write)
            # and that's also a cause when we receive an empty message
            return False

    def receive_user(self, client_socket):
        # Client should send his name right away, receive it
        user = self.receive_message(client_socket)

        # If False - client disconnected before he sent his name
        if user is False:
            pass
        
        self.sockets_list.append(client_socket)
        
        # Add accepted socket to select.select() list
        self.clients[client_socket] = user

        return user

    def check_message(self, message):
        # Check if the message is a command
        if message["data"].decode('utf-8')[0] == "#":
            print("command")
            # return False, followed by a tuple of the newly calculated message header and the message data
            new_message = "this is a command response"
            new_message_header = f"{len(new_message):<{HEADER_LENGTH}}".encode('utf-8')
            return False, (new_message_header, new_message.encode('utf-8'))
        else:
            print("broadcast")
            return True, message

    def broadcast_message(self, message, notified_socket, user, client_socket):
        # Don't sent it to sender
        if client_socket != notified_socket:
            # Send user and message (both with their headers)
            # We are reusing here message header sent by sender, and saved username header send by user when he connected
            client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    def user_message(self, user_message, notified_socket):
        # Send user a message (both with their headers)
        # GONNA HAVE TO MAKE SURE THIS FUNCTION DOESNT ACCEPT #'s FOR USERNAMES.
        user_message_header, user_message_message = user_message
        notified_socket.send(self.clients[notified_socket]['header'] + self.clients[notified_socket]['data'] + user_message_header + user_message_message)

    def cleanup_socket(self, notified_socket):
        try:
            print('Closed connection from: {}'.format(self.clients[notified_socket]['data'].decode('utf-8')))
            self.sockets_list.remove(notified_socket)
            del self.clients[notified_socket]
            return True
        except Exception as e:
            print(e)
            return False

    def main_loop(self):
        while True:

            # Calls Unix select() system call or Windows select() WinSock call with three parameters:
            #   - rlist - sockets to be monitored for incoming data
            #   - wlist - sockets for data to be send to (checks if for example buffers are not full and socket is ready to send some data)
            #   - xlist - sockets to be monitored for exceptions (we want to monitor all sockets for errors, so we can use rlist)
            # Returns lists:
            #   - reading - sockets we received some data on (that way we don't have to check sockets manually)
            #   - writing - sockets ready for data to be send thru them
            #   - errors  - sockets with some exceptions
            # This is a blocking call, code execution will "wait" here and "get" notified in case any action should be taken
            read_sockets, _, exception_sockets = select.select(self.sockets_list, [], self.sockets_list)

            # Iterate over notified sockets
            for notified_socket in read_sockets:
                
                # If notified socket is a server socket - new connection, accept it
                if notified_socket == self.server_socket:

                    # Accept new connection
                    client_socket, client_address = self.server_socket.accept()
                    initial_message = self.receive_user(client_socket)

                    print('Accepted new connection from {}:{}, username: {}'.format(*client_address, initial_message['data'].decode('utf-8')))

                # Else existing socket is sending a message
                else:

                    message = self.receive_message(notified_socket)

                    # If False, client disconnected, cleanup
                    if message is False:
                        self.cleanup_socket(notified_socket)
                        continue

                    # Get user by notified socket, so we will know who sent the message
                    user = self.clients[notified_socket]

                    print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
                    

                    broadcast_check, checked_message = self.check_message(message)

                    if broadcast_check == True:
                        # Iterate over connected clients and broadcast message
                        for client_socket in self.clients:
                            self.broadcast_message(checked_message, notified_socket, user, client_socket)
                    else:
                        print("not broadcasting")
                        self.user_message(checked_message, notified_socket)

            # It's not really necessary to have this, but will handle some socket exceptions just in case
            for notified_socket in exception_sockets:

                # Remove from list for socket.socket()
                self.sockets_list.remove(notified_socket)

                # Remove from our list of users
                del self.clients[notified_socket]

if __name__ == "__main__":
    server(IP, PORT)
