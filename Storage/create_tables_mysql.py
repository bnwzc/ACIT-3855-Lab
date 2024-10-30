import mysql.connector
import yaml
import logging
import logging.config
from datetime import datetime

with open('user.yml', 'r') as f:
  user = yaml.safe_load(f.read())
db_conn = mysql.connector.connect(host=user['datastore']['hostname'], user=user['datastore']['user'], password=user['datastore']['password'])
db_cursor = db_conn.cursor()


with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())

logger = logging.getLogger('basicLogger')


logger.info(f"{datetime.now()} - basiclogger - INFO - Connecting to DB. Hostname:{user['datastore']['hostname']}, Port:{user['datastore']['port']}")


db_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {user['datastore']['db']}")
db_cursor.execute(f"USE {user['datastore']['db']}")

db_cursor.execute('''
CREATE TABLE `match_report` (
  `match_id` VARCHAR(50) NOT NULL,
  `rank` VARCHAR(50) NOT NULL,
  `winner` TINYINT NOT NULL,
  `timestamp` DATETIME NOT NULL,
  `duration` FLOAT NOT NULL,
  `trace_id` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`match_id`))
''')
db_cursor.execute('''
CREATE TABLE `disconnection_report` (
  `disconnection_id` VARCHAR(50) NOT NULL,
  `region` VARCHAR(50) NOT NULL,
  `server` VARCHAR(50) NOT NULL,
  `timestamp` DATETIME NOT NULL,
  `duration` FLOAT NOT NULL,
  `latency` INT NOT NULL,
  `trace_id` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`disconnection_id`))
''')
db_conn.commit()
db_conn.close()