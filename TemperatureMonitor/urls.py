from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    #url(r'^$', 'TemperatureMonitor.views.home', name='home'),
    url(r'^api/v1/get/temperature/(?P<room>\w+)', 'TemperatureMonitor.RestApi.views.getTemperature', name='getTemperature'),
    url(r'^api/v1/set/tempthreshold/(?P<room>\w+)/(?P<type>\w+)/(?P<temperature>\d+)', 'TemperatureMonitor.RestApi.views.setTempThreshold', name='setTempThreshold'),

    url(r'^admin/', include(admin.site.urls)),
)
