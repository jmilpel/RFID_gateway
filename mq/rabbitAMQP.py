from config import config
from logger import loggerRabbit
from ujson import encode
import pika
import pika.exceptions

loggerRabbit = loggerRabbit.get_logger()

BROKER_AMQP = config.BROKER_AMQP

class Publisher:
    """ Class publisher for publish message at RabbitMQ broker
        We configure heartbeat according to broker configuration to keep the TCP connection established and channel"""

    def __init__(self):
        self.credentials = pika.PlainCredentials(username=BROKER_AMQP['username'], password=BROKER_AMQP['password'])
        self.parameters = pika.connection.ConnectionParameters(host=BROKER_AMQP['host'], port=int(BROKER_AMQP['port']),
                                                               virtual_host=BROKER_AMQP['virtual_host'],
                                                               credentials=self.credentials)
        self.exchange = BROKER_AMQP['exchange']
        self.queue = BROKER_AMQP['queue']
        self.connection = None
        self.channel = None

    def connect(self):
        if str(BROKER_AMQP['publisher']).lower() == 'true':
            """ Establish a new connection to RabbitMQ broker """
            if not self.connection or self.connection.is_closed:
                loggerRabbit.info('-- Trying to establish a new connection... --')
                try:
                    self.connection = pika.BlockingConnection(parameters=self.parameters)
                    self.channel = self.connection.channel()
                    self.channel.queue_declare(queue=self.queue, durable=True, arguments={'x-queue-type': 'classic'})
                    loggerRabbit.info('-- Successfully connected!! --')
                except Exception as e:
                    loggerRabbit.error('-- Error while establishing connection: %s --', str(e))
            elif not self.channel or self.channel.is_closed:
                loggerRabbit.info('-- Trying to recover channel connection... ---')
                try:
                    self.channel = self.connection.channel()
                    self.channel.queue_declare(queue=self.queue, durable=True, arguments={'x-queue-type': 'classic'})
                    loggerRabbit.info('-- Successfully channel connected!! --')
                except Exception as e:
                    loggerRabbit.error('-- Error while recovering lost channel: %s --', str(e))

    def simple_publish(self, msg):
        """ Simple publish message. It will be called from publish method"""
        try:
            self.channel.basic_publish(exchange=self.exchange, routing_key=self.queue, body=msg)  # body=encode(msg)
            loggerRabbit.info('AMQP message: %s', msg)
        except Exception as e:
            msg['retry'] = msg['retry'] + 1 if 'retry' in msg else 1
            self.connection.close()
            self.publish(msg=msg)
            loggerRabbit.error('-- Error publishing message %s at rabbit with simple_publish method: %s --', str(msg), str(e))

    def publish(self, msg):
        """Publish msg, reconnecting if necessary"""
        if 'retry' not in msg or 'retry' in msg and msg['retry'] < int(BROKER_AMQP['max_retries']):
            try:
                if not self.connection or self.connection.is_closed:
                    loggerRabbit.info('-- Detected not connected or connection close --')
                    self.connect()
                elif not self.channel or self.channel.is_closed:
                    loggerRabbit.info('-- Detected channel not connected or channel close --')
                    self.connect()
                self.simple_publish(msg=msg)

            except pika.exceptions.ConnectionClosed:
                loggerRabbit.error('-- Error publishing message %s at rabbit: connection is closed --', str(msg))
                self.connect()
                self.simple_publish(msg=msg)
            except pika.exceptions.ChannelClosed:
                loggerRabbit.error('-- Error publishing message %s at rabbit: channel is closed --', str(msg))
                self.connect()
                self.simple_publish(msg=msg)
            except pika.exceptions.AMQPConnectionError as e:
                loggerRabbit.error('-- Error publishing message %s at rabbit. AMQP connection error: %s --', str(msg), str(e))
                self.connect()
                self.simple_publish(msg=msg)
            except pika.exceptions.AMQPChannelError as e:
                loggerRabbit.error('-- Error publishing message %s at rabbit. AMQP channel error: %s --', str(msg), str(e))
                self.connect()
                self.simple_publish(msg=msg)
            except Exception as e:
                loggerRabbit.error('-- Error publishing message %s at rabbit: %s --', str(msg), str(e))
                self.connect()
                self.simple_publish(msg=msg)
        else:
            loggerRabbit.error('-- Max retries reached for msg %s --', str(msg))
