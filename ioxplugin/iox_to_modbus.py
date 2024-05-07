
#!/usr/bin/env python3

"""
Manages iox to modbus mappings 
Copyright (C) 2024 Universal Devices
"""
from .log import LOGGER
import os
from .node_properties import NodePropertyDetails, NodeProperties
from .nodedef import NodeDefs, NodeDefDetails
from .plugin import Plugin
from .iox_transport import *

MODBUS_REGISTER_TYPES=('coil', 'discrete-input', 'input', 'holding')
MODBUS_REGISTER_DATA_TYPES=('int16','uint16','int32','uint32','float32','string')

MODBUS_COMMUNICATION_MODES=('TCP', 'Serial')
MODBUS_ADDRESSING_MODES=('0-based', '1-based')


class ModbusComm:
    def __init__(self, comm_data):
        if comm_data == None:
            raise Exception ("Need comm data for modbus ...")
            return
        self.addressing_mode = '1-based'
        self._transport:IoXTransport = None
        self.transport = None 
        try: 
            if 'transport' in comm_data:
                self._transport:IoXTransport = IoXTransport(comm_data['transport'])
            if 'addressing_mode' in comm_data:
                self.addressing_mode = comm_data['addressing_mode']
        except Exception as ex:
            raise

    def connect(connection_params)->bool:
        if not self._transport.getMode() in MODBUS_COMMUNICATION_MODES:
            raise Exception (f"{self.communication_mode} is not a valid communication mode for this plugin ..")
            return False

        self.transport=self._transport.getTransport()
        if self.transport == None:
            raise Exception ("Invalid transport params ... ")
            return False

        return self.transport.connect()

class ModbusRegister:
    def __init__(self, protocol_data):
        if protocol_data == None:
            raise Exception ("Need protocol data ...")
        self.register_address = None
        self.register_type = None
        self.register_data_type = None
        self.num_registers = 1
        self.scale = 1

        try:
            if 'register_address' in protocol_data:
                self.register_address = protocol_data['register_address']
            if 'register_type' in protocol_data:
                self.register_type = protocol_data['register_type']
            if 'register_data_type' in protocol_data:
                self.register_data_type = protocol_data['register_data_type']
            if 'num_registers' in protocol_data:
                self.num_registers = protocol_data['num_registers']
            if 'scale' in protocol_data:
                self.scale = protocol_data['scale']

            if self.register_address == None:
                raise Exception("Expected a register address ... ")

            if self.register_type == None:
                self.register_type = 'input' 
                self.register_data_type = 'uint16'

            if self.register_data_type ==  None:
                self.register_data_type = 'uint16'

            if not self.register_type in MODBUS_REGISTER_TYPES:
                raise Exception(f"{self.register_type} is not a valid modbus register type ...")

            if not self.register_data_type in MODBUS_REGISTER_DATA_TYPES:
                raise Exception(f"{self.register_data_type} is not a valid modbus register data type ...")


            if self.register_data_type == 'int16' or self.register_data_type == 'uint16':
                self.num_registers = 1
            elif self.register_data_type == 'int32' or self.register_data_type == 'uint32':
                self.num_registers = 2
            elif self.register_data_type == 'float32': 
                self.num_registers = 2

        except Exception as ex:
            raise

        def getRegisterValue(self):
            try:
                #get the value from modbus sending it the number of registers to be read
                val = 1
                if self.register_data_type == 'string':
                    return str(val)

                return (val * self.scale)
            except Exception as ex:
                LOGGER.critical(str(ex))
                return -1
        
        def setRegisterValue(self, value)->bool:
            try:
                if value == None:
                    return False
                #get the value from modbus sending it the number of registers to be read
                if self.register_data_type == 'string' and not isinstance(value, str):
                    LOGGER.error(f"{value} is not a string ")
                    return False
                    #set the string value
                    return True

                value = (value / scale)
                #set the value
                return True
            except Exception as ex:
                LOGGER.critical(str(ex))
                return False 

class ModbusIoXNode:
    def __init__(self, node:NodeDefDetails):
        self.registers = {}
        if node == None:
            LOGGER.critical("No node definitions provided ...")
            raise Exception ("No node definitions provided ...")
        try:
            nps:NodeProperties=node.properties
            if nps == None:
                raise Exception (f"No properties for {node.name} ...")

            protocol_data = nps.getProtocolData()
            if protocol_data == None or len (protocol_data) == 0:
                raise Exception (f"No protocol data for {node.name} ...")

            for pid in protocol_data:
                self.registers[pid]=ModbusRegister(protocol_data[pid])
        except Exception as ex:
            LOGGER.critical(str(ex))
            raise

    def queryProperty(property_id:str):
        if property_id == None:
            LOGGER.error("You need to have a property id ...")
            return None
        mregister:ModbusRegister = self.registers[property_id]
        if mregister == None:
            LOGGER.error(f"No registers for {property_id}")
            return None
        return mregister.getRegisterValue()

    def setProperty(property_id:str, value):
        if property_id == None or value == None:
            LOGGER.error("You need to have a property id and value ...")
            return None
        mregister:ModbusRegister = self.registers[property_id]
        if mregister == None:
            LOGGER.error(f"No registers for {property_id}")
            return None
        return mregister.setRegisterValue(value)

class ModbusIoX:
    def __init__(self, plugin:Plugin):
        self.nodes = {}
        if plugin == None or plugin.nodedefs == None:
            raise Exception ("No plugin and/or node definitions provided ...")
        try:
            if not plugin.protocol.isModbus():
                LOGGER.error("This plugin does not support modbus")
                raise Exception("This plugin does not support modbus")

            nodedefs=plugin.nodedefs.getNodeDefs()
            for n in nodedefs: 
                node:NodeDefDetails=nodedefs[n]
                if not node.isController:
                    self.nodes[node.id]=ModbusIoXNode(node)
        except Exception as ex:
            LOGGER.critical(str(ex))
            raise

    def queryProperty(node_id:str, property_id:str):
        if nodeid == None or property_id == None:
            LOGGER.error("Need node id and property id ...")
            return None

        node:ModbusIoXNode = self.nodes[node_id]
        if node == None:
            LOGGER.error(f"No node for {node_id} ...")
            return None

        return node.queryProperty(propety_id) 

    def setProperty(node_id:str, property_id:str, value):
        if nodeid == None or property_id == None or value == None:
            LOGGER.error("Need node id, property id, and value ...")
            return None

        node:ModbusIoXNode = self.nodes[node_id]
        if node == None:
            LOGGER.error(f"No node for {node_id} ...")
            return None

        return node.setProperty(propety_id, value) 
