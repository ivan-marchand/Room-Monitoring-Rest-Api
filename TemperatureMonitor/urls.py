from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Rest API
    url(r'^api/v1/login', 'TemperatureMonitor.RestApi.views.testCredential', name='testCredential'),
    url(r'^api/v1/get/rooms', 'TemperatureMonitor.RestApi.views.getRooms', name='getRooms'),
    url(r'^api/v1/get/roomList', 'TemperatureMonitor.RestApi.views.getRoomList', name='getRoomList'),
    url(r'^api/v1/get/temperature/(?P<room>\w+)', 'TemperatureMonitor.RestApi.views.getTemperature', name='getTemperature'),
    url(r'^api/v1/sendIRCommand/(?P<device>\w+)/(?P<command>\w+)', 'TemperatureMonitor.RestApi.views.sendIRCommand', name='sendIRCommand'),
    
    # Plugin
    url(r'^api/v1/get/availablePlugins', 'TemperatureMonitor.RestApi.views.getAvailablePlugins', name='getAvailablePlugins'),
    url(r'^api/v1/get/plugins', 'TemperatureMonitor.RestApi.views.getPlugins', name='getPlugins'),
    url(r'^api/v1/get/plugin/(?P<id>\d+)', 'TemperatureMonitor.RestApi.views.getPlugin', name='getPlugin'),
    url(r'^api/v1/add/plugin/(?P<name>\w+)/(?P<type>\w)', 'TemperatureMonitor.RestApi.views.addPlugin', name='addPlugin'),
    url(r'^api/v1/update/plugin/(?P<id>\w+)/(?P<name>\w+)/(?P<type>\w)', 'TemperatureMonitor.RestApi.views.updatePlugin', name='updatePlugin'),
    url(r'^api/v1/del/plugin/(?P<id>\d+)', 'TemperatureMonitor.RestApi.views.delPlugin', name='delPlugin'),

    url(r'^admin/', include(admin.site.urls)),
)
