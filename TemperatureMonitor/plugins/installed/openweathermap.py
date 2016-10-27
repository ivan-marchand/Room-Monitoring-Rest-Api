import json
import httplib2
import urllib
from TemperatureMonitor.plugins.loader import AbstractPlugin

# Open Weather Map
class OpenWeatherMap(AbstractPlugin):

    def getTemperature(self):
        aResult = dict()
        url = "http://api.openweathermap.org/data/2.5/weather"
        criteria = "?units=imperial"
        # City
        aCityName = self.config.getConfig('city')
        if aCityName:
            criteria += "&q=%s" % aCityName
        # Zip Code
        aZipCode = self.config.getConfig('zip')
        if aZipCode:
            criteria = "&zip=%s" % aZipCode
        aApiKey = self.config.getConfig('appid')
        if aApiKey:
            url += criteria + "&appid=%s" % aApiKey
            h = httplib2.Http(".cache")
            resp, content = h.request(url)

            # Decode Spark Reply
            aContentJson = json.loads(content)
            if 'cod' in aContentJson and aContentJson['cod'] == 200:
                if 'main' in aContentJson:
                    if 'temp' in aContentJson['main']:
                        aResult['temperature'] = aContentJson['main']['temp']
                    if 'humidity' in aContentJson['main']:
                        aResult['humidity'] = aContentJson['main']['humidity']
            elif 'message' in aContentJson:
                aResult['error'] = aContentJson['message']
            else:
                aResult['error'] = "Unable to Process"
        else:
            aResult['error'] = "API Key Missing"
        return aResult

AbstractPlugin.Register('O', 'Open Weather Map', OpenWeatherMap, {
    'City' : ("City", "String", True),
    'appid' : ("API Key", "String", True),
    })
