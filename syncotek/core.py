from utils import decorator, common
from logger import loggerGateway, loggerRabbit
from config import config
from mq import rabbitAMQP
import serial

loggerGateway = loggerGateway.get_logger()
loggerRabbit = loggerRabbit.get_logger()

BROKER_AMQP = config.BROKER_AMQP
# BROKER_MQTT = config.BROKER_MQTT

"""
if BROKER_AMQP['publisher'] == 'true':
    logger.info('Initialize AMQP publisher pool ...')
    amqp_publisher = rabbitAMQP.Publisher()
"""
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
def publish_dataframes(processed_data):
    """ Complete the dataframes with current timestamp
     Consider include check the CRC-16 value  """
    for dataframe in processed_data:
        if dataframe:
            timestamp = common.get_now_timestamp()
            dataframe = "1500" + dataframe + common.convert_int_to_hex_string(timestamp)
            amqp_publisher.publish(dataframe)
            print(dataframe)


@decorator.catch_exceptions
def read_from_serial_and_send_to_rabbitmq(serial_port, serial_baudrdate):
    """Read data from the serial port, process it, and send it to RabbitMQ."""
    try:
        # Connect to serial port
        ser = serial.Serial(serial_port, serial_baudrdate, timeout=0.2)  # 57600
        if ser:
            print('Connected to', serial_port)
            loggerGateway.info('Connected to the reader at %s', serial_port)

        loggerRabbit.info('Connecting to RabbitAMQP server ...')
        amqp_publisher.connect()

        if amqp_publisher.channel:
            print('Connected to RabbitAMQP - Queue:', BROKER_AMQP['queue'])
            loggerRabbit.info('Connected to RabbitAMQP - Queue: %s', BROKER_AMQP['queue'])

        while True:
            """ Read data from serial port, process and publish them """
            # serial_data = ser.readline().decode('utf-8').strip()
            # Using readline() we had no complete frames. Using read(3000) we have complete frames. Maybe lower value of
            # 3000 is also valid
            serial_data = ser.read(3000)

            if serial_data:
                # Process the serial data
                processed_data = manage_received_data(serial_data)
                # Publish messages
                publish_dataframes(processed_data)

    except Exception as e:
        print(f"An error occurred: {e}")
