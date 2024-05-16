#!/usr/bin/env python3

"""
Class for handling node properties
Copyright (C) 2024 Universal Devices
"""

from .editor import Editors
from .log import LOGGER
from .validator import validate_id 



class NodePropertyDetails:
    def __init__(self, node_property):
        self.id = None
        self.name = None
        self.is_settable = False
        self.editor = None
        self.hide = False
        self.protocol_data = None

        if node_property == None:
            return
        try: 
            if 'id' in node_property:
                val = node_property['id']
                parsed_list = [item.strip() for item in val.split('|')]
                self.id=parsed_list[1] if len(parsed_list)==2 else val
            if 'name' in node_property:
                self.name = node_property['name']
            if 'is_settable' in node_property:
                self.is_settable = node_property['is_settable']
            if 'editor' in node_property:
                self.editor = Editors.getEditors().addEditor(node_property['editor'])
            if 'hide' in node_property:
                self.hide = node_property['hide']
            if 'protocol' in node_property:
                self.protocol_data = node_property['protocol']
        except Exception as ex:
            LOGGER.critical(str(ex))
            raise

    def isSet(self)->bool:
        return self.is_settable 

    def toIoX(self, node_id:str):
        editorId = self.editor.getEditorId()
        nls = ""
        st = f"<st id=\"{self.id}\" editor=\"{editorId}\" />"
        nls = f"ST-{node_id}-{self.id}-NAME = {self.name}"
        return st, nls

    def validate(self):
        return validate_id(self.id)


class NodeProperties:
    def __init__(self, node_properties):
        self.node_properties={}
        if node_properties == None:
            LOGGER.critical("no node properties were given ... ")
            return
        try:
            for node_property in node_properties:
                np = NodePropertyDetails(node_property)
                self.node_properties[np.id]=np
                
        except Exception as ex:
            LOGGER.critical(str(ex))
            raise

    def getProperty(self, property):
        if property == None:
            LOGGER.warn("property is null ... ")
            return

        return self.node_properties[property]

    def toIoX(self, node_id:str):
        nls = ""
        sts = "<sts>"
        try:
            for np in self.node_properties:
                node_property = self.node_properties[np]
                sts_np, nls_np = node_property.toIoX(node_id)
                if sts_np:
                    sts += f"\n{sts_np}"
                if nls_np:
                    nls += f"\n{nls_np}"
            sts += "\n</sts>"
            return sts, nls
        except Exception as ex:
            LOGGER.critical(str(ex))

    '''
        Returns a dictory of the form {property_id, protocol_data_object}
    '''
    def getProtocolData(self):
        out = {}
        for np in self.node_properties:
            node_property:NodePropertyDetails = self.node_properties[np]
            out[node_property.id] = node_property.protocol_data

        return out

    def getPG3Drivers(self):
        drivers = []
        for np in self.node_properties:
            prop = self.node_properties[np]
            if prop == None:
                continue
            editor = Editors.getEditors().editors[prop.editor.getEditorId()]
            drivers.append(
                {
                  "driver": f"{prop.id}", 
                  "value": 0, 
                  "uom": editor.uom,
                  "name": f"{prop.name}"
                }
            )
        return drivers

    def validate(self):
        try:
            rc = True
            for n in self.node_properties:
                if not self.node_properties[n].validate():
                    rc = False
            return rc
        except Exception as ex:
            LOGGER.critical(str(ex))


    def getAll(self):
        return self.node_properties