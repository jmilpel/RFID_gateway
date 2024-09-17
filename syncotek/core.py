from utils import decorator, common
from logger import loggerGateway, loggerRabbit
from config import config
from mq import rabbitAMQP
import serial
import serial.tools.list_ports
import time

loggerGateway = loggerGateway.get_logger()
loggerRabbit = loggerRabbit.get_logger()

BROKER_AMQP = config.BROKER_AMQP
# BROKER_MQTT = config.BROKER_MQTT

READER = config.READER

loggerRabbit.info('Initialize AMQP publisher pool ...')
amqp_publisher = rabbitAMQP.Publisher()

clients_ip = []


# Function to
@decorator.catch_exceptions
def rabbit_connection(adr):
    loggerRabbit.info('Connecting to RabbitAMQP server ...')
    amqp_publisher.connect()
    if amqp_publisher.channel:
        print(adr, 'connected to RabbitAMQP - Queue:', BROKER_AMQP['queue'])
        loggerRabbit.info('%s connected to RabbitAMQP - Queue: %s', adr, BROKER_AMQP['queue'])


# Function to
@decorator.catch_exceptions
def manage_received_data(data):
    """ Receive the RAW data and split it in dataframes"""
    while True:
        hex_string = common.convert_data_to_hexstring(data)
        loggerGateway.info('-->[RAW DATA]: %s', hex_string)
        # print('-->[RAW DATA]:', hex_string)
        dataframes = hex_string.split("1500")
        return dataframes


# Function to find all the readers connected via USB to the server
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


# Function to
@decorator.catch_exceptions
def com_publish_dataframes(processed_data, ser):
    """ Complete the dataframes with current timestamp
     Consider include check the CRC-16 value  """
    for dataframe in processed_data:
        if dataframe:
            com = ser.port.encode().hex()
            timestamp = common.get_now_timestamp()
            dataframe = "1500" + dataframe + com + common.convert_int_to_hex_string(timestamp)
            amqp_publisher.publish(dataframe)
            print(dataframe)


# Function to
@decorator.catch_exceptions
def eth_publish_dataframes(processed_data, ip):
    """ Complete the dataframes with current timestamp
     Consider include check the CRC-16 value  """
    for dataframe in processed_data:
        if dataframe:
            client_ip = ip.encode().hex()
            timestamp = common.get_now_timestamp()
            if dataframe != 'aaaaff06c10215e8a2':
                dataframe = "1500" + dataframe + client_ip + common.convert_int_to_hex_string(timestamp)
                amqp_publisher.publish(dataframe)
                print(dataframe)


# Function to control every connection with reader by ethernet
@decorator.catch_exceptions
def handle_client(client_socket, client_address):
    if client_address not in clients_ip:
        clients_ip.append(client_address)

        # Get the client's origin port
        client_ip, client_port = client_address
        loggerGateway.info('Connection established with at %s:%s', client_ip, client_port)
        print(f"Connection established with {client_ip}:{client_port}")

        rabbit_connection(client_ip)

        while True:
            data = client_socket.recv(int(READER['buffer']))
            if data:
                # Process the serial data
                processed_data = manage_received_data(data)
                # Publish messages
                eth_publish_dataframes(processed_data, str(client_ip)[-4:])

        client_socket.close()
        print(f"Connection closed with {client_address}.")


# Function to
@decorator.catch_exceptions
def handle_serial(serial_port, serial_baud_rate, retry_delay, buffer):
    """Read data from the serial port, process it, and send it to RabbitMQ."""
    while True:  # max_retries > 0:
        try:
            # Connect to serial port
            ser = serial.Serial(serial_port, serial_baud_rate, timeout=0.2)  # 57600
            if ser:
                print('Connected to', ser.port)
                loggerGateway.info('Connected to the reader at %s', ser.port)

            rabbit_connection(ser.port)

            while True:
                """ Read data from serial port, process and publish them """
                # serial_data = ser.readline().decode('utf-8').strip()
                # Using readline() we had no complete frames. Using read(3000) we have complete frames. Maybe lower
                # value of 3000 is also valid
                serial_data = ser.read(buffer)

                if serial_data:
                    # Process the serial data
                    processed_data = manage_received_data(serial_data)
                    # Publish messages
                    com_publish_dataframes(processed_data, ser)

        except Exception as e:
            # max_retries -= 1
            print(f"An error occurred: {e}")
            print(f"Trying to reconnect to", serial_port)
            time.sleep(retry_delay)
