from base64 import b64decode
from paramiko import AutoAddPolicy
from paramiko.client import SSHClient
import argparse

def main(connect_string):
    _d = b64decode(
        connect_string
    ).decode('utf8').split(';')
    host = {
        'ip': _d[0].split('@')[-1].split(':')[0],
        'port': int(_d[0].split('@')[-1].split(':')[1]) if len(_d[0].split('@')[-1].split(':')) == 2 else 22,
        'username': None,
        'password': None
    }
    if len( _d[0].split('@') ) > 1:
        host['username'] = _d[0].split('@')[0].split(':')[0]
        if len( _d[0].split('@')[0].split(':') ) > 1:
            host['password'] = _d[0].split('@')[0].split(':')[1]

    path = ';'.join(_d[2:])[:int(_d[1])]
    service_name = ';'.join(_d[2:])[int(_d[1]):].strip()

    client = SSHClient()
    client.set_missing_host_key_policy( AutoAddPolicy() )
    client.connect(
        host['ip'],
        port=host['port'],
        username=host['username'],
        password=host['password']
    )

    if service_name:
        stdin, stdout, stderr = client.exec_command(
            f"service {service_name} status"
        )
        output = stdout.read().decode('utf8')
        try:
            print(
                "Status:",
                output.split('\n')[2].replace('Active:', '').strip()
            )
        except IndexError:
            print('Fetch status raised error')
            print(f'Output: {output}')
    else:
        print('Service not specified')

    sftp_client = client.open_sftp()
    with open('config.txt', 'wb') as local_file:
        with sftp_client.file(path, 'r') as remote_file:
            local_file.write(
                remote_file.read()
            )

    input('Make changes in config.txt, then press Enter to continue')

    with open('config.txt', 'rb') as local_file:
        with sftp_client.file(path, 'w') as remote_file:
            remote_file.write(
                local_file.read()
            )

    print('Changes was uploaded')

    if service_name:
        stdin, stdout, stderr = client.exec_command(
            f"service {service_name} restart"
        )
        err = stderr.read().decode('utf8')
        if err:
            print(f'Service {service_name} not rebooted')
            print(f'Error: {err}')
        else:
            print(f'Service {service_name} has been rebooted')
    else:
        print('Finished')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Remote updating program settings')
    parser.add_argument(
        'connect_string',
        metavar='connectString',
        type=str,
        nargs='+',
        help='encoded connection credentials'
    )

    args = parser.parse_args()
    main(args.connect_string[0])