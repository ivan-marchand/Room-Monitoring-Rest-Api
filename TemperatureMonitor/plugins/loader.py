import inspect
import importlib
import os
from dircache import listdir

kInstalledPlugins = dict()

def ImportPlugins():
    pluginPath = os.path.join(os.path.dirname(__file__), "installed")
    for item in listdir(pluginPath):
        if item != "__init__.py" and os.path.isfile(os.path.join(pluginPath,item)):
            name, ext = os.path.splitext(item)
            if ext == ".py":
                importlib.import_module("TemperatureMonitor.plugins.installed.%s" % name)

class AbstractPlugin:
    config = None
    
    @staticmethod
    def Register(pluginType, pluginName, plugin, parameters=None):
        kInstalledPlugins[pluginType] = (pluginName, plugin, parameters)

    @staticmethod
    def Get(plugin):
       if plugin.type in kInstalledPlugins:
           return kInstalledPlugins[plugin.type][1](plugin)
       return None

    @staticmethod
    def GetTypes():
        types = []
        for pluginType, item in kInstalledPlugins.items():
            types.append( (pluginType, item[0]) )
        return types

    @staticmethod
    def GetAvailablePlugin():
        plugins = []
        for pluginType, item in kInstalledPlugins.items():
            plugin = {"type": pluginType, "name": item[0]}
            if item[2]:
                plugin["parameters"] = item[2]
            plugins.append(plugin)
        return plugins

    def __init__(self, config):
        self.config = config

    def hasService(self, name):
        service = getattr(self, name, None)
        return service != None and inspect.ismethod(service)
    
# Implement plugins
ImportPlugins()

