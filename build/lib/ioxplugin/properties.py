#!/usr/bin/env python3

"""
Python class representing all properties 
Copyright (C) 2024 Universal Devices
"""

import json
import os
from .log import LOGGER

PROPERTIES_SCHEMA_FILE="schemas/properties.schema.json"

class PropertyDetails:
    def __init__(self, elements):
        try:
            val = elements['enum'][0]
            parsed_list = [item.strip() for item in val.split('|')]
            self.id = parsed_list[1] 
            self.description = parsed_list[0] 
        except Exception as ex:
            LOGGER.critical(str(ex))
            raise

class Properties:
    def __init__(self):
       self.properties = {}
       try:
            with open(PROPERTIES_SCHEMA_FILE, 'r') as file:
                json_data = json.load(file)
                self.__init_elements(json_data)
       except Exception as ex:
            LOGGER.critical(str(ex))
            raise

    def __init_elements(self, properties:str)->object:
       all = properties['oneOf']
       if all == None: 
            return None
       for p in all: 
            prD = PropertyDetails(p)
            self.properties[prD.id]=prD

    def getAll(self):
        return self.properties

    def getProperty(self, property:str)->PropertyDetails:
        return self.properties[property]
