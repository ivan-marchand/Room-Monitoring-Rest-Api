from django.contrib import admin
from models import Room,Server,ServerConfig,Config,IRCommand,Device

admin.site.register(Server)
admin.site.register(ServerConfig)
admin.site.register(Room)
admin.site.register(Device)
admin.site.register(IRCommand)
admin.site.register(Config)

