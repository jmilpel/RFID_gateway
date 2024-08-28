from utils import decorator
import time
import pytz
import datetime
import binascii
# import crc16
# import fastcrc


def crc16_genibus(input_string):
    """ Check the CRC value (Not tested) """
    # crc16.crc16xmodem(bytes.fromhex(data)
    preset_value = 0xFFFF
    polynomial = 0x8408

    input_bytes = bytes.fromhex(input_string)
    ui_crc_value = preset_value
    for uc_i in range(len(input_bytes)):
        ui_crc_value ^= input_bytes[uc_i]
    for uc_j in range(8):
        if ui_crc_value & 0x0001:
            ui_crc_value = (ui_crc_value >> 1) ^ polynomial
        else:
            ui_crc_value = (ui_crc_value >> 1)
    return f"{ui_crc_value:04x}"


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
def get_seconds_from_midnight(timestamp):
    """ Get UTC timestamp in seconds at 00:00 from UTC timestamp"""
    tz = pytz.timezone('UTC')
    date_utc = datetime.datetime.fromtimestamp(timestamp, tz)
    string_date_midnight = date_utc.strftime("%Y-%m-%d") + " 00:00:00"
    new_object = tz.localize(datetime.datetime.strptime(string_date_midnight, '%Y-%m-%d %H:%M:%S'))
    midnight_timestamp = int((new_object - datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds())
    return timestamp - midnight_timestamp


@decorator.catch_exceptions
def convert_int_to_hex_string_with_length(number, length):
    """ Convert integer to hex string """
    str_hex = format(number, 'x')
    zero_added = length - len(str_hex)
    result = reverse('0'*zero_added + str_hex)
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
