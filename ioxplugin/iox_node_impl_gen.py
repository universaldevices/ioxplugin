
'''
This class creates an implemenation class for the Node class
Methods of this class should be implemented by developers
'''
import ast, astor, os
from .nodedef import NodeDefDetails, NodeProperties
from .commands import CommandDetails, CommandParam
from .log import LOGGER
from .validator import getValidName
from ioxplugin import ast_util 
from .uom import UOMs
from .editor import Editors

PROCESS_COMMAND_TEMPLATE='''
    def processCommand(self, command_name, **kwargs):
        try:
            for key, value in kwargs.items():
                print(f"{key}: {value}")
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False
    '''

class IoXNodeImplGen():
    def __init__(self, path:str, file_name:str, class_name:str):
        if class_name == None or file_name == None or path == None:
            LOGGER.critical("need path, filename, and class_name ")
            raise Exception ("need path, filename, and class_name") 

        self.file_path=f'{path}/{file_name}'
        self.class_name = class_name
        self.class_def = None

    def create_command_method(self, command_name:str, params:[]):
        if command_name == None:
            LOGGER.error("command_name cannot be None ...")
            raise Exception("command_name cannot be None ...")
            return None
        error = []

        ast_params = [ast.arg(arg='self')]
        if params and len(params)>0:
           for param in params:
               ast_params.append(ast.arg(arg=param))

        return_true = ast_util.astReturnBoolean(True)
        error.append(ast_util.astLogger("error", f"{command_name} failed .... "))
        error.append(ast_util.astReturnBoolean(False))
        body = ast_util.astTryExcept([return_true], error)
    

        method = ast.FunctionDef(
                name=command_name,
                args=ast.arguments(
                    args=ast_params,
                    defaults=[],
                    kwonlyargs=[], kw_defaults=[], vararg=None, kwarg=None
                ),
                body=[body],
                keywords=[],
                decorator_list=[]
        )
        return method

    def create(self):
        if os.path.exists(self.file_path): 
            LOGGER.info(f"{self.file_path} already exists ... ignoring")
            #do not redo if already exists
            return
        imports = ast_util.astCreateImports()
        python_code = astor.to_source(imports)
        with open(self.file_path, 'w') as file:
            file.write(python_code)

        global_defs = ast_util.astCreateGlobals(logger_only=True)
        for global_def in global_defs:
            python_code = astor.to_source(global_def)
            with open(self.file_path, 'a') as file:
                file.write(python_code) 

        #if self.nodedef.isController:
        #    for child in children:
        #        import_stmt = ast_util.astCreateImportFrom(child['node_class'], child['node_class'])
        #        python_code = astor.to_source(import_stmt)
        #        with open(file_path, 'a') as file:
        #            file.write(python_code) 

        # Create the class for the node 
        self.class_def = ast.ClassDef(
            name=f'{self.class_name}',
            bases=[],
            keywords=[],
            body=[],
            decorator_list=[]
        )
        
        self.class_def.body.append(ast_util.astAddImplClassInit())
        self.class_def.body.append(ast_util.astComment('You need to implement these methods ....'))
        self.class_def.body.append(self.create_command_method('setProperty', ['property_id', 'value']))
        self.class_def.body.append(self.create_command_method('queryProperty', ['property_id']))
        #self.class_def.body.append(self.create_command_method('processCommand', ['param_list']))
        self.class_def.body.append(self.create_command_method('discover', None))
        python_code = astor.to_source(self.class_def)
        with open(self.file_path, 'a') as file:
            file.write(python_code)
            file.write(PROCESS_COMMAND_TEMPLATE) 