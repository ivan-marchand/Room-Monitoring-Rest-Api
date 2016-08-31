from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Rest API
    url(r'^api/v1/login', 'TemperatureMonitor.RestApi.views.login', name='login'),
    url(r'^api/v1/get/rooms', 'TemperatureMonitor.RestApi.views.getRooms', name='getRooms'),
    url(r'^api/v1/get/temperature/(?P<room>\w+)', 'TemperatureMonitor.RestApi.views.getTemperature', name='getTemperature'),
    url(r'^api/v1/sendIRCommand/(?P<device>\w+)/(?P<command>\w+)', 'TemperatureMonitor.RestApi.views.sendIRCommand', name='sendIRCommand'),
    
    # Server
    url(r'^api/v1/get/serverTypes', 'TemperatureMonitor.RestApi.views.getServerTypes', name='getServerTypes'),
    url(r'^api/v1/get/servers', 'TemperatureMonitor.RestApi.views.getServers', name='getServers'),
    url(r'^api/v1/get/server/(?P<id>\d+)', 'TemperatureMonitor.RestApi.views.getServer', name='getServer'),
    url(r'^api/v1/add/server/(?P<name>\w+)/(?P<type>\w)', 'TemperatureMonitor.RestApi.views.addServer', name='addServer'),
    url(r'^api/v1/update/server/(?P<id>\w+)/(?P<name>\w+)/(?P<type>\w)', 'TemperatureMonitor.RestApi.views.updateServer', name='updateServer'),
    url(r'^api/v1/del/server/(?P<id>\d+)', 'TemperatureMonitor.RestApi.views.delServer', name='delServer'),

    url(r'^admin/', include(admin.site.urls)),
)
