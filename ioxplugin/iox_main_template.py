
IOX_MAIN_TEMPLATE='''
#!/usr/bin/env python3
# Main routine for IoX Plugin. 
# Do NOT Modify 

import udi_interface, os, sys, json, time
import version
from ioxplugin import Plugin
from __PROTOCOL_HANDLER_FILE__ import __PROTOCOL_HANDLER_CLASS__

PLUGIN_FILE_NAME = '__PLUGIN_FILE_NAME__'
LOGGER = udi_interface.LOGGER
if __name__ == '__main__':
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start(version.ud_plugin_version)
        plugin = None
        if not os.path.exists(PLUGIN_FILE_NAME):
            polyglot.Notices['config']=f"{PLUGIN_FILE_NAME} does not exist. Uplaod it using file upload ..."
        else:
            plugin = Plugin(PLUGIN_FILE_NAME)
            plugin.toIoX()
            plugin.generateCode(path='./')
        
        from __CONTROLLER_NODE_FILE__ import __CONTROLLER_NODE_CLASS__
        protocolHandler = __PROTOCOL_HANDLER_CLASS__(plugin)
        controller = __CONTROLLER_NODE_CLASS__(polyglot, protocolHandler)
        protocolHandler.setController(controller)
        controller.start()
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        LOGGER.info('exiting ...')
        sys(0)
'''


