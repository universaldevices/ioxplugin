
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

IMPL_PH_TEMPLATE='''
import udi_interface, os, sys, json, time
LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

class __PROTOCOL_HANDLER_CLASS__:
    ##
    #Implementation and Protocol Handler class
    ##

    ##
    #The plugin has all the information that's stored in the json file.
    #The controller allows you to communicate with the underlying system (PG3).
    #

    def __init__(self, plugin, controller):
        self.plugin = plugin
        self.controller = controller

    ####
    #  You need to implement these methods!
    ####

    ####
    # This method is called by IoX to set a property
    # in the node/device or service
    ####
    def setProperty(self, node, property_id, value):
        try:
            return True
        except Exception as ex:
            LOGGER.error(f'setProperty failed .... ')
            return False
    
    ####
    # This method is called by IoX to query a property
    # in the node/device or service
    ####
    def queryProperty(self, node, property_id):
        try:
            return True
        except Exception as ex:
            LOGGER.error(f'queryProperty failed .... ')
            return False

    ####
    # This method is called by IoX to send a command 
    # to the node/device or service
    ####
    def processCommand(self, node, command_name, **kwargs):
        try:
            for key, value in kwargs.items():
                print(f"{key}: {value}")
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    ####
    # This method is called at start so that you can do whatever initialization
    # you need. If you return false, the status of the controller node shows 
    # disconnected. So, make sure you return the correct status.
    ####
    def start(self)->bool:
        try:
            return True
        except Exception as ex:
            LOGGER.error(f'start failed .... ')
            LOGGER.error(str(ex))
            return False

    ####
    # This method is called at stop so that you can do whatever cleaning up 
    # that's necessary. The result is not checked so make sure everything is 
    # cleaned up
    ####
    def stop(self)->bool:
        try:
            return True
        except Exception as ex:
            LOGGER.error(f'discover failed .... ')
            return False


    # This method is called by IoX to discover  
    # nodes/devices or service
    ####
    def discover(self)->bool:
        try:
            return True
        except Exception as ex:
            LOGGER.error(f'discover failed .... ')
            return False


    ####
    # Notification methods
    ####

    ####
    # This method is called when a new node as been added to the system
    ####
    def nodeAdded(self, node):
        try:
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    ####
    # This method is called when a new node as been removed from the system
    ####
    def nodeRemoved(self, node)->bool:
        try:
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    ####
    # This method is called with the configuration parameters have changed. The parameter is a dictionary of key/value
    # pairs
    ####
    def configChanged(self, param)->bool:
        try:
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    ####
    # This method is called with the configuration is done. This is rarely used as its main function is to facilitate 
    ####
    def configDone(self)->bool:
        try:
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    ####
    # This method is called with custom data. Rarely used ...  
    ####
    def customData(self, data)->bool:
        try:
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    ####
    # This method is called when adding a node to the system is completed successfully. Make sure you use isinstance
    # to ensure it's your node and then do any additional processing necessary.
    # oauth
    ####
    def addNodeDone(self, node)->bool:
        try:
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    ####
    # This method is called when files are uplaoded. The path is the directory to which you can find the files
    # Do whatever you need with the files because they will be removed once you are done.
    ####
    def filesUploaded(self, path:str)->bool:
        try:
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    ####
    # This method is called at every short poll interval. The result is not checked
    ####
    def shortPoll(self)->bool:
        try:
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    ####
    # This method is called at every long poll interval. The result is not checked
    ####
    def longPoll(self)->bool:
        try:
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    ####
    # This method is called with the custom parameters provided by the user.
    # It is a dictionary so you get the parameter name/key and the value. e.g.
    # params['path']
    ####
    def processParams(self, params:Custom)->bool:
        try:
            return True
        except Exception as ex:
            LOGGER.error(f'process param failed .... ')
            return False

    ###
    # Convenient methods to access the system
    ###

    ###
    # Call this method to remove the blue ribbon that requests the attention of the user
    ###
    def clearNotices(self):
        self.controller.poly.Notices.clear()

    ###
    # Call this method to add a blue ribbon with notice for the customer to take action
    # This is a dictionary. So, you would need to provide the key (i.e. the parameter's name)
    # And a string that will be displayed in the ribbon
    ###
    def setNotices(self, key:str, notice:str) :
        if key == None or notice == None:
            LOGGER.error("setNotices requires both the key and the notice.")
            return
        self.controller.poly.Notices[key]=notice

    ###
    # Call this method to get a node and then call its methods for updating
    # their state in IoX. Take a look at the class that implements this node
    # it's always a good idea to use isinstance to make sure you are dealing 
    # with the correct node
    # The address is the address of the node.
    ###
    def getNode(self, address:str):
        return self.controller.poly.getNode()

    ###
    # If your plugin is an OAuth client, use this method to call APIs that 
    # automatically include all the tokens for authorization and authentication 
    ###
    def callOAuthApi(self, method='GET', url=None, params=None, body=None)->bool:
        return self.controller.callOAuthApi(method, url, params, body)

    '''

