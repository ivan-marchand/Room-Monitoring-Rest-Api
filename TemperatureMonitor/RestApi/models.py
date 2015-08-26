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
    yun_host = models.CharField(max_length=200,default=None,null=True,blank=True)
    yun_port = models.IntegerField(default=0,null=True,blank=True)
    spark_accessToken = models.CharField(max_length=100,default=None,null=True,blank=True)
    spark_deviceId = models.CharField(max_length=100,default=None,null=True,blank=True)

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
        # Arduino Yun
        if self.server.type == 'A':
            url = "http://%s:%s/arduino/getTemp/F" % (self.server.yun_host, self.server.yun_port)

            h = httplib2.Http(".cache")
            resp, content = h.request(url)

            return json.loads(content)
        # Spark Core
        elif self.server.type == 'S':
            url = "https://api.particle.io/v1/devices/%s/getTempF?access_token=%s" % (self.server.spark_deviceId, self.server.spark_accessToken)
            h = httplib2.Http(".cache")
            resp, content = h.request(url)

            # Decode Spark Reply
            print content
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
        if self.server:
            aResult = self.getTemperatureFromServer()
            if 'temperature' in aResult:
                aJsonDoc['temperature'] = float(aResult['temperature'])
            if 'humidity' in aResult:
                aJsonDoc['humidity'] = float(aResult['humidity'])
            if 'error' in aResult:
                aJsonDoc['error'] = aResult['error']
        elif self.temperature:
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
        # Arduino Yun
        if self.server.type == 'A':
            url = "http://%s:%s/arduino/sendIRCommand/%s/%s/%i" % (self.room.server.yun_host, self.room.server.yun_port, self.protocol, self.hexCode, self.nbBits)

            h = httplib2.Http(".cache")
            resp, content = h.request(url)
        
            result = json.loads(content)
            return 'error' not in result

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

    def __str__(self):              # __unicode__ on Python 2
        return self.key

