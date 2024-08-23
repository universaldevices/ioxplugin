#!/usr/bin/env python3

"""
Protocol processor
Copyright (C) 2024 Universal Devices
"""

from .log import PLUGIN_LOGGER



class Protocol:

    def __init__(self, protocol):
        if not protocol['name']:
            raise Exception("A protocol needs name ...")
        self.protocol = protocol
        self.name = protocol['name']

    """
        Returns the details of the protocol which might be 
        different for each. This is a dictionary
    """
    def getDetails(self):
        return self.protocol 

    def isModbus(self):
        return self.name == "Modbus"

    def isShelly(self):
        return self.name == "Shelly"

    def isProprietary(self):
        return self.name == "Proprietary"
