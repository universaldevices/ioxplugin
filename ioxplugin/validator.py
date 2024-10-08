
#!/usr/bin/env python3

"""
Useful validation routines
Copyright (C) 2024 Universal Devices
"""
from .log import PLUGIN_LOGGER
import re

def validate_id(id)->bool:
    try:
        if id == None or id == '':
            PLUGIN_LOGGER.critical('validate_id - id does not exist ... ') 
            return False

        #cannot have spaces in ids
        if re.search(" ", id):
            PLUGIN_LOGGER.critical(f'\"{id}\": ids cannot have spaces in between' )
            return False

        return True

    except Exception as ex:
        PLUGIN_LOGGER.critical(str(ex))
        return False

def getValidName(name:str, capitalize=True)->str:
    if name == None:
        return "_Null_Name"
    name = name.replace(' ','')
    if capitalize:
        return name[0].upper() + name[1:]
    return name