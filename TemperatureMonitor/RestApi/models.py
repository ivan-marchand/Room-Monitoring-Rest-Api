from django.db import models
from datetime import datetime
from django.utils import timezone
from itertools import repeat
from django.db.models.fields import BooleanField
from django.template.defaultfilters import default
from TemperatureMonitor.plugins.loader import ServerPlugin


class Server(models.Model):
    name = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=1, choices=ServerPlugin.GetTypes())

    @staticmethod
    def Get(name, type):
        aServers = Server.objects.filter(name=name, type=type)
        if len(aServers) > 0:
            return aServers[0]
        return None
    
    @staticmethod
    def GetById(id):
        aServers = Server.objects.filter(id=id)
        if len(aServers) > 0:
            return aServers[0]
        return None

    def getConfig(self, key):
        aConfigs = ServerConfig.objects.filter(server = self, key = key)
        if len(aConfigs):
            return aConfigs[0].value
        return None

    def addConfig(self, key, value):
        aConfig = ServerConfig(server = self, key = key, value=value)
        aConfig.save()

    def cleanConfig(self):
        for aConfig in ServerConfig.objects.filter(server=self):
            aConfig.delete()

    def getAsJson(self, getConfig):
        aJson = dict()
        aJson['name'] = self.name
        aJson['type'] = self.type
        aJson['id'] = self.id
        
        if getConfig:
            aJson['config'] = dict()
            for aConfig in ServerConfig.objects.filter(server=self):
                aJson['config'][aConfig.key] = aConfig.value
        return aJson

    def __str__(self):
        return "%s (%s)" % (self.name, self.get_type_display())

class ServerConfig(models.Model):
    server = models.ForeignKey('Server')
    key = models.CharField(max_length=20)
    value = models.CharField(max_length=200)

    def __str__(self):
        return "%s - %s" % (self.server, self.key)

class Room(models.Model):
    name = models.CharField(max_length=20, unique=True)
    server = models.ForeignKey('Server')

    def __str__(self):
        return self.name

    def getTemperatureFromServer(self):
        aResult = dict()
        serverPlugin = ServerPlugin.Get(self.server)
        if serverPlugin:
            if serverPlugin.hasService('getTemperature'):
                aResult = serverPlugin.getTemperature()
        else:
            aResult['error'] = "Unknown server type %s" % self.server.type
        
        return aResult

    def getTemperature(self, simulateRoom=False):
        aJsonDoc = dict()
        # Timestamp (on server time zone)
        now = datetime.now().replace(microsecond=0)
        aJsonDoc['timestamp'] = now.isoformat() 
        # Check if server is defined
        aResult = self.getTemperatureFromServer()
        if 'temperature' in aResult:
            aJsonDoc['temperature'] = float(aResult['temperature'])
        if 'humidity' in aResult:
            aJsonDoc['humidity'] = float(aResult['humidity'])
        if 'error' in aResult:
            aJsonDoc['error'] = aResult['error']

        return aJsonDoc

class Device(models.Model):
    TYPES = (
        ('A', 'A/C'),
        ('H', 'Heater'),
    )
    room = models.ForeignKey('Room')
    name = models.CharField(max_length=30, unique=True)
    type = models.CharField(max_length=1, choices=TYPES)
    actif = models.BooleanField(default=False)

    def __str__(self):
        return "%s (%s)" % (self.name, self.get_type_display())

class IRCommand(models.Model):
    device = models.ForeignKey('Device')
    name = models.CharField(max_length=20)
    text = models.CharField(max_length=20)
    protocol = models.CharField(max_length=20)
    hexCode = models.CharField(max_length=16)
    nbBits = models.IntegerField()
    repeat = models.IntegerField(default=1)
    minWaitBetweenRepeat = models.IntegerField(null=True, blank=True)
    lastSend = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return "%s-%s" % (self.device.name, self.name)

    def send(self):
        aReturnCode = False
        # Repeat?
        repeat = 0
        if self.repeat:
            if self.lastSend and self.minWaitBetweenRepeat:
                if self.lastSend.toordinal() + self.minWaitBetweenRepeat > datetime.now().toordinal():
                    repeat = self.repeat
            else:
                repeat = self.repeat

        # Call server plugin
        serverPlugin = ServerPlugin.Get(self.device.room.server)
        if serverPlugin:
            if serverPlugin.hasService('sendIRCommand'):
                aReturnCode = serverPlugin.sendIRCommand(self.protocol, self.hexCode, self.nbBits, repeat)

        # Update time stamp
        self.lastSend = timezone.now()
        self.save()
        return aReturnCode

class Config(models.Model):
    key = models.CharField(max_length=20, unique=True)
    value = models.CharField(max_length=200)

    @staticmethod
    def get(key):
        aConfigs = Config.objects.filter(key=key)
        if aConfigs:
                return aConfigs[0].value
        return None

    def __str__(self):
        return self.key

