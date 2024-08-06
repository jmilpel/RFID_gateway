import serial
# from serial import Serial
from utils import common
import pika
from concurrent.futures import ProcessPoolExecutor
import time
from syncotek import core
from logger import loggerMain, loggerRabbit

# RabbitMQ connection parameters
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_EXCHANGE = ''
RABBITMQ_QUEUE = 'RFID'

# Serial connection parameters
SERIAL_PORT = 'COM1'  # or '/dev/ttyUSB0' for Linux
SERIAL_BAUDRATE = 115200

logger = loggerMain.get_logger()
loggerRabbit = loggerRabbit.get_logger()

def connect_to_rabbitmq():
    """Establish a connection to RabbitMQ."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    print('Conectado al RabbitAMQP')
    logger.info('Conectado al RabbitAMQP')
    common.con
    return connection, channel


def send_to_rabbitmq(channel, message):
    """Send a message to RabbitMQ."""
    channel.basic_publish(exchange='',
                          routing_key=RABBITMQ_QUEUE,
                          body=message)


def process_serial_data(serial_data):
    """Process the serial data (this is a placeholder, implement your logic here)."""
    # Example processing: reversing the string
    processed_data = serial_data[::-1]
    return processed_data


def read_from_serial_and_send_to_rabbitmq(serial_port, serial_baudrate):
    """Read data from the serial port, process it, and send it to RabbitMQ."""
    try:
        # Connect to serial port
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=1)  # 57600
        if ser:
            print('Connected to', SERIAL_PORT)

        # Connect to RabbitMQ
        connection, channel = connect_to_rabbitmq() # _,

        while True:
            # Read data from serial port
            # serial_data = ser.readline().decode('utf-8').strip()
            serial_data = ser.read(8000)
            # print(serial_data)

            if serial_data:
                # Process the serial data
                processed_data = core.manage_received_data(serial_data)
                for dataframe in processed_data:
                    if dataframe:
                        timestamp = common.get_now_timestamp()
                        dataframe = "1500" + dataframe + common.convert_int_to_hex_string(timestamp)
                        send_to_rabbitmq(channel, dataframe)
                # Send the processed data to RabbitMQ
                # send_to_rabbitmq(channel, processed_data)
                # print(f"Sent to RabbitMQ: {processed_data}")

            # Simulate some delay for demonstration purposes
            #time.sleep(1)

    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    with ProcessPoolExecutor() as executor:
        # Submit the task to the executor
        future = executor.submit(read_from_serial_and_send_to_rabbitmq, SERIAL_PORT, SERIAL_BAUDRATE)

        # Wait for the task to complete
        try:
            future.result()
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()