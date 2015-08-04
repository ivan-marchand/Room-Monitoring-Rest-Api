from django.db import models
import urllib, httplib2
import json
from datetime import datetime

class Server(models.Model):
    name = models.CharField(max_length=20, unique=True)
    host = models.CharField(max_length=200)
    port = models.IntegerField()

    def __str__(self):              # __unicode__ on Python 2
        return self.name

class Room(models.Model):
    name = models.CharField(max_length=20, unique=True)
    temperature = models.IntegerField(default=None,null=True,blank=True)
    server = models.ForeignKey('Server',default=None,null=True,blank=True)
    high_threshold = models.IntegerField(default=None,null=True,blank=True)
    low_threshold = models.IntegerField(default=None,null=True,blank=True)

    def __str__(self):              # __unicode__ on Python 2
        return self.name

    def getTemperatureFromServer(self):
        url = "http://%s:%s/arduino/getTemp/F" % (self.server.host, self.server.port)

        h = httplib2.Http(".cache")
        resp, content = h.request(url)

        return json.loads(content)

    def getTemperature(self, simulateRoom=False):
        aJsonDoc = dict()
        # Timestamp (on server time zone)
        now = datetime.now().replace(microsecond=0)
        aJsonDoc['timestamp'] = now.isoformat() 
        # Check if server is defined
        if self.server:
            aResult = self.getTemperatureFromServer()
            if 'temperature' in aResult:
                aJsonDoc['temperature'] = float(aResult['temperature'])
            if 'humidity' in aResult:
                aJsonDoc['humidity'] = float(aResult['humidity'])
        elif simulateRoom and self.temperature:
            aJsonDoc['temperature'] = self.temperature

        return aJsonDoc

class IRCommand(models.Model):
    name = models.CharField(max_length=20)
    room = models.ForeignKey('Room')
    protocol = models.CharField(max_length=20)
    hexCode = models.CharField(max_length=16)
    nbBits = models.IntegerField()

    def __str__(self):
        return "%s-%s" % (self.room.name, self.name)

    def send(self):
        url = "http://%s:%s/arduino/sendIRCommand/%s/%s/%i" % (self.room.server.host, self.room.server.port, self.protocol, self.hexCode, self.nbBits)

        h = httplib2.Http(".cache")
        resp, content = h.request(url)
        
        result = json.loads(content)
        return 'error' not in result

class Config(models.Model):
    key = models.CharField(max_length=20, unique=True)
    value = models.CharField(max_length=200)

    @staticmethod
    def get(key):
        aConfigs = Config.objects.filter(key=key)
        if aConfigs:
                return aConfigs[0].value
        return None

    def __str__(self):              # __unicode__ on Python 2
        return self.key

