from base64 import b64encode

# Хост в формате user:pass@ip:port
host = input(f'Input host: ')

# Путь к конфиг-файлу, начиная с /
path = input(f'Input path: ')

# Название systemd сервиса
service_name = input('Input service name: ')

connect_string = f"{host};{len(path)};{path}{service_name}".encode('utf8')
print('connectString:', b64encode(connect_string).decode())
