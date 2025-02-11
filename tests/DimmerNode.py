import udi_interface, os, sys, json, time
LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom
class DimmerNode(udi_interface.Node):
    id = 'dimmer'
    """This is a list of properties that were defined in the nodedef"""
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 51, 'name': 'Status'}, {
        'driver': 'RAMP_RATE', 'value': 0, 'uom': 139, 'name': 'Ramp Rate'},
        {'driver': 'ON_LEVEL', 'value': 0, 'uom': 51, 'name': 'On Level'}]

    def __init__(self, polyglot, plugin, controller='dimmercontroll',
        address='dimmer', name='Dimmer'):
        super().__init__(polyglot, controller, address, name)
        self.plugin = plugin

    def getUOM(self, driver: str):
        try:
            for driver_def in self.drivers:
                if driver_def['driver'] == driver:
                    return driver_def['uom']
            return None
        except Exception as ex:
            return None

    def updateStatus(self, value, force: bool=None, text: str=None):
        return self.setDriver("ST", value, 51, force, text)

    def getStatus(self):
        return self.getDriver("ST")

    def updateRampRate(self, value, force: bool=None, text: str=None):
        return self.setDriver("RAMP_RATE", value, 139, force, text)

    def getRampRate(self):
        return self.getDriver("RAMP_RATE")

    def updateOnLevel(self, value, force: bool=None, text: str=None):
        return self.setDriver("ON_LEVEL", value, 51, force, text)

    def getOnLevel(self):
        return self.getDriver("ON_LEVEL")

    def __On(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            if 'onlevel.uom51' in jparam:
                onlevel = int(jparam['onlevel.uom51'])
            if 'ramprate.uom139' in jparam:
                ramprate = int(jparam['ramprate.uom139'])
            return self.On(onlevel, ramprate)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def __Off(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            if 'ramprate.uom139' in jparam:
                ramprate = int(jparam['ramprate.uom139'])
            return self.Off(ramprate)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def __FastOn(self, command):
        try:
            return self.FastOn()
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def __FastOff(self, command):
        try:
            return self.FastOff()
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def __setRampRate(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            if 'RAMP_RATE.uom139' in jparam:
                RAMP_RATE = int(jparam['RAMP_RATE.uom139'])
            return self.setRampRate(RAMP_RATE)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def __setOnLevel(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            if 'ON_LEVEL.uom51' in jparam:
                ON_LEVEL = int(jparam['ON_LEVEL.uom51'])
            return self.setOnLevel(ON_LEVEL)
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False
    """This is a list of commands that were defined in the nodedef"""
    commands = {'on': __On, 'off': __Off, 'faston': __FastOn, 'fastoff':
        __FastOff, 'RAMP_RATE': __setRampRate, 'ON_LEVEL': __setOnLevel}
    """    """

    def queryAll(self):
        self.queryStatus()
        self.queryRampRate()
        self.queryOnLevel()

    """########WARNING: DO NOT MODIFY THIS LINE!!! NOTHING BELOW IS REGENERATED!#########"""

    def queryStatus():
        try:
            return True
        except:
            return False

    def queryRampRate():
        try:
            return True
        except:
            return False

    def queryOnLevel():
        try:
            return True
        except:
            return False

    def On(onlevel, ramprate):
        try:
            return True
        except:
            return False

    def Off(ramprate):
        try:
            return True
        except:
            return False

    def FastOn():
        try:
            return True
        except:
            return False

    def FastOff():
        try:
            return True
        except:
            return False

    def setRampRate(ramprate):
        try:
            return True
        except:
            return False

    def setOnLevel(onlevel):
        try:
            return True
        except:
            return False