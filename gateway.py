from concurrent.futures import ProcessPoolExecutor
from config import config
from syncotek import core
# from logger import loggerMain
# import socket


READER = config.READER
# SERVER = config.SERVER
# CLIENT = config.CLIENT
# logger = loggerMain.get_logger()


def main():
    """main function"""
    with ProcessPoolExecutor() as executor:
        # Submit the task to the executor
        future = executor.submit(core.read_from_serial_and_send_to_rabbitmq, READER['com_port'], READER['baud_rate'])

        # Wait for the task to complete
        try:
            future.result()
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == '__main__':
    main()
