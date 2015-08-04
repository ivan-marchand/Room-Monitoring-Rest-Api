from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate
from TemperatureMonitor.RestApi import models
from TemperatureMonitor import settings

import json
import re
import base64

def login(request, jsonDoc):
    # Only check login in prod
    if settings.DEBUG:
        return True
    user = None
    success = False
    auth = request.META.get('HTTP_AUTHORIZATION')
    m = re.match("[\w\s]+ (?P<credential>[\w=_-]+)", str(auth))
    if m:
        username, password = base64.b64decode(m.group('credential')).split(':')
        user = authenticate(username=username, password=password)
    
    if user is not None:
        # the password verified for the user
        if user.is_active:
            success = True
        else:
            jsonDoc['error'] = "The password is valid, but the account has been disabled!"
    else:
        jsonDoc['error'] = "The username and password were incorrect."
    return success

def getTemperature(request, room):
    aJsonDoc = dict()
    # Logged in ?
    if not login(request, aJsonDoc):
        return HttpResponse(json.dumps(aJsonDoc))

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
    # Logged in ?
    if not login(request, aJsonDoc):
        return HttpResponse(json.dumps(aJsonDoc))

    aJsonDoc['room'] = room
    # Check if room exists
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
    # Success ?
    if 'result' not in aJsonDoc:
        aJsonDoc['result'] = "Failure"

    return HttpResponse(json.dumps(aJsonDoc))

def sendIRCommand(request, room, command):
    aJsonDoc = dict()
    # Logged in ?
    if not login(request, aJsonDoc):
        return HttpResponse(json.dumps(aJsonDoc))

    aJsonDoc['room'] = room
    aJsonDoc['command'] = command
    # Check if room exists
    aRooms = models.Room.objects.filter(name=room)
    if not aRooms:
        aJsonDoc['error'] = "Room not found"
    else:
        aCommands = models.IRCommand.objects.filter(room=aRooms[0],name=command)
        if not aCommands:
            aJsonDoc['error'] = "Command not found"
        else:
            if aCommands[0].send():
                aJsonDoc['result'] = "Success"

    # Success ?
    if 'result' not in aJsonDoc:
        aJsonDoc['result'] = "Failure"
    return HttpResponse(json.dumps(aJsonDoc))

