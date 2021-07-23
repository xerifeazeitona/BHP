"""
Simple Netcat replacement
"""

import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading


def execute(cmd):
    """receives a command, runs it, and returns the output as a string."""
    cmd = cmd.strip()
    if not cmd:
        return
    # run command and return output
    output = subprocess.check_output(
        shlex.split(cmd), stderr=subprocess.STDOUT)
    return output.decode()


class NetCat:
    """all the plumbing for the program features"""
    def __init__(self, args, buffer=None):
        """Initialize the class' objects"""
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        """entry point for managing this object"""
        if self.args.listen:
            self.listen()
        else:
            self.send()

    def send(self):
        """connect to a target and exchange data"""
        # connect to target and port
        self.socket.connect((self.args.target, self.args.port))
        # if there's a buffer, send it to the target
        if self.buffer:
            self.socket.send(self.buffer)

        try:
            # loop to receive data from the target
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    # If there's no more data, break out of the loop
                    if recv_len < 4096:
                        break
                if response:
                    # print the response data and pause to get
                    # interactive input, then send it
                    print(response)
                    try:
                        buffer = input('> ')
                        buffer += '\n'
                        self.socket.send(buffer.encode())
                    except EOFError:
                        self.socket.close()
                        sys.exit()
        # Ctrl+C to close the socket and quit
        except KeyboardInterrupt:
            print('User terminated.')
            self.socket.close()
            sys.exit()

    def listen(self):
        """
        binds to target and port, then starts listening in a loop,
        passing the connected socket to the handle method
        """
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)

        print(f'[*] Listening on [{self.args.target}] {self.args.port} ...')

        try:
            while True:
                client_socket, _ = self.socket.accept()
                client_thread = threading.Thread(
                    target=self.handle, args=(client_socket,)
                )
                client_thread.start()
        # Ctrl+C to close the socket and quit
        except KeyboardInterrupt:
            print('User terminated.')
            self.socket.close()
            sys.exit()

    def handle(self, client_socket):
        """
        executes the task corresponding to the command line argument it
        receives
        """
        # execute a command and send output back on the socket
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())

        # upload a file
        elif self.args.upload:
            file_buffer = b''
            # listen for content on socket until there's no more data coming in
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break

            # write accumulated content to the specified file
            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())

        # start a shell
        elif self.args.command:
            cmd_buffer = b''
            # sets up a loop 
            while True:
                try:
                    # send a prompt to sender
                    client_socket.send(b'BHP: #> ')
                    # wait for the command to come back
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    # execute the command
                    response = execute(cmd_buffer.decode())
                    if response:
                        # return output to sender
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()


if __name__ == "__main__":
    # create a command line interface with arguments support
    parser = argparse.ArgumentParser(
        description='BHP Net Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # what is displayed when invoked with '--help'
        epilog=textwrap.dedent('''Example:
            netcat.py -t 192.168.1.108 -p 5555 -l -c  # command shell
            netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt # upload to file
            netcat.py -t 192.168.1.108 -p 5555 -l -e\"cat /etc/passwd\"  # execute command
            echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135 # echo text to server port 135
            netcat.py -t 192.168.1.108 -p 5555 # connect to server            
        '''))
    # setup an interactive shell
    parser.add_argument('-c', '--command', action='store_true', help='command shell')
    # execute specific command
    parser.add_argument('-e', '--execute', help='execute specified command')
    # setup a listener
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    # which port to communicate
    parser.add_argument('-p', '--port', type=int, default=9007, help='specified port')
    # target IP
    parser.add_argument('-t', '--target', default='192.168.1.203', help='specified IP')
    # file upload
    parser.add_argument('-u', '--upload', help='upload file')
    args = parser.parse_args()
    # if it's a listener invoke NetCat with an empty buffer, otherwise
    # send buffer content from stdin
    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()

    # Start the NetCat
    nc = NetCat(args, buffer.encode())
    nc.run()
    