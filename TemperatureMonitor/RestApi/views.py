from django.shortcuts import render
from django.http import HttpResponse
from TemperatureMonitor.RestApi import models
import json
import urllib, httplib2

# Create your views here.
def getTemperature(request, room):
    aJsonDoc = dict()
    aJsonDoc['room'] = room
    aRooms = models.Room.objects.filter(name=room)
    if room == 'baby':
        aJsonDoc['temperature'] = getTemperatureFromServer(room)
    elif not aRooms:
        aJsonDoc['error'] = "Room not found"
    else:
        aRoom = aRooms[0]
        aJsonDoc['temperature'] = aRoom.temperature
    return HttpResponse(json.dumps(aJsonDoc))


def getTemperatureFromServer(room):
    host = models.Config.get('host')
    port = models.Config.get('port')
    path = models.Config.get('path')

    url = "http://%s:%s/%s" % (host, port, path)

    h = httplib2.Http(".cache") # WAT?
    resp, content = h.request(url)

    return json.loads(content)['value'].split('.')[0]

