from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate
from TemperatureMonitor.RestApi import models
from TemperatureMonitor import settings
from TemperatureMonitor.plugins.loader import AbstractPlugin

import json
import re
import base64
import threading
import requests
import traceback
from fuzzywuzzy import fuzz
from wit import Wit

def testCredential(request):
    aJsonDoc = dict()
    # Try to login
    return HttpResponse(json.dumps({'success': login(request, aJsonDoc, True)}))

def login(request, jsonDoc, force=False):
    # Only check login in prod
    if not force and settings.DEBUG:
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

def getRoomList(request):
    aJsonDoc = dict()

    aJsonDoc["action"] = "getRoomList"
    
    # Logged in ?
    if not login(request, aJsonDoc):
        return HttpResponse(json.dumps(aJsonDoc))

    aRoomList = []
    for aRoom in models.Room.objects.all():
        aRoomList.append(aRoom.name)
    aJsonDoc["room_list"] = aRoomList
        
    return HttpResponse(json.dumps(aJsonDoc))

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

def getAvailablePlugins(request):
    aJsonDoc = dict()
    # Logged in ?
    if not login(request, aJsonDoc):
        return HttpResponse(json.dumps(aJsonDoc))

    # Get Plugin from Db
    aJsonDoc['types'] = AbstractPlugin.GetAvailablePlugin()
        
    return HttpResponse(json.dumps(aJsonDoc))

def getPlugins(request):
    aJsonDoc = dict()
    # Logged in ?
    if not login(request, aJsonDoc):
        return HttpResponse(json.dumps(aJsonDoc))

    # Get Plugin from Db
    aJsonDoc['plugins'] = []
    for aPlugin in models.Plugin.objects.all():
        aJsonDoc['plugins'].append(aPlugin.getAsJson(True))
        
    return HttpResponse(json.dumps(aJsonDoc))

def getPlugin(request, id):
    aJsonDoc = dict()
    # Logged in ?
    if not login(request, aJsonDoc):
        return HttpResponse(json.dumps(aJsonDoc))

    # Get Plugin from Db
    aPlugin = models.Plugin.GetById(int(id))
    if aPlugin:
        aJsonDoc['plugin'] = aPlugin.getAsJson(True)
    else:
        aJsonDoc['error'] = "Plugin not found"
        
    return HttpResponse(json.dumps(aJsonDoc))
    
def updatePlugin(request, id, name, type):
    aJsonDoc = dict()
    # Logged in ?
    if not login(request, aJsonDoc):
        return HttpResponse(json.dumps(aJsonDoc))

    # Decode config (if any)
    aPluginConfig = None
    if len(request.body) > 0:
        try:
            aPostedJson = json.loads(request.body)
            if 'config' in aPostedJson:
                aPluginConfig = aPostedJson['config']
        except:
            aJsonDoc['error'] = "Unable to decode plugin config"
    
    # Check if plugin already exists
    aPlugin = models.Plugin.GetById(int(id))
    if not aPlugin:
        aJsonDoc['error'] = "Plugin not found"
    
    if 'error' not in aJsonDoc:
        # Update the plugin
        aPlugin.name = name
        aPlugin.type = type
        aPlugin.save()
        
        # Add Plugin config if any
        aPlugin.cleanConfig()
        if aPluginConfig:
            for key, value in aPluginConfig.items():
                aPlugin.addConfig(key, value)

        aJsonDoc['plugin'] = aPlugin.getAsJson(False)
    return HttpResponse(json.dumps(aJsonDoc))

def addPlugin(request, name, type):
    aJsonDoc = dict()
    # Logged in ?
    if not login(request, aJsonDoc):
        return HttpResponse(json.dumps(aJsonDoc))

    # Decode config (if any)
    aPluginConfig = None
    if len(request.body) > 0:
        try:
            aPostedJson = json.loads(request.body)
            if 'config' in aPostedJson:
                aPluginConfig = aPostedJson['config']
        except:
            aJsonDoc['error'] = "Unable to decode plugin config"
    
    # Check if plugin already exists
    if models.Plugin.Get(name=name, type=type):
        aJsonDoc['error'] = "Plugin %s already exists" % name
    
    if 'error' not in aJsonDoc:
        # Add the Plugin
        aPlugin = models.Plugin(name=name, type=type)
        aPlugin.save()
        
        # Add Plugin config if any
        if aPluginConfig:
            for key, value in aPluginConfig.items():
                aPlugin.addConfig(key, value)

        aJsonDoc['plugin'] = aPlugin.getAsJson(False)
    return HttpResponse(json.dumps(aJsonDoc))

def delPlugin(request, id):
    aJsonDoc = dict()
    # Logged in ?
    if not login(request, aJsonDoc):
        return HttpResponse(json.dumps(aJsonDoc))

    # Get Plugin from Db
    aPlugin = models.Plugin.GetById(int(id))
    if aPlugin:
        aJsonDoc['plugin'] = aPlugin.getAsJson(False)
        aPlugin.delete()
    else:
        aJsonDoc['error'] = "Plugin not found"
        
    return HttpResponse(json.dumps(aJsonDoc))



def send(request, response):
    print "Request:", request
    print "Response:", response
    sendTextMessage(request['context']['senderId'], response['text'])

def getTemperature(request):
    print request
    # Check if room exists
    if 'roomName' in request['entities']:
	aSelectedRoom = None
        aBestScore = 0
        for query in request['entities']['roomName']:
            for aRoom in models.Room.objects.all():
                aScore = fuzz.partial_ratio(query['value'], aRoom.name)
                if aScore > aBestScore:
                    aBestScore = aScore
                    aSelectedRoom = aRoom
	if not aSelectedRoom or aBestScore < 70:
            sendTextMessage(request['context']['senderId'], "I don't know this room \"%s\"" % query['value'])
        else:
            sendTextMessage(request['context']['senderId'], "Temperature in room %s is %.1f F" % (aSelectedRoom.name, aSelectedRoom.getTemperature()['temperature']))
    else:
        sendTextMessage(request['context']['senderId'], "Which room?")

actions = {
    'send': send,
    'getTemperature': getTemperature
}

        

def bot(request):
    try:
        if 'hub.verify_token' in request.GET:
            if request.GET['hub.verify_token'] == models.Config.get('FacebookVerifyToken'):
                if 'hub.challenge' in request.GET:
                    return HttpResponse(request.GET['hub.challenge'])
                return HttpResponse("KO")
        body = json.loads(request.body)
        print body
        for entry in body['entry']:
            for message in entry['messaging']:
                if 'is_echo' not in message and 'message' in message:
                    senderId = message['sender']['id']
                    client = Wit(access_token=models.Config.get('WitToken'), actions=actions)
                    client.run_actions("session", message['message']['text'], {'senderId': senderId})
    except Exception, e:
        traceback.print_exc()
  
    return HttpResponse()

def sendTextMessage(recipientId, messageText):
    messageData = {
                'recipient': {
                          'id': recipientId
                          },
                'message': {
                          'text': messageText
                          }
                }

    callSendAPI(messageData)

def callSendAPI(messageData):
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", json=messageData, params={'access_token': models.Config.get('FacebookToken')})
    print r.status_code, r.reason
    
