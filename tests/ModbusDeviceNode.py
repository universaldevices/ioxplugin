import udi_interface, os, sys, json, time
LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom
class ModbusDeviceNode(udi_interface.Node):
    id = 'modbus'
    """This is a list of properties that were defined in the nodedef"""
    drivers = [{'driver': 'LOAD_SHAVE', 'value': 0, 'uom': 25, 'name':
        'Load Shave'}, {'driver': 'GS_VOLTAGE', 'value': 0, 'uom': 72,
        'name': 'Grid Support Voltage'}, {'driver': 'SELL_AMPS', 'value': 0,
        'uom': 1, 'name': 'Maximum Sell Amps'}, {'driver':
        'LOAD_SHAVE_AMPS', 'value': 0, 'uom': 1, 'name': 'Load Shave Amps'},
        {'driver': 'DC_VOLTAGE', 'value': 0, 'uom': 72, 'name': 'DC Voltage '}]

    def __init__(self, polyglot, protocolHandler, controller=
        'modbuscontroll', address='modbus', name='ModbusDevice'):
        super().__init__(polyglot, controller, address, name)
        self.protocolHandler = protocolHandler

    def setProtocolHandler(self, protocolHandler):
        self.protocolHandler = protocolHandler
    """Use this method to update LoadShave in IoX"""

    def updateLoadShave(self, value, force: bool):
        return self.setDriver("LOAD_SHAVE", value, 25, force)

    def getLoadShave(self):
        return self.getDriver("LOAD_SHAVE")

    def queryLoadShave(self):
        if self.protocolHandler:
            val = self.protocolHandler.queryProperty(self, 'LOAD_SHAVE')
            if val != None:
                self.updateLoadShave(val, True)
                return True
        return False
    """Use this method to update GridSupportVoltage in IoX"""

    def updateGridSupportVoltage(self, value, force: bool):
        return self.setDriver("GS_VOLTAGE", value, 72, force)

    def getGridSupportVoltage(self):
        return self.getDriver("GS_VOLTAGE")

    def queryGridSupportVoltage(self):
        if self.protocolHandler:
            val = self.protocolHandler.queryProperty(self, 'GS_VOLTAGE')
            if val != None:
                self.updateGridSupportVoltage(val, True)
                return True
        return False
    """Use this method to update MaximumSellAmps in IoX"""

    def updateMaximumSellAmps(self, value, force: bool):
        return self.setDriver("SELL_AMPS", value, 1, force)

    def getMaximumSellAmps(self):
        return self.getDriver("SELL_AMPS")

    def queryMaximumSellAmps(self):
        if self.protocolHandler:
            val = self.protocolHandler.queryProperty(self, 'SELL_AMPS')
            if val != None:
                self.updateMaximumSellAmps(val, True)
                return True
        return False
    """Use this method to update LoadShaveAmps in IoX"""

    def updateLoadShaveAmps(self, value, force: bool):
        return self.setDriver("LOAD_SHAVE_AMPS", value, 1, force)

    def getLoadShaveAmps(self):
        return self.getDriver("LOAD_SHAVE_AMPS")

    def queryLoadShaveAmps(self):
        if self.protocolHandler:
            val = self.protocolHandler.queryProperty(self, 'LOAD_SHAVE_AMPS')
            if val != None:
                self.updateLoadShaveAmps(val, True)
                return True
        return False
    """Use this method to update DCVoltage in IoX"""

    def updateDCVoltage(self, value, force: bool):
        return self.setDriver("DC_VOLTAGE", value, 72, force)

    def getDCVoltage(self):
        return self.getDriver("DC_VOLTAGE")

    def queryDCVoltage(self):
        if self.protocolHandler:
            val = self.protocolHandler.queryProperty(self, 'DC_VOLTAGE')
            if val != None:
                self.updateDCVoltage(val, True)
                return True
        return False

    def queryAll(self):
        self.queryLoadShave()
        self.queryGridSupportVoltage()
        self.queryMaximumSellAmps()
        self.queryLoadShaveAmps()
        self.queryDCVoltage()

    def setLoadShave(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            LOAD_SHAVE = int(jparam['LOAD_SHAVE.uom25'])
            if self.protocolHandler:
                if self.protocolHandler.setProperty(self, 'LOAD_SHAVE',
                    LOAD_SHAVE):
                    self.updateLoadShave(LOAD_SHAVE, True)
                    return True
            return False
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def setGridSupportVoltage(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            GS_VOLTAGE = int(jparam['GS_VOLTAGE.uom72'])
            if self.protocolHandler:
                if self.protocolHandler.setProperty(self, 'GS_VOLTAGE',
                    GS_VOLTAGE):
                    self.updateGridSupportVoltage(GS_VOLTAGE, True)
                    return True
            return False
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def setMaximumSellAmps(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            SELL_AMPS = int(jparam['SELL_AMPS.uom1'])
            if self.protocolHandler:
                if self.protocolHandler.setProperty(self, 'SELL_AMPS',
                    SELL_AMPS):
                    self.updateMaximumSellAmps(SELL_AMPS, True)
                    return True
            return False
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False

    def setLoadShaveAmps(self, command):
        try:
            query = str(command['query']).replace("'", '"')
            jparam = json.loads(query)
            LOAD_SHAVE_AMPS = int(jparam['LOAD_SHAVE_AMPS.uom1'])
            if self.protocolHandler:
                if self.protocolHandler.setProperty(self, 'LOAD_SHAVE_AMPS',
                    LOAD_SHAVE_AMPS):
                    self.updateLoadShaveAmps(LOAD_SHAVE_AMPS, True)
                    return True
            return False
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False
    """This is a list of commands that were defined in the nodedef"""
    commands = {'LOAD_SHAVE': setLoadShave, 'GS_VOLTAGE':
        setGridSupportVoltage, 'SELL_AMPS': setMaximumSellAmps,
        'LOAD_SHAVE_AMPS': setLoadShaveAmps}
