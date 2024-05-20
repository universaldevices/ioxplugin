import udi_interface, os, sys, json, time
LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom
class ModbusDeviceNode(udi_interface.Node):
    id = 'modbus'
    """This is a list of properties that were defined in the nodedef"""
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 25, 'name': 'Status'}, {
        'driver': 'GV0', 'value': 0, 'uom': 25, 'name': 'Running'}, {
        'driver': 'GV1', 'value': 0, 'uom': 25, 'name': 'Zero Speed'}, {
        'driver': 'GV2', 'value': 0, 'uom': 25, 'name': 'Alarm'}, {'driver':
        'GV3', 'value': 0, 'uom': 25, 'name': 'Fault'}, {'driver': 'GV4',
        'value': 0, 'uom': 90, 'name': 'Frequency Ref'}, {'driver': 'GV5',
        'value': 0, 'uom': 90, 'name': 'Frequency Out'}, {'driver': 'GV6',
        'value': 0, 'uom': 1, 'name': 'Current'}, {'driver': 'GV7', 'value':
        0, 'uom': 138, 'name': 'Pressure'}, {'driver': 'GV8', 'value': 0,
        'uom': 72, 'name': 'Voltage'}]

    def __init__(self, polyglot, protocolHandler, controller=
        'modbuscontroll', address='modbus', name='ModbusDevice'):
        super().__init__(polyglot, controller, address, name)
        self.protocolHandler = protocolHandler

    def setProtocolHandler(self, protocolHandler):
        self.protocolHandler = protocolHandler
    """Use this method to update Status in IoX"""

    def updateStatus(self, value, force: bool):
        return self.setDriver("ST", value, 25, force)

    def getStatus(self):
        return self.getDriver("ST")

    def queryStatus(self):
        if self.protocolHandler:
            precision = 1
            if self.protocolHandler:
                val = self.protocolHandler.queryProperty(self, 'ST')
                if val != None:
                    if isinstance(val, int):
                        if precision > 1:
                            div = pow(10, precision)
                            fval = round(float(fval / div), precision)
                            self.updateStatus(fval, True)
                            return True
                    self.updateStatus(val, True)
                    return True
        return False
    """Use this method to update Running in IoX"""

    def updateRunning(self, value, force: bool):
        return self.setDriver("GV0", value, 25, force)

    def getRunning(self):
        return self.getDriver("GV0")

    def queryRunning(self):
        if self.protocolHandler:
            precision = 1
            if self.protocolHandler:
                val = self.protocolHandler.queryProperty(self, 'GV0')
                if val != None:
                    if isinstance(val, int):
                        if precision > 1:
                            div = pow(10, precision)
                            fval = round(float(fval / div), precision)
                            self.updateRunning(fval, True)
                            return True
                    self.updateRunning(val, True)
                    return True
        return False
    """Use this method to update ZeroSpeed in IoX"""

    def updateZeroSpeed(self, value, force: bool):
        return self.setDriver("GV1", value, 25, force)

    def getZeroSpeed(self):
        return self.getDriver("GV1")

    def queryZeroSpeed(self):
        if self.protocolHandler:
            precision = 1
            if self.protocolHandler:
                val = self.protocolHandler.queryProperty(self, 'GV1')
                if val != None:
                    if isinstance(val, int):
                        if precision > 1:
                            div = pow(10, precision)
                            fval = round(float(fval / div), precision)
                            self.updateZeroSpeed(fval, True)
                            return True
                    self.updateZeroSpeed(val, True)
                    return True
        return False
    """Use this method to update Alarm in IoX"""

    def updateAlarm(self, value, force: bool):
        return self.setDriver("GV2", value, 25, force)

    def getAlarm(self):
        return self.getDriver("GV2")

    def queryAlarm(self):
        if self.protocolHandler:
            precision = 1
            if self.protocolHandler:
                val = self.protocolHandler.queryProperty(self, 'GV2')
                if val != None:
                    if isinstance(val, int):
                        if precision > 1:
                            div = pow(10, precision)
                            fval = round(float(fval / div), precision)
                            self.updateAlarm(fval, True)
                            return True
                    self.updateAlarm(val, True)
                    return True
        return False
    """Use this method to update Fault in IoX"""

    def updateFault(self, value, force: bool):
        return self.setDriver("GV3", value, 25, force)

    def getFault(self):
        return self.getDriver("GV3")

    def queryFault(self):
        if self.protocolHandler:
            precision = 1
            if self.protocolHandler:
                val = self.protocolHandler.queryProperty(self, 'GV3')
                if val != None:
                    if isinstance(val, int):
                        if precision > 1:
                            div = pow(10, precision)
                            fval = round(float(fval / div), precision)
                            self.updateFault(fval, True)
                            return True
                    self.updateFault(val, True)
                    return True
        return False
    """Use this method to update FrequencyRef in IoX"""

    def updateFrequencyRef(self, value, force: bool):
        return self.setDriver("GV4", value, 90, force)

    def getFrequencyRef(self):
        return self.getDriver("GV4")

    def queryFrequencyRef(self):
        if self.protocolHandler:
            precision = 2
            if self.protocolHandler:
                val = self.protocolHandler.queryProperty(self, 'GV4')
                if val != None:
                    if isinstance(val, int):
                        if precision > 1:
                            div = pow(10, precision)
                            fval = round(float(fval / div), precision)
                            self.updateFrequencyRef(fval, True)
                            return True
                    self.updateFrequencyRef(val, True)
                    return True
        return False
    """Use this method to update FrequencyOut in IoX"""

    def updateFrequencyOut(self, value, force: bool):
        return self.setDriver("GV5", value, 90, force)

    def getFrequencyOut(self):
        return self.getDriver("GV5")

    def queryFrequencyOut(self):
        if self.protocolHandler:
            precision = 2
            if self.protocolHandler:
                val = self.protocolHandler.queryProperty(self, 'GV5')
                if val != None:
                    if isinstance(val, int):
                        if precision > 1:
                            div = pow(10, precision)
                            fval = round(float(fval / div), precision)
                            self.updateFrequencyOut(fval, True)
                            return True
                    self.updateFrequencyOut(val, True)
                    return True
        return False
    """Use this method to update Current in IoX"""

    def updateCurrent(self, value, force: bool):
        return self.setDriver("GV6", value, 1, force)

    def getCurrent(self):
        return self.getDriver("GV6")

    def queryCurrent(self):
        if self.protocolHandler:
            precision = 2
            if self.protocolHandler:
                val = self.protocolHandler.queryProperty(self, 'GV6')
                if val != None:
                    if isinstance(val, int):
                        if precision > 1:
                            div = pow(10, precision)
                            fval = round(float(fval / div), precision)
                            self.updateCurrent(fval, True)
                            return True
                    self.updateCurrent(val, True)
                    return True
        return False
    """Use this method to update Pressure in IoX"""

    def updatePressure(self, value, force: bool):
        return self.setDriver("GV7", value, 138, force)

    def getPressure(self):
        return self.getDriver("GV7")

    def queryPressure(self):
        if self.protocolHandler:
            precision = 1
            if self.protocolHandler:
                val = self.protocolHandler.queryProperty(self, 'GV7')
                if val != None:
                    if isinstance(val, int):
                        if precision > 1:
                            div = pow(10, precision)
                            fval = round(float(fval / div), precision)
                            self.updatePressure(fval, True)
                            return True
                    self.updatePressure(val, True)
                    return True
        return False
    """Use this method to update Voltage in IoX"""

    def updateVoltage(self, value, force: bool):
        return self.setDriver("GV8", value, 72, force)

    def getVoltage(self):
        return self.getDriver("GV8")

    def queryVoltage(self):
        if self.protocolHandler:
            precision = 2
            if self.protocolHandler:
                val = self.protocolHandler.queryProperty(self, 'GV8')
                if val != None:
                    if isinstance(val, int):
                        if precision > 1:
                            div = pow(10, precision)
                            fval = round(float(fval / div), precision)
                            self.updateVoltage(fval, True)
                            return True
                    self.updateVoltage(val, True)
                    return True
        return False

    def queryAll(self):
        self.queryStatus()
        self.queryRunning()
        self.queryZeroSpeed()
        self.queryAlarm()
        self.queryFault()
        self.queryFrequencyRef()
        self.queryFrequencyOut()
        self.queryCurrent()
        self.queryPressure()
        self.queryVoltage()

    def Query(self, command):
        try:
            if self.protocolHandler:
                return self.protocolHandler.processCommand(self, 'Query')
            return False
        except Exception as ex:
            LOGGER.error(f'failed parsing parameters ... ')
            return False
    """This is a list of commands that were defined in the nodedef"""
    commands = {'x_query': Query}
