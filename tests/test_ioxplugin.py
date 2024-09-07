#test ioxplugin

#from ioxplugin import Plugin, ModbusIoX
import os
from ioxplugin import Plugin
from ioxplugin import PluginStoreOps
#from ioxplugin import PG3WebsocketConnection
from ioxplugin import PLUGIN_LOGGER
import time


curdir = os.curdir

plugin_path=(f"{curdir}/tests/dimmer.iox_plugin.json")
#storeOps=PluginStoreOps('Local')
#storeOps.addToStore(plugin_path, "tech@universal-devices.com", "admin", "/usr/home/admin/workspace/ioxplugin/tests")

plugin=Plugin(plugin_path)
s = plugin.areNodesStatic()
plugin.toIoX()
plugin.generateCode(path="/usr/home/admin/workspace/ioxplugin/tests")
#ModbusIoX = ModbusIoX(plugin)
#plugin.generateCode(".")

