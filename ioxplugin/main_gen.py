
import astor
from .nodedef import NodeDefs, NodeDefDetails, NodeProperties
from .plugin_meta import PluginMetaData
from .log import LOGGER
from ioxplugin import ast_util
from .iox_node_gen import IoXNodeGen
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
        if create_main:
            #do not recreate the main
            with open(file_path, 'w') as file:
                imports = ast_util.astCreateImports()
                python_code = astor.to_source(imports)
                file.write(python_code)
                
                version_import = ast_util.astCreateImport("version")
                python_code = astor.to_source(version_import)
                file.write(python_code)

                #ioxplugin_import = ast_util.astCreateImport("ioxplugin")
                #ioxplugin_code = astor.to_source(ioxplugin_import)
                #file.write(ioxplugin_code)

                ioxplugin_from_import = ast_util.astCreateImportFrom("ioxplugin","Plugin")
                ioxplugin_code = astor.to_source(ioxplugin_from_import)
                file.write(ioxplugin_code)

                imp_from_import = ast_util.astCreateImportFrom(self.plugin_info.getPythonPHClassName(), 
                        self.plugin_info.getPythonPHClassName())
                ioxplugin_code = astor.to_source(imp_from_import)
                file.write(ioxplugin_code)
                file.write(f"\nPLUGIN_FILE_NAME = \'{self.plugin_info.plugin_file}\'\n")


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
            with open(file_path, 'a') as file:
                import_stmt = ast_util.astCreateImportFrom(nd.getPythonClassName(), nd.getPythonClassName())
                python_code = astor.to_source(import_stmt)
                file.write(python_code)

                global_defs = ast_util.astCreateGlobals(True)
                for global_def in global_defs:
                    python_code = astor.to_source(global_def)
                    file.write(python_code)

                main_body = ast_util.astCreateMainFunc(self.controllerNode.getPythonClassName(), self.plugin_info.getPythonPHClassName()) 
                python_code = astor.to_source(main_body)
                file.write(python_code)

        for child in children:
            child['parent'] = self.controllerNode.id

        for ndi in nodedefs:
            ndef = nodedefs[ndi]
            #file_path=f'{self.path}/{ndef.getPythonFileName()}'
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