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
import os



MAX_EVENTS = 5
EVENT_FILE = "events.json"

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())

logger = logging.getLogger('basicLogger')



if not os.path.exists("index.txt"):
    with open("index.txt", 'w') as f:
        f.write('0,0')
with open("index.txt", 'r') as f:
    content = f.read()
    match_index, disconnection_index = content.split(',')
    match_index = int(match_index)
    disconnection_index = int(disconnection_index)
def report_dota2_match(body):
    global match_index
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
        "index": match_index,
        "type": "mt",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    match_index = match_index + 1
    with open("index.txt", 'w') as f:
        f.write(f"{match_index},{disconnection_index}")
    return NoContent, 201 


def report_dota2_disconnection(body):
    global disconnection_index
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
        "index": disconnection_index, 
        "type": "dc",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    disconnection_index = disconnection_index + 1
    with open("index.txt", 'w') as f:
        f.write(f"{match_index},{disconnection_index}")
    return NoContent, 201 
            

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    logging.config.dictConfig(log_config)
    app.run(port=8080)

