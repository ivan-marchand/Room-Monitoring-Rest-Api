import httplib2
import json
from TemperatureMonitor.plugins.loader import AbstractPlugin

# Generic REST JSON API
class GenericRestJsonApi(AbstractPlugin):
    
    def getTemperature(self):
        path = self.config.getConfig('basePath')
        if not path:
            path = ""
	elif not path.endswith('/'):
            path += '/'
        url = "http://%s:%s/%sgetTemperature/F" % (self.config.getConfig('host'), self.config.getConfig('port'), path)
        # Add user/password
        if self.config.getConfig('username') and self.config.getConfig('password'):
            url += "?username=%s&password=%s" % (self.config.getConfig('username'), self.config.getConfig('password'))

        print url
        h = httplib2.Http(".cache")
        resp, content = h.request(url)

        return json.loads(content)

AbstractPlugin.Register('G', 'Generic REST Json API', GenericRestJsonApi, {
    'host' : ("Host", "String", True),
    'port' : ("Port", "Integer", True),
    })
