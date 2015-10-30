from django.db import models
import urllib, httplib2
import json
from datetime import datetime


class Server(models.Model):
    TYPES = (
        ('A', 'Arduino Yun'),
        ('S', 'Spark Core'),
    )
    name = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=1, choices=TYPES)

    def getConfig(self, key):
        aConfigs = ServerConfig.objects.filter(server = self, key = key)
        if len(aConfigs):
            return aConfigs[0].value
        return None

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
        # Arduino Yun
        if self.server.type == 'A':
            url = "http://%s:%s/arduino/getTemp/F" % (self.server.getConfig('host'), self.server.getConfig('port'))

            h = httplib2.Http(".cache")
            resp, content = h.request(url)

            return json.loads(content)
        # Spark Core
        elif self.server.type == 'S':
            url = "https://api.particle.io/v1/devices/%s/getTempF?access_token=%s" % (self.server.getConfig('deviceId'), self.server.getConfig('accessToken'))
            h = httplib2.Http(".cache")
            resp, content = h.request(url)

            # Decode Spark Reply
            aContentJson = json.loads(content)
            aResult = dict()
            aResult['temperature'], aResult['humidity'] = aContentJson['result'].split(':')
            return aResult
        return {'error' : "Unknown server"}

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
    actif = models.BooleanField()

    def __str__(self):
        return "%s (%s)" % (self.name, self.get_type_display())

class IRCommand(models.Model):
    device = models.ForeignKey('Device')
    name = models.CharField(max_length=20)
    text = models.CharField(max_length=20)
    protocol = models.CharField(max_length=20)
    hexCode = models.CharField(max_length=16)
    nbBits = models.IntegerField()

    def __str__(self):
        return "%s-%s" % (self.device.name, self.name)

    def send(self):
        # Arduino Yun
        if self.device.room.server.type == 'A':
            url = "http://%s:%s/arduino/sendIRCommand/%s/%s/%i" % (self.device.room.server.getConfig('host'), self.device.room.server.getConfig('port'), self.protocol, self.hexCode, self.nbBits)

            h = httplib2.Http(".cache")
            resp, content = h.request(url)
        
            result = json.loads(content)
            return 'error' not in result
        # Spark Core
        elif self.device.room.server.type == 'S':
            url = "https://api.particle.io/v1/devices/%s/sendIR" % (self.device.room.server.getConfig('deviceId'))
            h = httplib2.Http(".cache")
            headers = {'Content-type': 'application/x-www-form-urlencoded'}
            data = dict(access_token=self.device.room.server.getConfig('accessToken'), args=self.hexCode)
            resp, content = h.request(url, "POST", headers=headers, body=urllib.urlencode(data))

            # Decode Spark Reply
            result = json.loads(content)
            return 'return_value' in result and result['return_value'] != -1

        return False

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

