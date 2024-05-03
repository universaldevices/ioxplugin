#!/usr/bin/env python3

"""
Python class representing all UOMs and options
Copyright (C) 2024 Universal Devices
"""

import json
import os
from .log import LOGGER

UOM_SCHEMA_FILE="schemas/uom.schema.json"

INDEX_UOM = 25
PERCENT_UOM = 51

class UOMOption:
    def __init__(self, element):
        if element == None:
            return
        self.id=None
        self.min=None
        self.max=None
        self.name=None
        try:
            if 'enum' in element:
                self.id = element['enum'][0]
            elif 'min' in element:
                self.min=element['min']
            elif 'max' in element:
                self.max=element['max']
            self.name = element['description']
        except Exception as ex:
            LOGGER.log(str(ex))
            raise

class UOMDetails:
    def __init__(self, elements):
        
        self.options = {}
        try:
            val = elements['enum'][0]
            parsed_list = [item.strip() for item in val.split('|')]
            self.uom = int(parsed_list[1])
            self.description = parsed_list[0] 
            if 'oneOf' in elements:
                self.__init_options(elements ['oneOf'])
        except Exception as ex:
            LOGGER.log(str(ex))
            raise

    def __init_options(self, options):
        try:
            if options == None:
                return
            for option in options:
                uomOption = UOMOption(option)
                self.options[uomOption.id]=uomOption
        except Exception as ex:
            LOGGER.log(str(ex))
            raise

class UOMs:
    def __init__(self):
       self.uoms = {}
       try:
            with open(UOM_SCHEMA_FILE, 'r') as file:
                json_data = json.load(file)
                self.__init_elements(json_data)
       except Exception as ex:
            LOGGER.log(str(ex))
            raise

    def __init_elements(self, json_data:str)->object:
       all = json_data['oneOf']
       if all == None: 
            return None
       for u in all: 
            uomD = UOMDetails(u)
            self.uoms[uomD.uom]=uomD

    def getAll(self):
        return self.uoms

    def getUOM(self, uom:int)->UOMDetails:
        return self.uoms[uom]

    @staticmethod
    def isIndex(uom:int):
        return uom == INDEX_UOM

    @staticmethod
    def isPercent(uom:int):
        return uom == PERCENT_UOM

       