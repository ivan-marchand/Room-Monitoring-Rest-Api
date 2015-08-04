from django.shortcuts import render
from django.http import HttpResponse
from TemperatureMonitor.RestApi import models
import json

# Create your views here.
def getTemperature(request, room):
    aJsonDoc = dict()
    aJsonDoc['room'] = room
    # Check if room exists
    aRooms = models.Room.objects.filter(name=room)
    if not aRooms:
        aJsonDoc['error'] = "Room not found"
    else:
        aJsonDoc.update(aRooms[0].getTemperature())
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


