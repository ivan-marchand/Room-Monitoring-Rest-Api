import httplib2
import json
from TemperatureMonitor.plugins.loader import ServerPlugin

# Arduino Yun
class Yun(ServerPlugin):
    
    def getTemperature(self):
        url = "http://%s:%s/arduino/getTemp/F" % (self.config.getConfig('host'), self.config.getConfig('port'))

        h = httplib2.Http(".cache")
        resp, content = h.request(url)

        return json.loads(content)

    def sendIRCommand(protocol, hexCode, nbBits, repeat):
        url = "http://%s:%s/arduino/sendIRCommand/%s/%s/%i/%i" % (self.config.getConfig('host'), self.config.getConfig('port'), protocol, hexCode, nbBits, repeat)

        h = httplib2.Http(".cache")
        resp, content = h.request(url)
        
        result = json.loads(content)
        return result and 'error' not in result

ServerPlugin.Register('A', 'Arduino Yun', Yun)