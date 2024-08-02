import os
from configobj import ConfigObj

BASE = os.path.dirname(os.path.abspath(__file__))
CONFIG = ConfigObj(os.path.join(BASE, 'config.cfg'))

SERIAL = CONFIG['serial']
SERVER = CONFIG['server']
CLIENT = CONFIG['client']
UWB = CONFIG['uwb']
LOG = CONFIG['log']
BROKER_AMQP = CONFIG['broker_amqp']
BROKER_MQTT = CONFIG['broker_mqtt']
MONGO = CONFIG['mongo']

LOG_FOLDER = LOG['folder']
LOG_DAYS_FOR_ROTATE = LOG['days_for_rotate']
LOG_MAIN_FILE = LOG['main_file']
LOG_MONGO_FILE = LOG['mongo_file']
LOG_RABBIT_FILE = LOG['rabbit_file']
LOG_ANCHOR_FILE = LOG['anchor_file']
LOG_TAG_FILE = LOG['tag_file']
LOG_INVESTIGATE_FILE = LOG['investigate_file']
LOG_ERRORS_FILE = LOG['errors_file']
