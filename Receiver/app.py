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

MAX_EVENTS = 5
EVENT_FILE = "events.json"

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())

logger = logging.getLogger('basicLogger')


def report_dota2_match(body):
    trace_id = str(uuid.uuid4())
    logger.info(f"Received event match request with a trace id of {trace_id}.")
    body['trace_id'] = trace_id
    # response = requests.post(
    #     app_config["match"]["url"],
    #     json=body,
    #     headers={'Content-Type': 'application/json'}
    # )
    # logger.info(f"Returned event match response {trace_id} with status {response.status_code}.")
    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode(f"{app_config['events']['topic']}")]
    producer = topic.get_sync_producer()
    msg = {
        "type": "mt",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    return NoContent, 201 


def report_dota2_disconnection(body):
    trace_id = str(uuid.uuid4())
    logger.info(f"Received event disconnection request with a trace id of {trace_id}.")
    body['trace_id'] = trace_id
    # response = requests.post(
    #     app_config["disconnection"]["url"],
    #     json=body,
    #     headers={'Content-Type': 'application/json'}
    # )
    # logger.info(f"Returned event disconnection response {trace_id} with status {response.status_code}.")
    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode(f"{app_config['events']['topic']}")]
    producer = topic.get_sync_producer()
    msg = {
        "type": "dc",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    return NoContent, 201 
            

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    logging.config.dictConfig(log_config)
    app.run(port=8080)

