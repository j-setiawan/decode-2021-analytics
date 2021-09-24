import uuid
from datetime import datetime
from elasticsearch import Elasticsearch
from random import randrange

emotions = ['happy', 'sad', 'confused', 'frustrated']

with open('db.properties') as fp:
    lines = fp.readlines()
    cloudId = lines[0].strip()
    apiKey = lines[1].strip()

es = Elasticsearch(
    cloud_id=cloudId,
    api_key=apiKey
)


def from_solace(s_index, payload):
    payload['timestamp'] = datetime.now()
    doc = {s_index: payload}
    res = es.index(index=s_index, body=doc)
    print(res['result'])


# for i in range(500):
#     from_solace('decode_emotes', {'studentId': str(uuid.uuid4()), 'emotion': emotions[randrange(len(emotions))]})
