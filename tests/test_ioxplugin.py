#test ioxplugin

#from ioxplugin import Plugin, ModbusIoX
import os
from ioxplugin import Plugin
from ioxplugin import StoreEntry 

curdir = os.curdir



#plugin = Plugin("/usr/home/admin/workspace/plugin-dev/modbus/reference/modbus.iox_plugin.json")
plugin = Plugin(f"{curdir}/tests/dimmer.iox_plugin.json")
store=StoreEntry(plugin)
store.addToStore("tech@universal-devices.com", "admin", "/usr/home/admin/workspace/ioxplugin/tests")

s = plugin.areNodesStatic()
plugin.toIoX()
plugin.generateCode(path="/usr/home/admin/workspace/ioxplugin/tests")
#ModbusIoX = ModbusIoX(plugin)
#plugin.generateCode(".")
