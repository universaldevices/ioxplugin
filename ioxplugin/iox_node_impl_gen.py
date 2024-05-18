import os
from .log import LOGGER

'''
This class creates an implemenation class for the Node class
Methods of this class should be implemented by developers
'''
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

    def __init__(self, plugin):
        self.plugin = plugin

    def setController(self, controller):
        self.controller = controller

    ####
    #  You need to implement these methods!
    ####

    ####
    # MANDATORY
    # This method is called by IoX to set a property
    # in the node/device or service
    ####
    def setProperty(self, node, property_id, value):
        try:
            return True
        except Exception as ex:
            LOGGER.error(f'setProperty {property_id} failed .... ')
            return False
    
    ####
    # MANDATORY
    # This method is called by IoX to query a property
    # in the node/device or service. Return the actual 
    # value
    ####
    def queryProperty(self, node, property_id):
        try:
            return True
        except Exception as ex:
            LOGGER.error(f'queryProperty {property_id} failed .... ')
            return False

    ####
    # MANDATORY if and only if you have commands
    # This method is called by IoX to send a command 
    # to the node/device or service
    ####
    def processCommand(self, node, command_name, **kwargs):
        try:
            LOGGER.info(f"Processing command {command_name}") 
            if kwargs != None:
                for key, value in kwargs.items():
                    LOGGER.info(f"-param: {key}: {value}")
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    ####
    # MANDATORY if and only if you have commands
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
    # MANDATORY 
    # This method is called in order to get a unique address for your newly created node
    # for the given nodedef_id
    ####
    def getNodeAddress(self, nodedef_id):
        try:
            #do any mapping you wish. 
            return nodedef_id
        except Exception as ex:
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


    ####
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
    # This method is called when a new node as been added to the system.
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
    #This method is called upon start and gives you all the configuration parameters
    #used to initialize this plugin including the store, version, etc.
    ####
    def processConfig(self, config):
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
    # Call this method to update a property for a node.
    # The plugin already creates an implementation for you such that you can 
    # call something like updateHeatSetpoint(). This said, however, for dynamically
    # generated code/classes, you might not actually know the method naems. In those
    # cases, you can use this method instead.
    # You can use the text just as an arbitrary/freeform text that is displayed as is
    # in the clients without any processing.
    ###
    def setProperty(node_addr:str, property_id:str, value, force:bool, text:str=None):
        try:
            node = self.getNode(node_addr)
            if node == None:
                LOGGER.error(f"Set property failed for {node_address}")
                return False
             return node.setDriver(property_id, value, force=force, text=text)
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

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

    def create(self):
        if os.path.exists(self.file_path): 
            LOGGER.info(f"{self.file_path} already exists ... ignoring")
            #do not redo if already exists
            return
        with open(self.file_path, 'w') as file:
            file.write(IMPL_PH_TEMPLATE.replace("__PROTOCOL_HANDLER_CLASS__",self.class_name))