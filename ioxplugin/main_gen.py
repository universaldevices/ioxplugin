
import astor
from .nodedef import NodeDefs, NodeDefDetails, NodeProperties
from .plugin_meta import PluginMetaData
from .log import LOGGER
from ioxplugin import ast_util
from .iox_node_gen import IoXNodeGen
from .iox_main_template import IOX_MAIN_TEMPLATE
import os


class PluginMain:
    def __init__(self, path:str, plugin_info:PluginMetaData, node_defs:NodeDefs):
        self.plugin_info=plugin_info
        self.node_defs=node_defs
        self.path = path
        self.controllerNode = None

    def create(self):
        exec_name = self.plugin_info.getExecutableName()
        if exec_name == None:
            LOGGER.critical("need the executable name ...") 
            return False

        file_path = f'{self.path}/{exec_name}'
        create_main = not os.path.exists(file_path)

        self.controllerNode = None
        children = []
        #add import for each node
        nodedefs = self.node_defs.nodedefs
        for ndi in nodedefs:
            nd = nodedefs[ndi]
            if nd.isController:
                self.controllerNode = nd
            else:
                children.append(
                    {
                        'node_class': nd.getPythonClassName(),
                        'id': nd.id,
                        'name': nd.name,
                        'parent': None
                    }
                )

        if create_main:
            #do not recreate the main
            with open(file_path, 'w') as file:
                code = IOX_MAIN_TEMPLATE\
                .replace('__PROTOCOL_HANDLER_FILE__',self.plugin_info.getPythonPHClassName())\
                .replace('__PROTOCOL_HANDLER_CLASS__',self.plugin_info.getPythonPHClassName())\
                .replace('__PLUGIN_FILE_NAME__', self.plugin_info.plugin_file)\
                .replace('__CONTROLLER_NODE_FILE__',nd.getPythonClassName())\
                .replace('__CONTROLLER_NODE_CLASS__',nd.getPythonClassName())
                file.write(code)
                
                
        for child in children:
            child['parent'] = self.controllerNode.id

        for ndi in nodedefs:
            ndef = nodedefs[ndi]
            ngen = IoXNodeGen(ndef, self.path)
            nc = ngen.create(children)
    
    def generateVersion(self):
        versionFile = os.path.join(self.path, "version.py")
        with open(versionFile, 'w') as file:
            file.write(self.plugin_info.getVersion())

    def generateRequirements(self):
        requirementsFile = os.path.join(self.path, "requirements.txt")
        with open(requirementsFile, 'w') as file:
            reqs = self.plugin_info.getRequirements()
            for req in reqs:
                file.write(req)
                file.write('\n')