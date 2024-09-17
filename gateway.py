from concurrent.futures import ProcessPoolExecutor
from config import config
from syncotek import core
from logger import loggerGateway
import socket

READER = config.READER
INTERFACE = config.INTERFACE

loggerGateway = loggerGateway.get_logger()


def main():
    """main function"""
    loggerGateway.info('Initialize process pool executor for reader ...')
    reader_pool = ProcessPoolExecutor(max_workers=int(READER['max_process']))

    # Depends on the type of connection we use different methods
    # Check which interface is active
    if INTERFACE['ether'] == 'true':
        # Receive data from the reader
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_server:
            socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Associate to the socket the server IP and port
            socket_server.bind((READER['server_ip'], int(READER['server_port'])))

            # Listening the entry connections (maxi 1 connection in queue)
            socket_server.listen(1)
            print(f"Gateway is now listening at {READER['server_ip']}:{READER['server_port']}")
            loggerGateway.info('Gateway is now listening at %s:%s', READER['server_ip'], READER['server_port'])

            # Use the ProcessPpoolExecutor
            while True:
                # Waiting for a new connection
                client_socket, client_address = socket_server.accept()
                # Send the connection to the ProcessPool to manage it
                reader_pool.submit(core.handle_client, client_socket, client_address)

    elif INTERFACE['rs232'] == 'true':
        futures = []
        """ Find USB devices by product id """
        ports = core.find_usb_devices(int(READER['id_product']))
        for port in ports:
            index = ports.index(port)
            variable_name = "future" + str(index)
            locals()[variable_name] = reader_pool.submit(core.handle_serial, port.device, READER['baud_rate'],
                                                         READER['retry_delay'], READER['buffer'])
            futures.append(locals()[variable_name])
        # Wait for the task to complete
        try:
            for future in futures:
                future.result()

        except Exception as e:
            print(f"An error occurred: {e}")

    elif INTERFACE['rs485'] == 'true':
        # Not developed
        print("RS485")


if __name__ == '__main__':
    main()
