from concurrent.futures import ProcessPoolExecutor
from config import config
from syncotek import core
from logger import loggerGateway

READERS = config.READERS

loggerGateway = loggerGateway.get_logger()


def main():
    """main function"""
    loggerGateway.info('Initialize process pool executor for reader ...')
    reader_pool = ProcessPoolExecutor()
    """ Depends on the type of connection we call different functions """
    if READERS['RS232'] == 'true':
        futures = []
        """ Find USB devices by product id """
        ports = core.find_usb_devices(int(READERS['id_product']))
        for port in ports:
            index = ports.index(port)
            variable_name = "future" + str(index)
            locals()[variable_name] = reader_pool.submit(core.read_from_serial_and_send_to_rabbitmq,
                                                         port.device, READERS['baud_rate'], READERS['retry_delay'])
            futures.append(locals()[variable_name])

        # Wait for the task to complete
        try:
            for future in futures:
                future.result()

        except Exception as e:
            print(f"An error occurred: {e}")

    elif READERS['RS485'] == 'true':
        print("RS485")
    elif READERS['ETHER'] == 'true':
        print("ETHER")


if __name__ == '__main__':
    main()
