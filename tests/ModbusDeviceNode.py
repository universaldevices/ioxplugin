import udi_interface, os, sys, json, time
LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom
class ModbusDeviceNode(udi_interface.Node):
    id = 'modbus'
    """This is a list of properties that were defined in the nodedef"""
    drivers = [{'driver': 'GV0', 'value': 0, 'uom': 25, 'name':
        'Load Shave'}, {'driver': 'GV1', 'value': 0, 'uom': 72, 'name':
        'Grid Support Voltage'}, {'driver': 'GV2', 'value': 0, 'uom': 1,
        'name': 'Maximum Sell Amps'}, {'driver': 'GV3', 'value': 0, 'uom': 
        1, 'name': 'Load Shave Amps'}, {'driver': 'GV4', 'value': 0, 'uom':
        72, 'name': 'DC Voltage '}]

    def __init__(self, polyglot, protocolHandler, controller=
        'modbuscontroll', address='modbus', name='ModbusDevice'):
        super().__init__(polyglot, controller, address, name)
        self.protocolHandler = protocolHandler

    def setProtocolHandler(self, protocolHandler):
        self.protocolHandler = protocolHandler
    """Use this method to update LoadShave in IoX"""

    def updateLoadShave(self, value, force: bool):
        return self.setDriver("GV0", value, 25, force)

    def getLoadShave(self):
        return self.getDriver("GV0")

    def queryLoadShave(self):
        if self.protocolHandler:
            val = self.protocolHandler.queryProperty(self, 'GV0')
            if val:
                self.updateLoadShave(val, True)
                return True
        return False
    """Use this method to update GridSupportVoltage in IoX"""

    def updateGridSupportVoltage(self, value, force: bool):
        return self.setDriver("GV1", value, 72, force)

    def getGridSupportVoltage(self):
        return self.getDriver("GV1")

    def queryGridSupportVoltage(self):
        if self.protocolHandler:
            val = self.protocolHandler.queryProperty(self, 'GV1')
            if val:
                self.updateGridSupportVoltage(val, True)
                return True
        return False
    """Use this method to update MaximumSellAmps in IoX"""

    def updateMaximumSellAmps(self, value, force: bool):
        return self.setDriver("GV2", value, 1, force)

    def getMaximumSellAmps(self):
        return self.getDriver("GV2")

    def queryMaximumSellAmps(self):
        if self.protocolHandler:
            val = self.protocolHandler.queryProperty(self, 'GV2')
            if val:
                self.updateMaximumSellAmps(val, True)
                return True
        return False
    """Use this method to update LoadShaveAmps in IoX"""

    def updateLoadShaveAmps(self, value, force: bool):
        return self.setDriver("GV3", value, 1, force)

    def getLoadShaveAmps(self):
        return self.getDriver("GV3")

    def queryLoadShaveAmps(self):
        if self.protocolHandler:
            val = self.protocolHandler.queryProperty(self, 'GV3')
            if val:
                self.updateLoadShaveAmps(val, True)
                return True
        return False
    """Use this method to update DCVoltage in IoX"""

    def updateDCVoltage(self, value, force: bool):
        return self.setDriver("GV4", value, 72, force)

    def getDCVoltage(self):
        return self.getDriver("GV4")

    def queryDCVoltage(self):
        if self.protocolHandler:
            val = self.protocolHandler.queryProperty(self, 'GV4')
            if val:
                self.updateDCVoltage(val, True)
                return True
        return False

    def queryAll():
        self.queryLoadShave()
        self.queryGridSupportVoltage()
        self.queryMaximumSellAmps()
        self.queryLoadShaveAmps()
        self.queryDCVoltage()

    def ResetController(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            p1 = int(jparam['p1.uom1'])
            p2 = int(jparam['p2.uom25'])
            p3 = int(jparam['p3.uom1'])
            if self.protocolHandler:
                return self.protocolHandler.processCommand('ResetController',
                    p1n=p1, p2n=p2, p3n=p3)
            return False
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def setLoadShave(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            GV0 = int(jparam['GV0.uom25'])
            if self.protocolHandler:
                if self.protocolHandler.setProperty(self, 'GV0', GV0):
                    self.updateLoadShave(GV0, True)
                    return True
            return False
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def setGridSupportVoltage(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            GV1 = int(jparam['GV1.uom72'])
            if self.protocolHandler:
                if self.protocolHandler.setProperty(self, 'GV1', GV1):
                    self.updateGridSupportVoltage(GV1, True)
                    return True
            return False
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def setMaximumSellAmps(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            GV2 = int(jparam['GV2.uom1'])
            if self.protocolHandler:
                if self.protocolHandler.setProperty(self, 'GV2', GV2):
                    self.updateMaximumSellAmps(GV2, True)
                    return True
            return False
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def setLoadShaveAmps(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            GV3 = int(jparam['GV3.uom1'])
            if self.protocolHandler:
                if self.protocolHandler.setProperty(self, 'GV3', GV3):
                    self.updateLoadShaveAmps(GV3, True)
                    return True
            return False
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False
    """This is a list of commands that were defined in the nodedef"""
    commands = {'reset': ResetController, 'GV0': setLoadShave, 'GV1':
        setGridSupportVoltage, 'GV2': setMaximumSellAmps, 'GV3':
        setLoadShaveAmps}
