import connexion
from connexion import NoContent
from manage_db import engine, make_session
from models import MatchReport, DisconnectionReport
import yaml
import logging
import logging.config
import datetime
from sqlalchemy import and_


MAX_EVENTS = 5
EVENT_FILE = "events.json"

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())

logger = logging.getLogger('basicLogger')


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

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    logging.config.dictConfig(log_config)
    app.run(port=8090)
