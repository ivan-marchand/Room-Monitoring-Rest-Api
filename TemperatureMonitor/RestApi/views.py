from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate
from TemperatureMonitor.RestApi import models
from TemperatureMonitor import settings

import json
import re
import base64
import threading

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

# Function used for multi threading
def GetRoom(s, room, result):
    aRoomJsonDoc = dict()
    aRoomJsonDoc['room'] = room.name
    aRoomJsonDoc.update(room.getTemperature())
    
    # Get list of device in the room
    aRoomJsonDoc['devices'] = []
    for aDevice in models.Device.objects.filter(room = room, actif = True):
        aDeviceJson = dict()
        aDeviceJson['name'] = aDevice.name
        aDeviceJson['type'] = aDevice.type
        aDeviceJson['commands'] = []
        # Get list of commands for this device
        for aCommand in models.IRCommand.objects.filter(device = aDevice):
            aCommandJson = dict()
            aCommandJson['name'] = aCommand.name
            aCommandJson['text'] = aCommand.text
            aCommandJson['type'] = "IR"
            aDeviceJson['commands'].append(aCommandJson)
        aRoomJsonDoc['devices'].append(aDeviceJson)

    # Ensure no one else is accessing the list
    s.acquire()
    result.append(aRoomJsonDoc)
    s.release()
    return

def getRooms(request):
    aJsonDoc = []

    # Logged in ?
    if not login(request, aJsonDoc):
        return HttpResponse(json.dumps(aJsonDoc))

    # Use semaphore to make sure that there is no concurrent access to aJsonDoc
    s = threading.Semaphore()

    # Start one thread by room
    threads = []
    for aRoom in models.Room.objects.all():
        t = threading.Thread(target=GetRoom, args=(s, aRoom, aJsonDoc, ))
        t.start()
        threads.append(t)
        
    # Wait for completion
    for t in threads:
        t.join()

    return HttpResponse(json.dumps(aJsonDoc))

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

def sendIRCommand(request, device, command):
    aJsonDoc = dict()
    # Logged in ?
    if not login(request, aJsonDoc):
        return HttpResponse(json.dumps(aJsonDoc))

    aJsonDoc['device'] = device
    aJsonDoc['command'] = command
    # Check if room exists
    aDevices = models.Device.objects.filter(name=device)
    if not aDevices:
        aJsonDoc['error'] = "Device not found"
    else:
        aCommands = models.IRCommand.objects.filter(device=aDevices[0], name=command)
        if not aCommands:
            aJsonDoc['error'] = "Command not found"
        else:
            if aCommands[0].send():
                aJsonDoc['result'] = "Success"

    # Success ?
    if 'result' not in aJsonDoc:
        aJsonDoc['result'] = "Failure"
    return HttpResponse(json.dumps(aJsonDoc))

