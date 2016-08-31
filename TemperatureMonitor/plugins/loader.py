import inspect
import importlib
import os
from dircache import listdir

kPluginCollection = dict()

def ImportPlugins(type):
    pluginPath = os.path.join(os.path.dirname(__file__), type)
    for item in listdir(pluginPath):
        if item != "__init__.py" and os.path.isfile(os.path.join(pluginPath,item)):
            name, ext = os.path.splitext(item)
            if ext == ".py":
                importlib.import_module("TemperatureMonitor.plugins.server.%s" % name)
                
class ServerPlugin:
    config = None
    
    @staticmethod
    def Register(serverType, serverName, plugin):
        kPluginCollection[serverType] = (serverName, plugin)

    @staticmethod
    def Get(server):
       if server.type in kPluginCollection:
           return kPluginCollection[server.type][1](server)
       return None

    @staticmethod
    def GetTypes():
        types = []
        for serverType, item in kPluginCollection.items():
            types.append( (serverType, item[0]) )
        return types

    def __init__(self, config):
        self.config = config

    def hasService(self, name):
        service = getattr(self, name, None)
        return service != None and inspect.ismethod(service)
    
# Implement plugins
ImportPlugins('server')

