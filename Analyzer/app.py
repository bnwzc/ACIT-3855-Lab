import connexion
from connexion import NoContent
import requests
import yaml
import logging
import logging.config
import uuid
import datetime
import json
from pykafka import KafkaClient

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())

logger = logging.getLogger('basicLogger')

def get_match_reading(index):
    """ Get BP Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 1000ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    logger.info("Retrieving Match at index %d" % index)
    count_match = -1
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200
            if msg['type'] == 'mt':
                count_match = count_match + 1
            if count_match == index and msg['type'] == 'mt':
                return msg, 200
    except Exception as e:
        logger.error("Error while processing messages: %s", e)

    logger.error("No more messages found")
    logger.error("Could not find Match at index %d" % index)
    return {"message": "Not Found"}, 404
    

def get_disconnection_reading(index):
    """ Get BP Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 1000ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    logger.info("Retrieving Disconnection at index %d" % index)
    count_disconnection = -1
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200
            print(index)
            if msg['type'] == 'dc':
                print(count_disconnection)
                count_disconnection = count_disconnection + 1
            if count_disconnection == index and msg['type'] == 'dc':
                return msg, 200
    except Exception as e:
        logger.error("Error while processing messages: %s", e)

    logger.error("No more messages found")
    logger.error("Could not find Disconnection at index %d" % index)
    return {"message": "Not Found"}, 404

def get_event_stats():
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    stats = {
        "num_match": 0,
        "num_disconnection": 0,
    }

    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            event = json.loads(msg_str)
            if event['type'] == 'mt':
                stats["num_match"] += 1
            elif event['type'] == 'dc':
                stats["num_disconnection"] += 1

    except Exception as e:
        logger.error("Error while processing messages: %s", e)

    return stats, 200

    


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    logging.config.dictConfig(log_config)
    app.run(port=8110)
