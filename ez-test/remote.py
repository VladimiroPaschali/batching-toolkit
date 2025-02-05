import paramiko as pmk
import os
def init_ssh(host: str, username: str, key_filename: str = None) -> pmk.SSHClient:
    '''
    Initialize a SSH connection to a remote host
    :param host: The hostname or IP address of the remote host
    :param username: The username to use for the connection
    :param key_filename: The path to the private key file to use for the connection, otherwise the default key from .ssh will be used
    :return: A connected SSHClient object
    '''
    # if not os.path.exists('~/.ssh/id_rsa'):
    #     raise FileNotFoundError('Private key not found')
    
    ssh = pmk.SSHClient()
    ssh.set_missing_host_key_policy(pmk.AutoAddPolicy())
    
    ssh.connect(host, username=username) # key is not provided beacuse it is not needed
    return ssh

if __name__ == '__main__':
    ssh = init_ssh('optiplex', 'vladimiro')
    _, stdout, stderr = ssh.exec_command('ls -l')
    print(stdout.read().decode())
    ssh.close()
