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
    if not aRooms:
        aJsonDoc['error'] = "Room not found"
    elif aRooms[0].server:
        aJsonDoc['temperature'] = getTemperatureFromServer(aRooms[0])
    else:
        aJsonDoc['temperature'] = aRooms[0].temperature
    return HttpResponse(json.dumps(aJsonDoc))

def setTempThreshold(request, room, type, temperature):
    aJsonDoc = dict()
    aJsonDoc['room'] = room
    aRooms = models.Room.objects.filter(name=room)
    if not aRooms:
        aJsonDoc['error'] = "Room not found"
    else:
        aRoom = aRooms[0]
        if type == 'high':
            aRoom.high_threshold = int(temperature)
            aRoom.save()
            aJsonDoc['result'] = "Success"
        elif type == 'low':
            aRoom.low_threshold = int(temperature)
            aRoom.save()
            aJsonDoc['result'] = "Success"
        else:
            aJsonDoc['error'] = "Unknown type : %s" % type
    return HttpResponse(json.dumps(aJsonDoc))

def getTemperatureFromServer(room):

    url = "http://%s:%s/arduino/getTemp/F" % (room.server.host, room.server.port)

    h = httplib2.Http(".cache") # WAT?
    resp, content = h.request(url)

    return json.loads(content)['temperature']

