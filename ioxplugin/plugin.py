#!/usr/bin/env python3

"""
Plugin schema processor and validator
Copyright (C) 2024 Universal Devices
"""

#import fastjsonschema
import json,os
from .nodedef import NodeDefs
from .editor import Editors
from .plugin_meta import PluginMetaData
from .log import init_ext_logging, LOGGER
from .iox_profile import ProfileWriter
from .iox_node_gen import IoXNodeGen
from .main_gen import PluginMain
from .protocol import Protocol
from .iox_node_impl_gen import IoXNodeImplGen
import argparse


PLUGIN_SCHEMA_FILE="schemas/plugin.schema.json"

CMD_SCHEMA="schemas/commands.schema.json"
EDITOR_SCHEMA="schemas/editor.schema.json"
ICON_SCHEMA="schemas/icon.schema.json"
NODEP_SCHEMA="schemas/node.properties.schema.json"
NODE_SCHEMA="schemas/node.schema.json"
PMETA_SCHEMA="schemas/plugin.meta.schema.json"
PROP_SCHEMA="schemas/properties.schema.json"
UOM_SCHEMA="schemas/uom.schema.json"



class Plugin:

    def __init__(self, plugin_file, path:str=None, schema=PLUGIN_SCHEMA_FILE):
        self.path = os.path.dirname(plugin_file) if path == None else path
        self.path = './' if self.path == '' else self.path
        init_ext_logging(self.path)
        self.meta = None
        self.editors=Editors()
        self.nodedefs:NodeDefs = None
        self.protocol:Protocol = None
        
        self.isValid = False
        if plugin_file == None:
            LOGGER.critical("plugin file does not exist ... ")
            return

        self.profileWriter=ProfileWriter(True, self.path)

        try:
            self.isValid=self.validate_json(schema, plugin_file)
            if not self.isValid:
                LOGGER.critical("not a valid plugin configuration file ... ")
                return
            with open(plugin_file, 'r') as file:
                plugin_json = json.load(file)

            if 'plugin' in plugin_json:
                self.meta = PluginMetaData(plugin_json['plugin'])
                self.meta.setPluginFile(plugin_file)
            if 'editors' in plugin_json:
                self.editors.addEditors(plugin_json['editors'])
            if 'nodedefs' in plugin_json:
                self.nodedefs = NodeDefs(plugin_json['nodedefs'])
                self.nodedefs.addController(f"{self.meta.getName().replace(' ','_').capitalize()} Controller")
            if 'protocol' in plugin_json:
                self.protocol = Protocol(plugin_json['protocol'])

        except Exception as ex:
            raise

    def toIoX(self)->bool:
        if not self.validate():
            LOGGER.critical("invalid json file ... ")
            return False

        try:
            nodedefs, nls = self.nodedefs.toIoX()
            if nodedefs:
                self.profileWriter.writeToNodeDef(nodedefs)
            if nls:
                self.profileWriter.writeToNLS(nls)

            editors, nls = self.editors.toIoX()
            if editors:
                self.profileWriter.writeToEditor(editors)
            if nls:
                self.profileWriter.writeToNLS(nls)
        except Exception as ex:
            LOGGER.critical(str(ex))

        return True

    def validate_json(self, schema:str, payload:str)->bool:
        ''' 
            Does not suppot file refernences
        '''
        LOGGER.info('fastjsonschema does not currently support file references ... ignoring validation request.')
        return True

        #use later when supported
        if schema == None or json == None:
            return False
        try:
            with open(schema, 'r') as file:
                plugin_schema = json.load(file)
            with open(CMD_SCHEMA,'r') as file:
                cmd_schema = json.load(file)
            with open(EDITOR_SCHEMA,'r') as file:
                editor_schema = json.load(file)
            with open(ICON_SCHEMA,'r') as file:
                icon_schema = json.load(file)
            with open(NODEP_SCHEMA,'r') as file:
                nodep_schema = json.load(file)
            with open(NODE_SCHEMA,'r') as file:
                node_schema = json.load(file)
            with open(PMETA_SCHEMA,'r') as file:
                pmeta_schema = json.load(file)
            with open(PROP_SCHEMA,'r') as file:
                prop_schema = json.load(file)
            with open(UOM_SCHEMA,'r') as file:
                uom_schema = json.load(file)

            handlers={
                    'commands.schema.json': cmd_schema,
                    'editor.schema.json': editor_schema,
                    'icon.schema.json': icon_schema,
                    'node.properties.schema.json': nodep_schema,
                    'node.schema.json': node_schema,
                    'plugin.meta.schema.json': pmeta_schema,
                    'properties.schema.json': prop_schema,
                    'uom.schema.json': uom_schema
                    }

            #validate = fastjsonschema.compile(plugin_schema, handlers)
            #validate(payload)
            return True
        except Exception as ex:
            return False

    def validate(self):
        n = self.nodedefs.validate()
        e = self.editors.validate()

        return n and e
    
    def getPythonPHClassName(self):
        return self.meta.getPythonPHClassName()

    def getPythonPHFileName(self):
        return self.meta.getPythonPHFileName()

    def generateCode(self, path:str):
        try:
            if path == None:
                LOGGER.critical("need path to write python files to")
                raise Exception("path to write python files to")

            name = self.meta.getName()
            excecutableName = self.meta.getExecutableName()
            if name == None or excecutableName == None:
                LOGGER.critical("need name for the plugin and the executable")
                raise Exception("need name for the plugin and the executable")

            if self.nodedefs.size() == 0:
                LOGGER.critical("no nodedefs defined ...")
                raise Exception("no nodedefs")

            main = PluginMain(path, self.meta, self.nodedefs)
            main.create()
            main.generateRequirements()
            main.generateVersion()

            #now generate the proto handler/impl
            node_impl_gen=IoXNodeImplGen(path, self.getPythonPHFileName(), self.getPythonPHClassName())
            node_impl_gen.create()



        except Exception as ex:
            LOGGER.critical(str(ex))
            raise Exception(ex)

def generate_code():
    project_path = "/usr/home/admin/workspace/plugin-dev/ext"
    json_file = f"{project_path}/dimmer.iox_plugin.json"
    try:
        parser = argparse.ArgumentParser(description="the path IoX Plugin json file")
    
        parser.add_argument('project_path', type=str, help='path to the project directory')
        parser.add_argument('json_file', type=str, help='path to the json file')
        
        args = parser.parse_args()

        project_path = args.project_path
        json_file = args.json_file
    except SystemExit as ex:
        pass

    #print (project_path)
    #print (json_file)
    mod=Plugin(json_file, project_path)
    mod.toIoX()
    mod.generateCode(project_path)



if __name__ == "__main__":
    generate_code()

