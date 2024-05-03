
import astor
from nodedef import NodeDefs, NodeDefDetails, NodeProperties
from plugin_meta import PluginMetaData
from log import LOGGER
import ast_util
from iox_node_gen import IoXNodeGen


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
        imports = ast_util.astCreateImports()
        python_code = astor.to_source(imports)
        with open(file_path, 'w') as file:
            file.write(python_code)

        version_import = ast_util.astCreateImport("version")
        python_code = astor.to_source(version_import)
        with open(file_path, 'a') as file:
            file.write(python_code)

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
            import_stmt = ast_util.astCreateImportFrom(nd.getPythonClassName(), nd.getPythonClassName())
            python_code = astor.to_source(import_stmt)
            with open(file_path, 'a') as file:
                file.write(python_code)

        global_defs = ast_util.astCreateGlobals(True)
        for global_def in global_defs:
            python_code = astor.to_source(global_def)
            with open(file_path, 'a') as file:
                file.write(python_code)

        main_body = ast_util.astCreateMainFunc(self.controllerNode.getPythonClassName()) 
        python_code = astor.to_source(main_body)
        with open(file_path, 'a') as file:
            file.write(python_code)

        for child in children:
            child['parent'] = self.controllerNode.id

        for ndi in nodedefs:
            ndef = nodedefs[ndi]
            file_path=f'{self.path}/{ndef.getPythonFileName()}'
            ngen = IoXNodeGen(ndef, self.path)
            nc = ngen.create(children)
            python_code = astor.to_source(nc)
            with open(file_path, 'a') as file:
                    file.write(python_code)
