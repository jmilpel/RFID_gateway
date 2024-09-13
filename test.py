import socket
from utils import common

ip = '192.168.0.200'
port = 200

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to a remote host and port
error_code = sock.connect_ex((ip, port))

if error_code == 0:
    print('Connection established successfully to', ip, ':', port)
    # msg = 'AAAAFF06C10215E8A2'
    # sock.send(common.convert_str_to_hex(msg))
else:
    print('Error connecting:', error_code)

while True:
    eth_data, address = sock.recv(1024)
    print(eth_data.decode())
