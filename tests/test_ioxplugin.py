#test ioxplugin

#from ioxplugin import Plugin, ModbusIoX
import os
from ioxplugin import Plugin
from ioxplugin import PluginStoreOps
#from ioxplugin import PG3WebsocketConnection
from ioxplugin import PLUGIN_LOGGER
import time


curdir = os.curdir
pg3wss= PG3WebsocketConnection()
if not pg3wss.connect('admin','admin'):
    PLUGIN_LOGGER.error('login failed')
    exit(1)
PLUGIN_LOGGER.debug('connected ..')
#pg3wss.await_completion()
time.sleep(20000)

plugin_path=(f"{curdir}/tests/dimmer.iox_plugin.json")
storeOps=PluginStoreOps('Local')
storeOps.addToStore(plugin_path, "tech@universal-devices.com", "admin", "/usr/home/admin/workspace/ioxplugin/tests")

plugin=Plugin(plugin_path)
s = plugin.areNodesStatic()
plugin.toIoX()
plugin.generateCode(path="/usr/home/admin/workspace/ioxplugin/tests")
#ModbusIoX = ModbusIoX(plugin)
#plugin.generateCode(".")