class IoXNodeImplGen():
    def __init__(self, path:str, file_name:str, class_name:str):
        if class_name == None or file_name == None or path == None:
            LOGGER.critical("need path, filename, and class_name ")
            raise Exception ("need path, filename, and class_name") 

        self.file_path=f'{path}/{file_name}'
        self.class_name = class_name
        self.class_def = None

#    def create_command_method(self, command_name:str, params:[]):
#        if command_name == None:
#            LOGGER.error("command_name cannot be None ...")
#            raise Exception("command_name cannot be None ...")
#            return None
#        error = []
#
#        ast_params = [ast.arg(arg='self')]
#        if params and len(params)>0:
#           for param in params:
#               ast_params.append(ast.arg(arg=param))
#
#        return_true = ast_util.astReturnBoolean(True)
#        error.append(ast_util.astLogger("error", f"{command_name} failed .... "))
#        error.append(ast_util.astReturnBoolean(False))
#        body = ast_util.astTryExcept([return_true], error)
#    
#
#        method = ast.FunctionDef(
#                name=command_name,
#                args=ast.arguments(
#                    args=ast_params,
#                    defaults=[],
#                    kwonlyargs=[], kw_defaults=[], vararg=None, kwarg=None
#                ),
#                body=[body],
#                keywords=[],
#                decorator_list=[]
#        )
#        return method

    def create(self):
        if os.path.exists(self.file_path): 
            LOGGER.info(f"{self.file_path} already exists ... ignoring")
            #do not redo if already exists
            return
#        imports = ast_util.astCreateImports()
#        python_code = astor.to_source(imports)
        with open(self.file_path, 'w') as file:
            file.write(IMPL_PH_TEMPLATE.replace("__PROTOCOL_HANDLER_CLASS__",self.class_name))
      #      file.write(python_code)
      #      global_defs = ast_util.astCreateGlobals(logger_only=True)
      #      for global_def in global_defs:
      #          python_code = astor.to_source(global_def)
      #          file.write(python_code) 

        #if self.nodedef.isController:
        #    for child in children:
        #        import_stmt = ast_util.astCreateImportFrom(child['node_class'], child['node_class'])
        #        python_code = astor.to_source(import_stmt)
        #        with open(file_path, 'a') as file:
        #            file.write(python_code) 

        # Create the class for the node 
        #self.class_def = ast.ClassDef(
        #    name=f'{self.class_name}',
        #    bases=[],
        #    keywords=[],
        #    body=[],
        #    decorator_list=[]
        #)
        
        #self.class_def.body.append(ast_util.astAddImplClassInit())
        #self.class_def.body.append(ast_util.astComment('You need to implement these methods ....'))
        #self.class_def.body.append(self.create_command_method('setProperty', ['node','property_id', 'value']))
        #self.class_def.body.append(self.create_command_method('queryProperty', ['node','property_id']))
        ##self.class_def.body.append(self.create_command_method('processCommand', ['param_list']))
        #self.class_def.body.append(self.create_command_method('discover', ['node']))
        #python_code = astor.to_source(self.class_def)
        #with open(self.file_path, 'a') as file:
            #file.write(python_code)
            #file.write(PROCESS_COMMAND_TEMPLATE) 