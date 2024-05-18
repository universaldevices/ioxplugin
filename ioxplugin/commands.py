#!/usr/bin/env python3

"""
Class for handling node commands
Copyright (C) 2024 Universal Devices
"""

import json
import os
from .editor import Editors 
from .log import LOGGER
from .validator import validate_id, getValidName


class CommandParam:

    def __init__(self, param):
        self.id = None
        self.name = None
        self.editor: None
        if param == None:
            LOGGER.debug("no parameters given for the command parameter")
            return

        try:
            if 'id' in param:
                self.id = param['id']
            if 'name' in param:
                self.name = param['name']
            if 'editor' in param:
                self.editor = Editors.getEditors().addEditor(param['editor']) 
        except Exception as ex:
            LOGGER.critical(str(ex))
            raise

    def toIoX(self, node_id:str, init_prop=None)->(str,str):
        nls=""
        param=""
        editor_id = self.editor.getEditorId()

        param=f"<p id=\"{self.id}\" editor=\"{editor_id}\""
        if init_prop:
            param+=f" init=\"{init_prop}\""
        param+="/>"
        if self.name:
            nls+=f"CMDP-{node_id}-{editor_id}-{self.id}-NAME = {self.name}"
        elif init_prop:
            nls+=f"CMDP-{node_id}-{editor_id}:{init_prop} = {self.name}"


        return param, nls

    def validate(self)->bool:
        return validate_id(self.id)



class CommandDetails:

    def __init__(self, command):
        self.id = None
        self.name = None
        self.params = {}
        self.init_prop = None
        if command == None:
            LOGGER.critical("no commands given for the command ... ")
            return

        try: 
            if 'id' in command:
                self.id = command['id']
            if 'name' in command:
                self.name = command['name']
            if 'params' in command:
                params = command['params']
                for param in params:
                    p = CommandParam(param)
                    self.params[p.id]=p

            if self.id.lower() == "query":
                self.id = "x_query"

        except Exception as ex:
            LOGGER.critical(str(ex))
            raise

    def toIoX(self, node_id:str)->(str,str):
        nls = ""
        cmd = ""
        if self.name:
            nls+=f"CMD-{node_id}-{self.id}-NAME = {self.name}"
        if len(self.params) == 0:
            cmd = f"<cmd id=\"{self.id}\"/>"
        else:
            cmd = f"<cmd id=\"{self.id}\">"
            for p in self.params:
                param=self.params[p]
                param_x, param_nls=param.toIoX(node_id, self.init_prop)
                if param_x:
                   cmd+=f"\n{param_x}"
                if param_nls:
                   nls+=f"\n{param_nls}"
            cmd += f"\n</cmd>"

        return cmd, nls

    def validate(self):
        try:
            if validate_id(self.id):
                rc = True
                for p in self.params:
                    if not self.params[p].validate():
                        rc = False
                return rc
            return False
        except Exception as ex:
            LOGGER.critical(str(ex))
            return False

    def hasParams(self):
        return len(self.params) > 0

    def getParams(self):
        return self.params


class Commands:
    def __init__(self, commands):
        self.acceptCommands={}
        self.sendCommands={}
        if commands == None:
            LOGGER.critical("no commands given for the commands class ... ")
            raise ValueError("no commands given for the commands class ... ")
            return
        try:
            if 'accepts' in commands:
                accepts = commands['accepts']
                for accept in accepts:
                    a = CommandDetails(accept)
                    self.acceptCommands[a.id]=a

            if 'sends' in commands:
                sends = commands['sends']
                for send in sends:
                    s = CommandDetails(send)
                    self.sendCommands[s.id]=s

        except Exception as ex:
            LOGGER.critical(str(ex))
            raise

    def addInit(self, type:str, property_id:str, property_name:str, editor_id:str):
        cmdList = self.acceptCommands
        if type == "sends":
            cmdList = self.sendCommands

        init = {
                "id": f"{property_id}",
                "name":f"set{getValidName(property_name)}",
                "params": [
                    {
                        "id" : property_id ,
                        "name": getValidName(property_name),
                        "editor":{
                            "idref": editor_id
                        }
                    }
                ]
        }
        i = CommandDetails(init)
        i.init_prop = property_id
        cmdList[i.id]=i
        return i

    def toIoX(self, node_id:str)->(str, str):
        nls = ""
        cmds = "<cmds>"
        try:
            if len (self.sendCommands) == 0:
                cmds += "\n<sends/>"
            else:
                cmds += "\n<sends>"
                for c in self.sendCommands:
                    cmd = self.sendCommands[c]
                    cmd_x, cmd_nls = cmd.toIoX(node_id)
                    if cmd_x:
                        cmds += f"\n{cmd_x}"
                    if cmd_nls:
                        nls += f"\n{cmd_nls}"
                cmds += "\n</sends>"

            if len (self.acceptCommands) == 0:
                cmds += "\n<accepts/>"
            else:
                cmds += "\n<accepts>"
                for c in self.acceptCommands:
                    cmd = self.acceptCommands[c]
                    cmd_x, cmd_nls = cmd.toIoX(node_id)
                    if cmd_x:
                        cmds += f"\n{cmd_x}"
                    if cmd_nls:
                        nls += f"\n{cmd_nls}"
                cmds += "\n</accepts>"
            cmds += "\n</cmds>"
            return cmds,nls

        except Exception as ex:
            LOGGER.critical(str(ex))
            return None, None

    def validate(self)->bool:
        try:
            rc = True
            for c in self.sendCommands:
                if not self.sendCommands[c].validate():
                    rc = False

            for c in self.acceptCommands:
                if not self.acceptCommands[c].validate():
                    rc = False

            return rc
        except Exception as ex:
            LOGGER.error(str(ex))
            return False
