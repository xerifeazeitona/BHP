import paramiko

def ssh_command(ip, port, user, passwd, cmd):
    """
    Makes a connection to an SSH server and runs a single command.
    """
    client = paramiko.SSHClient()
    # auto accept the server's SSH keys, bad idea on networks we don't control
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # connect to the server
    client.connect(ip, port=port, username=user, password=passwd)

    # execute the command on the server
    _, stdout, stderr = client.exec_command(cmd)
    output = stdout.readlines() + stderr.readlines()
    # if there's output, print it out
    if output:
        print('--- Output ---')
        for line in output:
            print(line.strip())

if __name__ == "__main__":
    import getpass
    # only works properly if the username is the same in both client and server
    # user = getpass.getuser()  
    user = input('Username: ')
    password = getpass.getpass()

    ip = input('Enter server IP: ') or '192.168.69.116'
    port = input('Enter port or <CR>: ') or 2222
    cmd = input('Enter command or <CR>: ') or 'id'
    # send command to be executed
    ssh_command(ip, port, user, password, cmd)
