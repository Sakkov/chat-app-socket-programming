# Simple CLI chat-app

This is a simple CLI chat app made with python socket programming.

## How to run it
Running this is super easy. You just need python. I used python 3.8.10 default. Other versions works as well. Navigate to the root directory of this project and run this command to run the server:
```console
python server.py
```
To run the client run this command:
```console
python client.py
```
You might need to use "python3" instead of "python".

You can change the IP and PORT in "client.py" and "server.py".

# Usage
When you have the server running and run a client your name will be requested. To make an actually usable chat-app you would have to implement passwords.

## Sending messages
By default you'll be sending broadcast messages. If you want to send a private message to a client, write their name, colon and your message. Here is an example:
```console
Hessu:Hellurei!
```

## Groups
To create a group you need to write:
```console
create group {group name}:[group members separated by a comma]
```
For example:
```console
create group sus:Hessu,Mikki,Pluto
```

The creator of the group can modify the group with the command:
```console
modify group {group name}:[new group members separated by a comma]
```
For example:
```console
modify group sus:Hessu,Mikki,Pluto,Minni
```

To send a group message write:

```console
group {group name}:{message}
```

For example:
```console
group sus:ah-hyuck!
```

## Last seen
To see when was someone online you can use the command:
```console
last seen {name}
```

For example, if I would want to know when was Minni last seen online I would write:
```console
last seen Minni
```