#test ioxplugin

from ioxplugin import Plugin, ModbusIoX
import os

curdir = os.curdir


plugin = Plugin("/usr/home/admin/workspace/ioxplugin/tests/modbus.iox_plugin.json", ".")
plugin.toIoX()
ModbusIoX = ModbusIoX(plugin)
#plugin.generateCode(".")
