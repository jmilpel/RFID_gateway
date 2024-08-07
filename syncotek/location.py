import math
from utils import common, decorator
from config import config
# from entities import anchor
from logger import loggerErrors # loggerAnchor, loggerInvestigate


BROKER_AMQP = config.BROKER_AMQP
# BROKER_MQTT = config.BROKER_MQTT

# logger_protocol = loggerAnchor.get_logger()
# logger_investigate = loggerInvestigate.get_logger()
logger_errors = loggerErrors.get_logger()
# anchors = anchor.fill_anchors_data()

@decorator.catch_exceptions
def calculate_distance_on_flat(distance, anchor_id):
    hypotenuse = distance
    distance_on_flat = distance
    # leg = anchors[anchor_id]['coordinates']['z'] - tag_middle_altitude
    partial = math.pow(hypotenuse, 2) - math.pow(leg, 2)
    if partial > 0:
        distance_on_flat = math.sqrt(partial)
    return distance_on_flat


@decorator.catch_exceptions
def manage_received_data(data, publisher):
    header = '7778003010'
    pieces = data.split(header)
    for entry in pieces[1:len(pieces)+1]:
        data = header + entry
        body_length = common.decode_woxu_value(data[12:16])
        sequence = common.decode_woxu_value(data[16:20])
        tag_id = common.decode_woxu_id(data[20:36])
        anchor_id = common.decode_woxu_id(data[36:52])
        distance = common.decode_woxu_value(data[52:60])
        distance_on_flat = calculate_distance_on_flat(distance=distance, anchor_id=anchor_id)
        sos = common.decode_woxu_value(data[60:62])
        battery = common.decode_woxu_value(data[62:64])
        timestamp = common.get_now_timestamp()
        seconds = common.get_seconds_from_midnight(timestamp=timestamp)
        json_msg = {'tag_id': tag_id, 'anchor_id': anchor_id, 'woxu_distance': distance, 'distance': distance_on_flat, 'battery': battery, 'timestamp': timestamp, 'seconds': seconds}
        if distance > 65000:
            logger_errors.info('[ERROR] -- anchor %s -- tag %s -- distance %d cm -- data %s ', anchor_id, tag_id, distance, data)
        else:
            if sos:
                publisher.publish(msg=json_msg)
                # logger_protocol.info('--> [SOS] -- anchor %s -- tag %s -- distance %d cm -- battery %d ', anchor_id, tag_id, distance, battery)
            else:
                if body_length == 71:
                    steps = common.decode_woxu_value(data[150:158])
                    publisher.publish(msg=json_msg)
                    # logger_protocol.info('--> [LOCATION] -- anchor %s -- tag %s -- distance %d cm -- battery %d -- steps %d', anchor_id, tag_id, distance, battery, steps)
                else:
                    publisher.publish(msg=json_msg)
                    # logger_protocol.info('--> [LOCATION] -- anchor %s -- tag %s -- distance %d cm -- battery %d ', anchor_id, tag_id, distance, battery)