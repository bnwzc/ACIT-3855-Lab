import connexion
from connexion import NoContent
import yaml
import logging
import logging.config
import datetime
from datetime import datetime
from sqlalchemy import and_
from apscheduler.schedulers.background import BackgroundScheduler
import json
import requests
from flask import jsonify


with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())

logger = logging.getLogger('basicLogger')

DEFAULT = {
    'num_match_readings': 0,
    'num_disconnection_readings': 0,
    'max_match_duration': 0,
    'max_disconnection_latency': 0,
    'last_updated': datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
}



def get_stats():
    logger.info("Start get stats")
    file = app_config["datastore"]["filename"]
    try:
        with open(file, "r") as f:
            stats_data = json.load(f)
        logger.debug(f"Statistics data: {stats_data}")
        
    except FileNotFoundError:
        logger.error("Statistics do not exist")
        return 404
        
    return jsonify(stats_data), 200
    
def populate_stats():
    logger.info("Start Periodic Processing")
    
    file = app_config["datastore"]["filename"]
    try:
        with open(file, "r") as f:
            stats = json.load(f)
            start_timestamp = stats["last_updated"]
            end_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            stats["last_updated"] = end_timestamp

    except FileNotFoundError:
        stats = DEFAULT
        start_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        end_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            
    match_responses= requests.get(app_config["eventstore"]["url"] + "/dota2/match_reading", params={"start_timestamp": start_timestamp, "end_timestamp": end_timestamp})
    disconnection_responses = requests.get(app_config["eventstore"]["url"] + "/dota2/disconnection_reading", params={"start_timestamp": start_timestamp, "end_timestamp": end_timestamp})
    if match_responses.status_code == 200:
        logger.info(f"Number of match events received: {len(match_responses.json())}")
    else:
        logger.error(f"Error fetching match events: {match_responses.status_code}")
    if disconnection_responses.status_code == 200:
        logger.info(f"Number of disconnection events received: {len(disconnection_responses.json())}")
    else:
        logger.error(f"Error fetching disconnection events: {disconnection_responses.status_code}")
        
    stats["num_match_readings"] = stats["num_match_readings"] + len(match_responses.json())
    stats["num_disconnection_readings"] = stats["num_disconnection_readings"] + len(disconnection_responses.json())
    for i in match_responses.json():
        if float(i["duration"]) > float(stats["max_match_duration"]):
            stats["max_match_duration"] = i["duration"]
    for i in disconnection_responses.json():
        if int(i["latency"]) > int(stats["max_disconnection_latency"]):
            stats["max_disconnection_latency"] = i["latency"]
        
    with open(file, "w") as f:
        json.dump(stats, f, indent=4)

    logger.info("End Periodic Processing")

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    logging.config.dictConfig(log_config)
    app.run(port=8100)
