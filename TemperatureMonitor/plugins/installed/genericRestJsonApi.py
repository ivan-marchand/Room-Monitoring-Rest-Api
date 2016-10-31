import httplib2
import json
from TemperatureMonitor.plugins.loader import AbstractPlugin

# Generic REST JSON API
class GenericRestJsonApi(AbstractPlugin):

    def get(self, path):
        # Get base path
        basePath = self.config.getConfig('basePath')
        if not basePath:
            basePath = ""
        elif not path.endswith('/'):
            basePath += '/'
        url = "http://%s:%s/%s%s" % (self.config.getConfig('host'), self.config.getConfig('port'), basePath, path)

        # Add user/password
        if self.config.getConfig('username') and self.config.getConfig('password'):
            url += "?username=%s&password=%s" % (self.config.getConfig('username'), self.config.getConfig('password'))

        print url
        h = httplib2.Http(".cache")
        resp, content = h.request(url)

        return json.loads(content)
    
    def getTemperature(self):
        return get("getTemperature/F")

    def getThermostat(self):
        return get("getThermostat")

    def setThermostat(self, mode, temperature=None):
        if mode.upper() == "OFF":
            return get("setThermostat/OFF")
        elif mode.upper() == "HEAT" or mode.upper() == "COOL":
            return get("setThermostat/%s/%i" % (mode.upper(), temperature))
        else:
            return {"error": "Unknown mode %s" % mode}
            

AbstractPlugin.Register('G', 'Generic REST Json API', GenericRestJsonApi, {
    'host' : ("Host", "String", True),
    'port' : ("Port", "Integer", True),
    })
