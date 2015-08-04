#!/usr/bin/env python
import sys
import os
rootDir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(rootDir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'TemperatureMonitor.settings'

from TemperatureMonitor.RestApi.models import Room, Config
from elasticsearch import Elasticsearch

# Init es connection
es = Elasticsearch([Config.get('ElasticSearchUrl')],port=80)

for aRoom in Room.objects.all():
    if aRoom.server:
        aJsonDoc = dict()
        aJsonDoc['room'] = aRoom.name
        aJsonDoc.update(aRoom.getTemperature())
        print aJsonDoc
        result = es.index(index="roommonitoring", doc_type='temperature', id="%s-%s" % (aRoom.name, aJsonDoc['timestamp']), body=aJsonDoc)

