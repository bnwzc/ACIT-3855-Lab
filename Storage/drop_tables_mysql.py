import mysql.connector
import yaml
with open('user.yml', 'r') as f:
  user = yaml.safe_load(f.read())
db_conn = mysql.connector.connect(host=user['datastore']['hostname'], user=user['datastore']['user'], password=user['datastore']['password'], database=user['datastore']['db'])
db_cursor = db_conn.cursor()
db_cursor.execute('''
    DROP TABLE `match_report`, `disconnection_report`
''')
db_conn.commit()
db_conn.close()