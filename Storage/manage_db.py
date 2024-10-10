from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import yaml

with open('user.yml', 'r') as f:
    user = yaml.safe_load(f.read())
    
engine = create_engine(f"mysql+mysqldb://{user['datastore']['user']}:{user['datastore']['password']}@{user['datastore']['hostname']}:{user['datastore']['port']}/{user['datastore']['db']}")


def make_session():
    return sessionmaker(bind=engine)()
