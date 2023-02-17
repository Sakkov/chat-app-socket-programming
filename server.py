import socket
import threading
import time
import sys

HOST = ''
PORT = 8080

class Server:
    def __init__(self):
        self.server_socket = socket.create_server((HOST, PORT), family=socket.AF_INET6, dualstack_ipv6=True)
        self.server_socket.listen(5)
        self.clients = {}
        self.offline_clients = {}
        self.groups = {}
        self.offline_messages = {}
        print(f'Server started on {HOST}:{PORT}')

    def broadcast(self, message):
        for client in self.clients:
            self.clients[client]['socket'].send(message)

    def group_send(self, message, group, client_socket, name):
        if group in self.groups:
            for member in self.groups[group]['members']:
                if member in self.clients:
                    self.clients[member]['socket'].send(message)
                    client_socket.send(f'[{member} received your message];'.encode('utf-8'))
                else:
                    client_socket.send(f'{member} is offline. Message will be delivered when they come online;'.encode('utf-8'))
                    if member in self.offline_messages:
                        self.offline_messages[member].append({'sender': name, 'message': message.decode('utf-8')})
                    else:
                        self.offline_messages[member] = [{'sender': name, 'message': message.decode('utf-8')}]
        else:
            print(f'[Error] Group {group} does not exist')


    def handle_client(self, client_socket, address):
        name = client_socket.recv(1024).decode('utf-8')
        self.clients[name] = {'socket': client_socket, 'last_seen': 'Online'}
        self.broadcast(f'[{name} has joined the chat];'.encode('utf-8'))
        if name in self.offline_messages:
            client_socket.send(f'[You have {len(self.offline_messages[name])} new messages];'.encode('utf-8'))
            for message_dict in self.offline_messages[name]:
                message = message_dict['message']
                client_socket.send(message.encode('utf-8'))
                self.clients[message_dict['sender']]['socket'].send(f'[{name} received your message] {message}'.encode('utf-8'))
            del self.offline_messages[name]
            client_socket.send('[End of new messages];'.encode('utf-8'))
        while True:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                if data.startswith('create group'):
                    try:
                        group_name, members = data.split(' ', 2)[2].split(':', 1)
                        if group_name in self.groups:
                            client_socket.send(f'[Error] Group {group_name} already exists;'.encode('utf-8'))
                            continue
                        members = members.split(',')
                        self.groups[group_name] = {'creator': name, 'members': members}
                        client_socket.send(f'[{group_name} has been created with members {", ".join(members)}];'.encode('utf-8'))
                    except ValueError:
                        client_socket.send(f'[Error] Invalid format for creating a group;'.encode('utf-8'))
                elif data.startswith('modify group'):
                    try:
                        group_name, members = data.split(' ', 2)[2].split(':', 1)
                        members = members.split(',')
                        if group_name in self.groups and self.groups[group_name]['creator'] == name:
                            self.groups[group_name]['members'] = members
                            client_socket.send(f'[{group_name} has been modified with members {", ".join(members)}];'.encode('utf-8'))
                        else:
                            client_socket.send(f'[Error] You are not the creator of the group {group_name};'.encode('utf-8'))
                    except ValueError:
                        client_socket.send(f'[Error] Invalid format for modifying a group;'.encode('utf-8'))
                elif data.startswith('group'):
                    try:
                        group_name, message = data.split(' ', 1)[1].split(':', 1)
                        if group_name in self.groups and name in self.groups[group_name]['members']:
                            self.group_send(f'[{time.ctime()}][{group_name}][{name}] {message};'.encode('utf-8'), group_name, client_socket, name)
                        else:
                            client_socket.send(f'[Error] You are not a member of the group {group_name};'.encode('utf-8'))
                    except ValueError:
                        client_socket.send(f'[Error] Invalid format for group message;'.encode('utf-8'))
                elif data.startswith('last seen'):
                    try:
                        recipient = data.split(' ', 2)[2]
                        if recipient in self.clients:
                            try:
                                if recipient in self.clients:
                                    client_socket.send(f'[{recipient} is currently online];'.encode('utf-8'))
                                else:
                                    client_socket.send(f'[{recipient} was last seen: {self.offline_clients[recipient]["last_seen"]}];'.encode('utf-8'))
                            except KeyError:
                                client_socket.send(f'[{recipient} is currently online];'.encode('utf-8'))
                        else:
                            client_socket.send(f'[Error] {recipient} is not in the chat;'.encode('utf-8'))
                    except IndexError:
                        client_socket.send(f'[Error] Invalid format for last seen command;'.encode('utf-8'))
                elif ':' in data:
                    recipient, message = data.split(':', 1)
                    new_message = f'[{time.ctime()}][private][from {name} to {recipient}] {message};'
                    if recipient in self.clients:
                        self.clients[recipient]['socket'].send(new_message.encode('utf-8'))
                        client_socket.send(new_message.encode('utf-8'))
                        client_socket.send(f'[{recipient} received your message];'.encode('utf-8'))
                    else:
                        client_socket.send(f'{recipient} is offline. Message will be delivered when they come online;'.encode('utf-8'))
                        if recipient in self.offline_messages:
                            self.offline_messages[recipient].append({'sender': name, 'message': new_message})
                        else:
                            self.offline_messages[recipient] = [{'sender': name, 'message': new_message}]
                elif data == 'exit':
                    break
                else:
                    self.broadcast(f'[{time.ctime()}][{name}] {data};'.encode('utf-8'))
            except ConnectionResetError:
                break
        self.clients[name]['last_seen'] = time.ctime(time.time())
        self.broadcast(f'[{name} has left the chat];'.encode('utf-8'))
        self.offline_clients[name] = self.clients[name]
        del self.clients[name]
        print(f'Closed connection from {address[0]}:{address[1]}')

    def start_server(self):
        while True:
            client_socket, address = self.server_socket.accept()
            print(f'Accepted connection from {address[0]}:{address[1]}')
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
            client_thread.start()

if __name__ == '__main__':
    server = Server()
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("Closing the server...")
        server.server_socket.close()
        sys.exit()

