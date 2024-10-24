#test ioxplugin

#from ioxplugin import Plugin, ModbusIoX
import os
from ioxplugin import Plugin
from ioxplugin import PluginStoreOps
#from ioxplugin import PG3WebsocketConnection
from ioxplugin import PLUGIN_LOGGER
import time


curdir = os.curdir

#plugin_path=(f"{curdir}/tests/dimmer.iox_plugin.json")
plugin_path=(f"/home/admin/workspace/plugin-dev/shelly")
#storeOps=PluginStoreOps('Local')
#storeOps.addToStore(plugin_path, "tech@universal-devices.com", "admin", "/usr/home/admin/workspace/ioxplugin/tests")

plugin=Plugin(f"{plugin_path}/shelly.iox_plugin.json")
s = plugin.areNodesStatic()
s = plugin.getEnableDiscovery()
plugin.toIoX()
#plugin.generateCode(path="/usr/home/admin/workspace/ioxplugin/tests")
plugin.generateCode(plugin_path)
#ModbusIoX = ModbusIoX(plugin)
#plugin.generateCode(".")

