import connexion
from connexion import NoContent
from manage_db import engine, make_session
from models import MatchReport, DisconnectionReport
import yaml
import logging
import logging.config
import datetime
from sqlalchemy import and_
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType 
from threading import Thread



MAX_EVENTS = 5
EVENT_FILE = "events.json"
with open('user.yml', 'r') as f:
    user = yaml.safe_load(f.read())
with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

logger = logging.getLogger('basicLogger')

logger.info(f"{datetime.datetime.now()} - basiclogger - INFO - Connecting to DB. Hostname:{user['datastore']['hostname']}, Port:{user['datastore']['port']}")

def report_dota2_match(body):
    session = make_session()
    new_match = MatchReport(
        match_id=body["match_id"],
        rank=body["rank"],
        winner=body["winner"],
        duration=body["duration"],
        trace_id=body["trace_id"]
    )
    
    
    session.add(new_match)
    session.commit()
    logger.info(f"Stored event match request with a trace id of {new_match.trace_id}.")
    session.close()

    return NoContent, 201


   

def report_dota2_disconnection(body):
    session = make_session()
    new_disconnection = DisconnectionReport(
        disconnection_id=body["disconnection_id"],
        region=body["region"],
        server=body["server"],
        duration=body["duration"],
        latency=body["latency"],
        trace_id=body["trace_id"]
    )
    session.add(new_disconnection)
    session.commit()
    logger.info(f"Stored event disconnection request with a trace id of {new_disconnection.trace_id}.")
    session.close()

    return NoContent, 201

def get_match_readings(start_timestamp, end_timestamp):
    session = make_session()
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S")
    results = session.query(MatchReport).filter(
        and_(MatchReport.timestamp >= start_timestamp_datetime, MatchReport.timestamp < end_timestamp_datetime)
    )
    results_list = []
    for result in results:
        results_list.append(result.to_dict())
    session.close()
    logger.info("Query for match readings after %s returns %d results" % (start_timestamp, len(results_list)))
    return results_list, 200

def get_disconnection_readings(start_timestamp, end_timestamp):
    session = make_session()
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S")
    results = session.query(DisconnectionReport).filter(
        and_(DisconnectionReport.timestamp >= start_timestamp_datetime, DisconnectionReport.timestamp < end_timestamp_datetime)
    )
    results_list = []
    for result in results:
        results_list.append(result.to_dict())
    session.close()
    logger.info("Query for disconnection readings after %s returns %d results" % (start_timestamp, len(results_list)))
    return results_list, 200

def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group', reset_offset_on_start=False, auto_offset_reset=OffsetType.LATEST)
    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]
        if msg["type"] == "mt": # Change this to your event type
            # Store the event1 (i.e., the payload) to the DB
            report_dota2_match(payload)
        elif msg["type"] == "dc": # Change this to your event type
            # Store the event2 (i.e., the payload) to the DB
            report_dota2_disconnection(payload)
        # Commit the new message as being read
        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    logging.config.dictConfig(log_config)
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)
    

