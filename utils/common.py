from utils import decorator
import time
import pytz
import datetime
import binascii
import crc16


@decorator.catch_exceptions
def get_now_timestamp(units='seconds'):
    """ Get now timestamp"""
    now = int(time.time())
    if units == 'ms':
        now = now * 1000
    return now


@decorator.catch_exceptions
def reverse(data):
    """ Reverse hex string in block of two characters """
    result = "".join([data[x:x + 2] for x in range(0, len(data), 2)][::-1])
    return result


@decorator.catch_exceptions
def convert_int_to_hex_string(number):
    """ Convert integer to hex string """
    return format(number, 'x')


@decorator.catch_exceptions
def decode_woxu_value(value):
    reverse_string = "".join([value[x:x+2] for x in range(0, len(value), 2)][::-1])
    return int(reverse_string, 16)


@decorator.catch_exceptions
def decode_woxu_id(hardware_id):
    result = ''
    for x in range(0, len(hardware_id), 2)[::-1]:
        if hardware_id[x:x+2] != '00' or result:
            result += (hardware_id[x:x+2].upper())
    if len(result) == 4:
        result = '00' + result
    return result


@decorator.catch_exceptions
def encode_woxu_ip(ip):
    """ Format string ip address for WOXU DISCOVERY packet """
    result = ''
    ascii_string = '%d'*len(ip) % tuple(map(ord, ip))
    for x in range(0, len(ascii_string), 2):
        _ = ascii_string[x:x + 2]
        result += format(int(_), 'x')
    length = len(result)
    if length < 32:
        added = "0" * (32-length)
        result += added
    return result


@decorator.catch_exceptions
def format_date():
    """ Format date for WOXU DISCOVERY packet"""
    now = get_now_timestamp(units='ms')
    now_hex = convert_int_to_hex_string(number=now)
    if len(now_hex) % 2 != 0:
        now_hex = '0' + now_hex
    result = reverse(now_hex)
    length = len(result)
    if length < 16:
        added = "0" * (16-length)
        result += added
    return result


@decorator.catch_exceptions
def get_seconds_from_midnight(timestamp):
    """ Get UTC timestamp in seconds at 00:00 from UTC timestamp"""
    tz = pytz.timezone('UTC')
    date_utc = datetime.datetime.fromtimestamp(timestamp, tz)
    string_date_midnight = date_utc.strftime("%Y-%m-%d") + " 00:00:00"
    new_object = tz.localize(datetime.datetime.strptime(string_date_midnight, '%Y-%m-%d %H:%M:%S'))
    midnight_timestamp = int((new_object - datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds())
    return timestamp - midnight_timestamp


@decorator.catch_exceptions
def calculate_woxu_checksum(data):
    """ calculate WOXU WIRELESS checksum for hex string """
    hex_checksum = convert_int_to_hex_string(crc16.crc16xmodem(bytes.fromhex(data)))
    if len(hex_checksum) < 4:
        zero_added = 4 - len(hex_checksum)
        hex_checksum = '0'*zero_added + hex_checksum
    result = reverse(hex_checksum)
    return result


@decorator.catch_exceptions
def convert_int_to_hex_string_with_length(number, length):
    """ Convert integer to hex string """
    str_hex = format(number, 'x')
    zero_added = length - len(str_hex)
    result = reverse('0'*zero_added + str_hex)
    return result


@decorator.catch_exceptions
def encode_woxu_id(value_id, length):
    reverse_string = reverse(value_id)
    zero_size = length - len(reverse_string)
    result = reverse_string + '0'*zero_size
    return result


@decorator.catch_exceptions
def encode_woxu_coordinate(number, length=8):
    _ = hex((number + (1 << 32)) % (1 << 32))
    str_hex = _.replace('0x', '')
    result = reverse(str_hex)
    zero_size = length - len(result)
    if zero_size:
        result = result + '0' * zero_size
    return result


@decorator.catch_exceptions
def convert_data_to_hexstring(data):
    return binascii.hexlify(data).decode()


@decorator.catch_exceptions
def convert_str_to_bin(string):
    bin_text = ' '.join(format(ord(char), '08b') for char in string)
    return bin_text


@decorator.catch_exceptions
def convert_str_to_hex(string):
    return bytes.fromhex(string)


@decorator.catch_exceptions
def convert_str_to_hex_to_int(string):
    hex_bytes = bytes.fromhex(string)
    return int.from_bytes(hex_bytes, byteorder="big")


@decorator.catch_exceptions
def convert_hex_to_bin(hex_value):
    return bin(int(hex_value, 16))[2:]


def convert_hex_to_int(hex_value):
    return int(hex_value, 16)


def convert_bin_to_dec(bin_value):
    return int(bin_value, 2)


def print_tags(table):
    print("\n")
    print("|Nº\t|PC\t|EPC\t\t\t\t\t\t|CRC\t|RSSI\t|CNT\t|ANT\t|")
    print("---------------------------------------------------------------------")

    iterator = iter(table)
    index = 1

    while True:
        try:
            element = next(iterator)
            print(
                f"{index}\t|{element['PC']}|{element['EPC']}\t|{element['CRC']}\t|{element['RSSI']}\t|{element['CNT']}"
                f"\t\t|{element['ANT']}\t\t|")
            index += 1
        except StopIteration:
            break


def int_rssi(rssi):
    return convert_str_to_hex_to_int(rssi) - 255
