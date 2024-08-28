from concurrent.futures import ProcessPoolExecutor
from config import config
from syncotek import core
from logger import loggerGateway

READER = config.READER

loggerGateway = loggerGateway.get_logger()


def main():
    """main function"""
    loggerGateway.info('Initialize process pool executor for reader ...')
    reader_pool = ProcessPoolExecutor()

    future = reader_pool.submit(core.read_from_serial_and_send_to_rabbitmq, READER['com_port'], READER['baud_rate'])

    # Wait for the task to complete
    try:
        future.result()
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    main()
