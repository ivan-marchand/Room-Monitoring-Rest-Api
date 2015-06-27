from django.contrib import admin
from django.db import models

class Room(models.Model):
    name = models.CharField(max_length=20, unique=True)
    temperature = models.IntegerField()

    def __str__(self):              # __unicode__ on Python 2
        return self.name
admin.site.register(Room)

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

admin.site.register(Config)
