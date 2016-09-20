from django.contrib import admin
from models import Room,Plugin,PluginConfig,Config,IRCommand,Device

admin.site.register(Plugin)
admin.site.register(PluginConfig)
admin.site.register(Room)
admin.site.register(Device)
admin.site.register(IRCommand)
admin.site.register(Config)

