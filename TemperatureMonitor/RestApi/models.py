from django.db import models
from datetime import datetime
from django.utils import timezone
from itertools import repeat
from enum import Enum
from django.db.models.fields import BooleanField
from django.template.defaultfilters import default
from TemperatureMonitor.plugins.loader import AbstractPlugin

class Plugin(models.Model):
    name = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=1, choices=AbstractPlugin.GetTypes())

    @staticmethod
    def Get(name, type):
        aPlugins = Plugin.objects.filter(name=name, type=type)
        if len(aPlugins) > 0:
            return aPlugins[0]
        return None
    
    @staticmethod
    def GetById(id):
        aPlugins = Plugin.objects.filter(id=id)
        if len(aPlugins) > 0:
            return aPlugins[0]
        return None

    def getConfig(self, key):
        aConfigs = PluginConfig.objects.filter(plugin = self, key = key)
        if len(aConfigs):
            return aConfigs[0].value
        return None

    def addConfig(self, key, value):
        aConfig = PluginConfig(plugin = self, key = key, value=value)
        aConfig.save()

    def cleanConfig(self):
        for aConfig in PluginConfig.objects.filter(plugin=self):
            aConfig.delete()

    def getAsJson(self, getConfig):
        aJson = dict()
        aJson['name'] = self.name
        aJson['type'] = self.type
        aJson['id'] = self.id
        
        if getConfig:
            aJson['config'] = dict()
            for aConfig in PluginConfig.objects.filter(plugin=self):
                aJson['config'][aConfig.key] = aConfig.value
        return aJson

    def __str__(self):
        return "%s (%s)" % (self.name, self.get_type_display())

class PluginConfig(models.Model):
    plugin = models.ForeignKey('Plugin')
    key = models.CharField(max_length=20)
    value = models.CharField(max_length=200)

    def __str__(self):
        return "%s - %s" % (self.plugin, self.key)

class Room(models.Model):
    name = models.CharField(max_length=20, unique=True)
    plugin = models.ForeignKey('Plugin')

    def __str__(self):
        return self.name

    def getTemperatureFromPlugin(self):
        aResult = dict()
        aPlugin = AbstractPlugin.Get(self.plugin)
        if aPlugin:
            if aPlugin.hasService('getTemperature'):
                aResult = aPlugin.getTemperature()
        else:
            aResult['error'] = "Unknown plugin type %s" % self.plugin.type
        
        return aResult

    def setThermostat(self, mode, temperature=None):
        aResult = dict()
        aPlugin = AbstractPlugin.Get(self.plugin)
        if aPlugin:
            if aPlugin.hasService('setThermostat'):
                aResult = aPlugin.setThermostat(mode, temperature)
        else:
            aResult['error'] = "setThermostat not implemented for plugin type %s" % self.plugin.type
        
        return aResult

    def getThermostat(self):
        aResult = dict()
        aPlugin = AbstractPlugin.Get(self.plugin)
        if aPlugin:
            if aPlugin.hasService('getThermostat'):
                aResult = aPlugin.getThermostat()
        else:
            aResult['error'] = "getThermostat not implemented for plugin type %s" % self.plugin.type
        
        return aResult

    def getTemperature(self, simulateRoom=False):
        aJsonDoc = dict()
        # Timestamp (on plugin time zone)
        now = datetime.now().replace(microsecond=0)
        aJsonDoc['timestamp'] = now.isoformat() 
        # Check if plugin is defined
        aResult = self.getTemperatureFromPlugin()
        if 'temperature' in aResult:
            aJsonDoc['temperature'] = float(aResult['temperature'])
        if 'humidity' in aResult:
            aJsonDoc['humidity'] = float(aResult['humidity'])
        if 'error' in aResult:
            aJsonDoc['error'] = aResult['error']
        if 'unit' in aResult:
            aJsonDoc['unit'] = aResult['unit']

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

        # Call plugin
        aPlugin = AbstractPlugin.Get(self.device.room.plugin)
        if aPlugin:
            if aPlugin.hasService('sendIRCommand'):
                aReturnCode = aPlugin.sendIRCommand(self.protocol, self.hexCode, self.nbBits, repeat)

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

