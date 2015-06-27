from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    #url(r'^$', 'TemperatureMonitor.views.home', name='home'),
    url(r'^api/v1/get/temp/(?P<room>\w+)', 'TemperatureMonitor.RestApi.views.getTemperature', name='getTemperature'),

    url(r'^admin/', include(admin.site.urls)),
)
