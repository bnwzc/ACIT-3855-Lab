import connexion
from connexion import NoContent
import requests
import yaml
import logging
import logging.config
import uuid

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
    response = requests.post(
        app_config["match"]["url"],
        json=body,
        headers={'Content-Type': 'application/json'}
    )
    logger.info(f"Returned event match response {trace_id} with status {response.status_code}.")
    return NoContent, response.status_code


def report_dota2_disconnection(body):
    trace_id = str(uuid.uuid4())
    logger.info(f"Received event disconnection request with a trace id of {trace_id}.")
    body['trace_id'] = trace_id
    response = requests.post(
        app_config["disconnection"]["url"],
        json=body,
        headers={'Content-Type': 'application/json'}
    )
    logger.info(f"Returned event disconnection response {trace_id} with status {response.status_code}.")
    return NoContent, response.status_code 
            

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    logging.config.dictConfig(log_config)
    app.run(port=8080)

