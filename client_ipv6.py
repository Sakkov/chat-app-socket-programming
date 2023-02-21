import socket
import threading
import sys

class Client:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.client_socket.connect(('::1', 8080))
        print('Connected to the server')
        self.name = input('Enter your display name: ')
        self.client_socket.send(self.name.encode('utf-8'))
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

    def receive_messages(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                for line in data.split(';'):
                    if line:
                        print(f'{line}\n')
            except OSError:
                print("Server closed the connection")
                break

    def start_client(self):
        try:
            while True:
                message = input()
                self.client_socket.send(message.encode('utf-8'))
                if message == 'exit':
                    break
            print("Closing the client...")
            self.client_socket.close()
            sys.exit()
        except KeyboardInterrupt:
            self.client_socket.close()
            sys.exit()

if __name__ == '__main__':
    client = Client()
    client.start_client()