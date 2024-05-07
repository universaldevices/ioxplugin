#!/usr/bin/env python3

"""
Protocol processor
Copyright (C) 2024 Universal Devices
"""

from .log import LOGGER



class Protocol:

    def __init__(self, protocol):
        if not protocol['name']:
            raise Exception("A protocol needs name ...")
        self.config = None
        self.name = protocol['name']
        if 'config' in protocol:
            self.config = protocol['config']

    def isModbus(self):
        return self.name == "Modbus"

    def isShelly(self):
        return self.name == "Shelly"

    def isProprietary(self):
        return self.name == "Proprietary"
