#test ioxplugin

from ioxplugin import Plugin, ModbusIoX
import os

curdir = os.curdir


plugin = Plugin("/usr/home/admin/workspace/ioxplugin/tests/modbus.iox_plugin.json")
plugin.toIoX()
plugin.generateCode(path="/usr/home/admin/workspace/ioxplugin/tests")
ModbusIoX = ModbusIoX(plugin)
#plugin.generateCode(".")
