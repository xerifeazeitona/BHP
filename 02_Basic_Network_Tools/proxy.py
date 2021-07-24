import sys
import socket
import threading


# create a printable character representation of the first 256 integers.
HEX_FILTER = ''.join(
    [(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])

def hexdump(src, length=16, show=True):
    """
    Provides a way to watch the communication going through the proxy
    in real time.
    """
    # if src is a byte string, decode to regular string
    if isinstance(src, bytes):
        src = src.decode()

    results = list()
    for i in range(0, len(src), length):
        # grab a piece of the string to dump and put it into the word variable
        word = str(src[i:i+length])

        # substitute the string representation of each character for the
        # corresponding character in the raw string
        printable = word.translate(HEX_FILTER)
        hexa = ' '.join([f'{ord(c):02X}' for c in word])
        hexwidth = length*3
        # add to results the hex value of the index of the first byte in the
        # word, the hex value of the word, and its printable representation
        results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')
    if show:
        for line in results:
            print(line)
    else:
        return results

def receive_from(connection):
    """
    Accumulate responses from the socket in a buffer. If there's no more
    data or the connection times out, returns the buffer to the function
    caller.
    """
    buffer = b''
    # 5s timeout might be too aggressive on slow connections
    connection.settimeout(5)
    # Loop to read response data into the buffer
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception as e:
        pass
    return buffer

def request_handler(buffer):
    """perform packet modifications"""
    return buffer

def response_handler(buffer):
    """perform packet modifications"""
    return buffer

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    # create a socket for the remote host
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect to the remote host
    remote_socket.connect((remote_host, remote_port))

    # check if we need to request data before going into the main loop
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        # dump the contents of the packet for inspection
        hexdump(remote_buffer)

    remote_buffer = response_handler(remote_buffer)
    if len(remote_buffer):
        print(f'[<==] Sending {len(remote_buffer)} bytes to localhost.')
        client_socket.send(remote_buffer)

    # main loop
    while True:
        # read from local, process the data and send to remote
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            line = f'[==>] Received {len(local_buffer)} bytes from localhost.'
            print(line)
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print('[==> Sent to remote.]')

        # read from remote, process the data and sent to local
        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print(f'[<==] Received {len(remote_buffer)} bytes from remote.')
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print('[<==] Sent to localhost.')

        # when there's no more data, close both connections and bail out
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print('[*] No more data. Closing connections.')
            break

def server_loop(local_host, local_port,
                remote_host, remote_port, receive_first):
    """
    When a fresh connection request comes in, hand it off to the
    proxy_handler function in a new thread
    """
    # create a socket then bind to the local host and listen
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print(f'problem on bind: {e}')
        print(f'[!!] Failed to listen on {local_host}:{local_port}')
        print('[!!] Check for other listening sockets or correct permissions.')
        sys.exit(0)

    print(f'[*] Listening on {local_host}:{local_port}')
    server.listen(5)

    # main loop
    while True:
        client_socket, addr = server.accept()
        # print out the local connection information
        line = f'> Received incoming connection from {addr[0]}:{addr[1]}'
        print(line)
        # start a thread to talk to the remote host
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()

def main():
    """
    Take in some command line arguments and then fire up the server loop
    that listens for connections.
    """
    if len(sys.argv[1:]) != 5:
        print('Usage: ./proxy.py [localhost] [localport]', end='')
        print('[remotehost] [remoteport] [receive_first]')
        print('Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True')
        sys.exit(0)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port,
                remote_host, remote_port, receive_first)

if __name__ == "__main__":
    main()
