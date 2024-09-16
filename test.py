import socket

# Configuración del servidor
SERVER_IP = '192.168.0.77'
SERVER_PORT = 8010
BUFFER_SIZE = 1024  # Tamaño del buffer para recibir datos

# Crear el socket TCP/IP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    # Asociar el socket a la dirección y puerto del servidor
    server_socket.bind((SERVER_IP, SERVER_PORT))

    # Escuchar las conexiones entrantes (máximo 1 conexión en cola)
    server_socket.listen(1)
    print(f"Servidor escuchando en {SERVER_IP}:{SERVER_PORT}")

    while True:
        # Esperar una nueva conexión
        client_socket, client_address = server_socket.accept()
        with client_socket:
            print(f"Conexión establecida con {client_address}")

            # Obtener el puerto de origen del cliente
            client_ip, client_port = client_address
            print(f"Cliente IP: {client_ip}, Cliente Puerto: {client_port}")

            # Leer el mensaje del cliente (SYN en este caso)
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                break
            print(f"Datos recibidos: {data.decode()}")

            # Responder al cliente con un SYN-ACK (ejemplo)
            response = "SYN-ACK"
            client_socket.sendall(response.encode())
            print(f"Respuesta SYN-ACK enviada al cliente {client_ip}:{client_port}")


"""
# Leer los datos enviados por el cliente (por ejemplo, una trama RFID)
            data = client_socket.recv(BUFFER_SIZE)
            if data:
                print(f"Datos recibidos: {data.decode()}")
                
                # Aquí puedes procesar los datos recibidos (trama RFID)

                # Responder al cliente si es necesario
                response = "Datos recibidos"
                client_socket.sendall(response.encode())
                print(f"Respuesta enviada al cliente {client_ip}:{client_port}")
"""