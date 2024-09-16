from utils import decorator, common
from logger import loggerGateway, loggerRabbit
from config import config
from mq import rabbitAMQP
import serial
import serial.tools.list_ports
import socket
import time

loggerGateway = loggerGateway.get_logger()
loggerRabbit = loggerRabbit.get_logger()

BROKER_AMQP = config.BROKER_AMQP
# BROKER_MQTT = config.BROKER_MQTT


loggerRabbit.info('Initialize AMQP publisher pool ...')
amqp_publisher = rabbitAMQP.Publisher()


@decorator.catch_exceptions
def manage_received_data(serial_data):
    """ Receive the RAW data and split it in dataframes"""
    while True:
        hex_string = common.convert_data_to_hexstring(serial_data)
        loggerGateway.info('-->[RAW DATA]: %s', hex_string)
        dataframes = hex_string.split("1500")
        return dataframes


@decorator.catch_exceptions
def find_usb_devices(id_product):
    """Find a USB device with the given PID."""
    ports = serial.tools.list_ports.comports()
    if ports:
        rfid_ports = []
        for i in ports:
            if i.pid == int(id_product):
                rfid_ports.append(i)
        return rfid_ports
    else:
        return None


@decorator.catch_exceptions
def publish_dataframes(processed_data, ser):
    """ Complete the dataframes with current timestamp
     Consider include check the CRC-16 value  """
    for dataframe in processed_data:
        if dataframe:
            com = ser.port.encode().hex()
            timestamp = common.get_now_timestamp()
            dataframe = "1500" + dataframe + com + common.convert_int_to_hex_string(timestamp)
            amqp_publisher.publish(dataframe)
            print(dataframe)


@decorator.catch_exceptions
def read_from_serial_and_send_to_rabbitmq(serial_port, serial_baud_rate, retry_delay):
    """Read data from the serial port, process it, and send it to RabbitMQ."""
    while True:  # max_retries > 0:
        try:
            # Connect to serial port
            ser = serial.Serial(serial_port, serial_baud_rate, timeout=0.2)  # 57600
            if ser:
                print('Connected to', ser.port)
                loggerGateway.info('Connected to the reader at %s', ser.port)

            loggerRabbit.info('Connecting to RabbitAMQP server ...')
            amqp_publisher.connect()

            if amqp_publisher.channel:
                print(ser.port, 'connected to RabbitAMQP - Queue:', BROKER_AMQP['queue'])
                loggerRabbit.info('%s connected to RabbitAMQP - Queue: %s', ser.port, BROKER_AMQP['queue'])

            while True:
                """ Read data from serial port, process and publish them """
                # serial_data = ser.readline().decode('utf-8').strip()
                # Using readline() we had no complete frames. Using read(3000) we have complete frames. Maybe lower
                # value of 3000 is also valid
                serial_data = ser.read(1024)

                if serial_data:
                    # Process the serial data
                    processed_data = manage_received_data(serial_data)
                    # Publish messages
                    publish_dataframes(processed_data, ser)

        except Exception as e:
            # max_retries -= 1
            print(f"An error occurred: {e}")
            print(f"Trying to reconnect to", serial_port)
            time.sleep(retry_delay)


@decorator.catch_exceptions
def read_from_ethernet_and_send_to_rabbitmq(ip, port, buffer):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # Associate the server IP and port to the socket
        server_socket.bind((ip, port))

        # Listening the entry connections (máx 1 connection at queue)
        server_socket.listen(1)
        print(f"Server listening at {ip}:{port}")

        while True:
            # Waiting for a new connection
            client_socket, client_address = server_socket.accept()
            with client_socket:
                print(f"Connection established at {client_address}")

                # Get the origin port from the client
                client_ip, client_port = client_address
                print(f"Client IP: {client_ip}, Client Port: {client_port}")

                # Read the message from the client (SYN in this case)
                data = client_socket.recv(buffer)
                if not data:
                    break
                print(f"Data received: {data.decode()}")

                # Response to the client with a SYN-ACK message
                response = "SYN-ACK"
                client_socket.sendall(response.encode())
                print(f"Response SYN-ACK sends to the client {client_ip}:{client_port}")

    """
    # Read data send from the client
                data = client_socket.recv(BUFFER_SIZE)
                if data:
                    print(f"Data received: {data.decode()}")

                    # Here we can proccess or print the data received

                    # Response to the client if its necessary
                    response = "Data received"
                    client_socket.sendall(response.encode())
                    print(f"Response sent to the client {client_ip}:{client_port}")
    """



    """
    # delay = retry_delay
    while True:
        try:
            # Create a socket and connect to the reader
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Connect to a remote host and port
            error_code = sock.connect_ex((ip, port))

            if error_code == 0:
                print('Connection established successfully to', ip, ':', port)
                loggerGateway.info('Connected to the reader at IP --> %s:%s', ip, port)
            else:
                print('Error connecting:', error_code)
                loggerGateway.info('Error connecting %s', error_code)

            loggerRabbit.info('Connecting to RabbitAMQP server ...')
            amqp_publisher.connect()

            if amqp_publisher.channel:
                print(ip, ':', port, 'connected to RabbitAMQP - Queue:', BROKER_AMQP['queue'])
                loggerRabbit.info('%s:%s connected to RabbitAMQP - Queue: %s', ip, port, BROKER_AMQP['queue'])

            while True:
                # Read data from serial port, process and publish them
                # Using readline() we had no complete frames. Using read(3000) we have complete frames. Maybe lower
                # value of 3000 is also valid
                eth_data, address = sock.recvfrom(1024)
                print(eth_data)

                if eth_data:
                    # Process the serial data
                    processed_data = manage_received_data(eth_data)
                    # Publish messages
                    publish_dataframes(processed_data, ip)

        except Exception as e:
            # max_retries -= 1
            print(f"An error occurred: {e}")
            print(f"Trying to reconnect to", ip, ':', port)
            time.sleep(retry_delay)"""
