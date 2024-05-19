#test ioxplugin

#from ioxplugin import Plugin, ModbusIoX
import os
from ioxplugin import Plugin

curdir = os.curdir


plugin = Plugin("/usr/home/admin/workspace/plugin-dev/modbus/modbus.iox_plugin.json")
plugin.toIoX()
plugin.generateCode(path="/usr/home/admin/workspace/ioxplugin/tests")
#ModbusIoX = ModbusIoX(plugin)
#plugin.generateCode(".")
