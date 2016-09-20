import json
import httplib2
import urllib
from TemperatureMonitor.plugins.loader import AbstractPlugin

# Spark Core
class SparkCore(AbstractPlugin):

    def getTemperature(self):
        url = "https://api.particle.io/v1/devices/%s/getTempF?access_token=%s" % (self.config.getConfig('deviceId'), self.config.getConfig('accessToken'))
        h = httplib2.Http(".cache")
        resp, content = h.request(url)

        # Decode Spark Reply
        aContentJson = json.loads(content)
        aResult = dict()
        if 'result' in aContentJson:
            aResult['temperature'], aResult['humidity'] = aContentJson['result'].split(':')
        elif 'error' in aContentJson:
            aResult['error'] = aContentJson['error']
        else:
            aResult['error'] = "Unable to process"
        return aResult

    def sendIRCommand(protocol, hexCode, nbBits, repeat):
        url = "https://api.particle.io/v1/devices/%s/sendIR" % (self.config.getConfig('deviceId'))
        h = httplib2.Http(".cache")
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        data = dict(access_token=self.config.getConfig('accessToken'), args="%s,%s,%i,%i" % (protocol, hexCode, nbBits, repeat))
        resp, content = h.request(url, "POST", headers=headers, body=urllib.urlencode(data))

        # Decode Spark Reply
        result = json.loads(content)
        return 'return_value' in result and result['return_value'] != -1

AbstractPlugin.Register('S', 'Spark Core', SparkCore)