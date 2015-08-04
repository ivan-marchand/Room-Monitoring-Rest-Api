from django.contrib import admin
from models import Room,Server,Config,IRCommand

admin.site.register(Server)
admin.site.register(Room)
admin.site.register(IRCommand)
admin.site.register(Config)

