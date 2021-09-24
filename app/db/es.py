import uuid
from datetime import datetime
from elasticsearch import Elasticsearch
from random import randrange

emotions = ['happy', 'sad', 'confused', 'frustrated']

with open('db.properties') as fp:
    lines = fp.readlines()
    hostname = lines[0].strip()
    username = lines[1].strip()
    password = lines[2].strip()

es = Elasticsearch(
    hostname,
    http_auth=(username, password)
)


def from_solace(s_index, payload):
    payload['timestamp'] = datetime.now()
    doc = {s_index: payload}
    es.index(index=s_index, body=doc)


# for i in range(500):
#     from_solace('decode_emotes', {'studentId': str(uuid.uuid4()), 'emotion': emotions[randrange(len(emotions))]})
