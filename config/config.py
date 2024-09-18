import os
from configobj import ConfigObj

BASE = os.path.dirname(os.path.abspath(__file__))
CONFIG = ConfigObj(os.path.join(BASE, 'config.cfg'))

READER = CONFIG['reader']
INTERFACE = CONFIG['interface']
LOG = CONFIG['log']
BROKER_AMQP = CONFIG['broker_amqp']

LOG_FOLDER = LOG['folder']
LOG_DAYS_FOR_ROTATE = LOG['days_for_rotate']
LOG_GATEWAY_FILE = LOG['gateway_file']
LOG_RABBIT_FILE = LOG['rabbit_file']
