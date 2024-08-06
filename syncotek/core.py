from utils import decorator, common  # constant
from logger import loggerMain, loggerRabbit
from config import config
from mq import rabbitAMQP
import serial
# from syncotek import location
# import time

logger = loggerMain.get_logger()
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
    # Manage connection. This is done from one process of ProcessPoolExecutor
    while True:
        hex_string = common.convert_data_to_hexstring(serial_data)
        logger.info('-->[RAW DATA]: %s', hex_string)
        # print('RAW data:', hex_string)
        dataframes = hex_string.split("1500")
        # print(dataframes)
        return dataframes


def publish_dataframes(processed_data):
    for dataframe in processed_data:
        if dataframe:
            timestamp = common.get_now_timestamp()
            dataframe = "1500" + dataframe + common.convert_int_to_hex_string(timestamp)
            amqp_publisher.publish(dataframe)
            print(dataframe)


def read_from_serial_and_send_to_rabbitmq(serial_port, serial_baurdate):
    """Read data from the serial port, process it, and send it to RabbitMQ."""
    try:
        # Connect to serial port
        ser = serial.Serial(serial_port, serial_baurdate, timeout=0.2)  # 57600
        if ser:
            print('Connected to', serial_port)
            logger.info('Connected to the reader at %s', serial_port)

        loggerRabbit.info('Connecting to RabbitAMQP server ...')
        amqp_publisher.connect()

        if amqp_publisher.channel:
            print('Connected to RabbitAMQP - Queue:', BROKER_AMQP['queue'])
            loggerRabbit.info('Connected to RabbitAMQP - Queue: %s', BROKER_AMQP['queue'])

        while True:
            # Read data from serial port
            # serial_data = ser.readline().decode('utf-8').strip()
            serial_data = ser.read(3000)
            # print(serial_data)

            if serial_data:
                # Process the serial data
                processed_data = manage_received_data(serial_data)
                # Publish messages
                publish_dataframes(processed_data)


    except Exception as e:
        print(f"An error occurred: {e}")


"""
@decorator.catch_exceptions
def manage_received_data(socket_server):
    # Manage connection. This is done from one process of ProcessPoolExecutor
    while True:
        data, address = socket_server.recvfrom(1024)
        if data:
            data = data.hex().upper()
            data_splitted = data.split("1500")
            print(data_splitted)
            for data in data_splitted:
                if data:
                    data = "1500" + data
                    header = data[0:12]
                    if header == constant.ReceivedPacketType.LOCATION.value:
                        if BROKER_AMQP['publisher'] == 'true':
                            location.manage_received_data(data=data, publisher=amqp_publisher)
                        if BROKER_MQTT['publisher'] == 'true':
                            location.manage_received_data(data=data, publisher=mqtt_publisher)
                    elif header == constant.ReceivedPacketType.REG_TAG.value:
                        regTag.manage_received_data(data=data, address=address)
                    elif header == constant.ReceivedPacketType.ACK.value:
                        ack.manage_received_data(data=data, address=address)
                    elif header == constant.ReceivedPacketType.HEARTBEAT.value:
                        heartbeat.manage_received_data(data=data)
                    elif header == constant.ReceivedPacketType.SYNC.value:
                        sync.manage_received_data(data=data)
                    elif header == constant.ReceivedPacketType.REG_ANCHOR.value:
                        regAnchor.manage_received_data(data=data, address=address)
                    else:
                        logger_investigate.info('[UNKNOWN] -- header %s -- data %s', header, data)
                        pass"""
