import httplib2
import json
from TemperatureMonitor.plugins.loader import AbstractPlugin

# Arduino Yun
class Yun(AbstractPlugin):
    
    def getTemperature(self):
        url = "http://%s:%s/arduino/getTemp/F" % (self.config.getConfig('host'), self.config.getConfig('port'))
        # Add user/password
        if self.config.getConfig('username') and self.config.getConfig('password'):
            url += "?username=%s&password=%s" % (self.config.getConfig('username'), self.config.getConfig('password'))

        print url
        h = httplib2.Http(".cache")
        resp, content = h.request(url)

        return json.loads(content)

    def sendIRCommand(protocol, hexCode, nbBits, repeat):
        url = "http://%s:%s/arduino/sendIRCommand/%s/%s/%i/%i" % (self.config.getConfig('host'), self.config.getConfig('port'), protocol, hexCode, nbBits, repeat)

        h = httplib2.Http(".cache")
        resp, content = h.request(url)
        
        result = json.loads(content)
        return result and 'error' not in result

AbstractPlugin.Register('A', 'Arduino Yun', Yun, {
    'host' : ("Host", "String", True),
    'port' : ("Port", "Integer", True),
    })