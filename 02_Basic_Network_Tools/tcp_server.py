"""
Standard multi-threaded TCP server
"""

import socket
import threading

IP = '0.0.0.0'
PORT = 9007

def main():
    """main server loop"""
    # create a socket object
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # pass the IP and PORT that we want to listen on
    server.bind((IP, PORT))
    # start listening with max backlog of 5 connections
    server.listen(5)
    print(f'[*] Listening on {IP}:{PORT}')

    while True:
        # receive client socket and remote connection details
        client, address = server.accept()
        print(f'[*] Accepted connection from {address[0]}:{address[1]}')
        # create a new thread object
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

def handle_client(client_socket):
    """performs the recv and sends a simple message back to the client"""
    with client_socket as sock:
        request = sock.recv(1024)
        print(f'[*] Received: {request.decode("utf-8")}')
        sock.send(b'ACK')

if __name__ == "__main__":
    main()
