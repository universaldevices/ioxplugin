CONTROLLER_TEMPLATE_HEADER='''
import udi_interface, os, shutil, sys, json, time, threading
from udi_interface import OAuth
LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom
from ioxplugin import Plugin, OAuthService

DATA_PATH='./data'
'''

CONTROLLER_TEMPLATE_BODY='''

    def __initOAuth(self):
        if self.plugin and self.plugin.meta and self.plugin.meta.getEnableOAUTH2():
            self.oauthService = OAuthService(self.polyglot)
            self.poly.subscribe(polyglot.OAUTH, self.__oauthHandler)

    def __configHandler(self, param):
        try:
            if os.path.exists(DATA_PATH):
                self.filesUploaded(DATA_PATH)
                shutil.rmtree(DATA_PATH)
            if param:
                return self.processConfig(param)
        except Exception as ex:
            LOGGER.warn(str(ex))

        return True

    def __bonjourHandler(self, message):
        try:
            command = message['command']
            if command == None or command != "bonjour": 
                return
            mdns = message['mdns']
            self.processMDNSResults(mdns)
        except Exception as ex:
            LOGGER.error(str(ex))

    def __start(self):
        LOGGER.info(f'Starting... ')
        try:
            self.poly.setCustomParamsDoc()
            if not self.configDoneAlready:
                with self.configDone:
                    result = self.configDone.wait(timeout=10)
                    if not result:
                        #timedout
                        LOGGER.info("timed out while waiting for configDone")
                        self.__updateStatus(0, True) 
                        return False
            if self.start():
                self.__addAllNodes()
                self.poly.updateProfile()
                self.__updateStatus(1, True) 
                return True
            else:
                LOGGER.info("failed processing config ...")
                self.__updateStatus(0, True) 
                return False
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    def __stop(self):
        LOGGER.info(f'Stopping ... ')
        self.stop()
        self.__updateStatus(0,True)
        return True

    def __poll(self, polltype):
        if not self.configDoneAlready:
            return
        if 'shortPoll' in polltype:
            self.shortPoll()
        elif 'longPoll' in polltype:
            self.longPoll()

    def __addAllNodes(self):
        config = self.poly.getConfig()
        if config is None or config['nodes'] is None or len(config['nodes']) <= 0:
            config = {}
            config['nodes'] = []

        if self.plugin.areNodesStatic():
            for child in self.children:
                try:
                    config['nodes'].append({'nodeDefId': child['id'], 'address':
                    child['id'], 'name': child['name'],
                    'primaryNode': child['parent']})
                except Exception as ex:
                    LOGGER.error(str(ex))
                    return

        for node in config['nodes']:
            if node['nodeDefId'] == self.id:
                continue
            if not self.__addNodeFromConfig(node):
                return
        LOGGER.info(f'Done adding nodes ...')
    
    def __getNodeClass(self, nodeDefId:str)->str:
        for child in self.children:
            if child['id'] == nodeDefId:
                return child['node_class']
        return None

    def __addNodeFromConfig(self, node_info) ->bool:
        if node_info is None:
            LOGGER.error('node cannot be null')
            return False
        try:
            node_class = self.__getNodeClass(node_info['nodeDefId'])
            if node_class == None:
                return False 
            node_address=self.getNodeAddress(node_info['nodeDefId'])
            cls = globals()[node_class]
            node = cls(self.poly, self.plugin, node_info['primaryNode'], node_address, node_info['name'])
            if node is None:
                LOGGER.error(f'invalid noddef id ...')
                return False
            else:
                node_r = self.poly.addNode(node)
                if node_r:
                    return True
                LOGGER.error("failed adding node ... ") 
                return False
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    def __addNodeDoneHandler(self, node):
        try:
            if node['nodeDefId'] == self.id:
                return True
            return self.addNodeDone(node)

        except ValueError as err:
            LOGGER.error(str(x))
            return False

    def __configDoneHandler(self):
        rc = False
        if self.oauthService:
            # First check if user has authenticated
            try:
                self.oauthService.getAccessToken()
                # If getAccessToken did raise an exception, then proceed with device discovery
                rc = self.processConfigDone()

            except ValueError as err:
                LOGGER.warning('Access token is not yet available. Please authenticate.')
                polyglot.Notices['auth'] = 'Please initiate authentication using the Authenticate Buttion'
                return False
        with self.configDone:
            self.configDoneAlready = True
            self.configDone.notifyAll()
        return rc

    def __customNSHandler(self, key, data):
        if key == 'oauth':
            # This provides the oAuth config (key='oauth') and saved oAuth tokens (key='oauthTokens))
            if not self.oauthService:
                return 
            try:
                self.oauthService.customNsHandler(key, data)
            except Exception as ex:
                LOGGER.error(ex)
        else:
            self.customParamHandler(key, data)

    def __oauthHandler(self, token):
        if not self.oauthService:
            return 
        # This provides the oAuth config (key='oauth') and saved oAuth tokens (key='oauthTokens))
        try:
            self.oauthService.oauthHandler(token)
        except Exception as ex:
            LOGGER.error(ex)


    def __updateStatus(self, value, force: bool):
        return self.setDriver("ST", value, 2, force)

    def __getStatus(self):
        return self.getDriver("ST")

    def __query(self, command):
        nodes = self.poly.getNodes()
        if nodes is None or len(nodes) == 0:
            return True
        for n in nodes:
            node = nodes[n]
            if node is None:
                continue
            else:
                node.query()

    #######################
    ###### NOTICES ########
    #######################
    def clearNotices(self):
        """
        Call this method to remove the blue ribbon that requests the attention of the user
        """
        self.poly.Notices.clear()

    def setNotices(self, key:str, notice:str) :
        """
        Call this method to add a blue ribbon with notice for the customer to take action
        This is a dictionary. So, you would need to provide the key (i.e. the parameter's name)
        And a string that will be displayed in the ribbon
        """
        if key == None or notice == None:
            LOGGER.error("setNotices requires both the key and the notice.")
            return
        self.poly.Notices[key]=notice

    #####################
    ###### NODES ########
    #####################

    def getNode(self, address:str):
        """
        Call this method to get a node and then call its methods for updating
        their state in IoX. Take a look at the class that implements this node
        it's always a good idea to use isinstance to make sure you are dealing 
        with the correct node.
        The address is the address of the node.
        """
        return self.controller.poly.getNode(address)

    
    def addNode(self, address:str, nodeDefId:str, name:str, parent:str=None):
        """
        "Call this method to create dynamic node. The parent will always be the controller 
        "for this node
        """
        if address == None or nodeDefId == None:
            LOGGER.error("need address and nodeDefId ...")
            return False

        if parent == None:
            parent = address  

        nodeInfo={}
        nodeInfo['primaryNode']=parent
        nodeInfo['address']=address
        nodeInfo['name']=name
        nodeInfo['nodeDefId']=nodeDefId
        return self.__addNodeFromConfig(nodeInfo)

    #####################
    ###### OAUTH ########
    #####################

    def callOAuthApi(self, method='GET', url=None, params=None, body=None)->bool:
        """
        Use this method to call an OAUTH protected URL
        """
        if not self.oauthService:
            return False
        return self.oauthService(method, url, params, body)

    
    #############################
    ###### CUSTOM PARAMS ########
    #############################
    def createCustomParam(self, key):
        """
        Creates a user defined/custom parameter for key/value pairs of your own and stores in the 
        database. Whenever a key is updated the customParamHandler (below) is called with the 
        key and its updated value. example:
        myKey = self.createCustomParam('myKey')
        self.updateCustomParam(myKey, "my value" )
        """ 
        try:
            return Custom(self.controller.poly, key)
        except Exception as ex:
            LOGGER.error(f'create custom param failed ...')
            return None

    def updateCustomParam(self, key:Custom, value:str):
        """
        Updates a user defined param. Whenever this method is called, customParamHandler is called
        with the updated values.
        """
        try:
            key = value
        except Exception as ex:
            LOGGER.error(f'failed updating custom param ...' )


    ###
    # This is a list of commands that were defined in the nodedef
    ###
    commands = {'discover': discover, 'x_query': __query}

    ######## DO NOT MODIFY THIS LINE#########
    ###
    ###Nothing below this line is updated####
    ###
    
    #############################
    ###### START|STOP ###########
    #############################
    ####

    def start(self)->bool:
        """
        MANDATORY if and only if you have commands
        This method is called at start so that you can do whatever initialization
        you need. If you return false, the status of the controller node shows 
        disconnected. So, make sure you return the correct status.
        """
        try:
            return True
        except Exception as ex:
            LOGGER.error(f'start failed .... ')
            LOGGER.error(str(ex))
            return False

    def stop(self)->bool:
        """
        This method is called at stop so that you can do whatever cleaning up 
        that's necessary. The result is not checked so make sure everything is 
        cleaned up
        """
        try:
            return True
        except Exception as ex:
            LOGGER.error(f'stop failed .... ')
            return False


    #############################
    ###### PARAMS ###############
    #############################

    def parameterHandler(self, params:Custom)->bool:
        """
        This method is called with the custom parameters provided by the user.
        It is a dictionary so you get the parameter name/key and the value. e.g.
        params['path']
        """
        try:
            return True
        except Exception as ex:
            LOGGER.error(f'process param failed .... ')
            return False

    def customParamHandler(self, key, value):
        """
        This method is called when a custom value (key/value) pair that's stored in the 
        database is changed. You can use this method to manage custom parameters of your own
        in the database.
        """
        try:
            return True
        except Exception as ex:
            LOGGER.error(f'process custom param failed .... ')
            return False

    def customDataHandler(self, data):
        """
        Rarely used.
        """
        try:
            return True
        except Exception as ex:
            LOGGER.error(ex)
    
    #####################
    ###### NODES ########
    #####################

    def getNodeAddress(self, nodedef_id):
        """
        This method is called every time a node is added so that you can map it to 
        anything else you want. 
        """
        try:
            #do any mapping you wish. 
            return nodedef_id
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    def addNodeDone(self, node)->bool:
        """
        " This method is called when adding a node to the system is completed successfully. Make sure you use isinstance
        " to ensure it's your node and then do any additional processing necessary.
        " oauth
        """
        try:
            ###You can store your nodes in a dictionary for mapping or otherwise such as
            #if node == None:
            #   return False
            #self.nodes[node.address] = node
            ###
            return True
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False


    def nodeRemoved(self, node)->bool:
        """
        This method is called when a new node as been removed from the system
        """
        try:
            ###if you stored your nodes a dictionary, delete them 
            #if node == None:
            #   return False
            #del self.nodes[node.address]
            ###
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    

    #####################
    ###### POLL #########
    #####################

    def shortPoll(self)->bool:
        """
        This method is called at every short poll interval. The result is not checked
        """
        try:
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    def longPoll(self)->bool:
        """
        This method is called at every long poll interval. The result is not checked
        """
        try:
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False


    ##########################
    ###### FILE UPLOAD #######
    ##########################

    def filesUploaded(self, path:str)->bool:
        """
        This method is called when files are uplaoded. The path is the directory to which you can find the files
        Do whatever you need with the files because they will be removed once you are done.
        """
        try:
            pass
            ###copy files to your desired directory, something like this:
            #file_path = os.path.join(path, filename)
            #if os.path.isfile(file_path):
            #    dest_path = os.path.join('./', filename)
            #    shutil.copy(file_path, dest_path)
            ###
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    ##########################
    ###### CONFIG ############
    ##########################

    def processConfig(self, config):
        """
        This method is called upon start and gives you all the configuration parameters
        used to initialize this plugin including the store, version, etc.
        """
        try:
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    def processConfigDone(self)->bool:
        """
        This method is called with the configuration is done. This is rarely used as its main function is to facilitate 
        """
        try:
            return True
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    #############################
    ###### DISCOVERY ############
    #############################

    def discover(self)->bool:
        """
        This method is called by IoX to discover  
        nodes/devices or service
        """
        try:
            return True
        except Exception as ex:
            LOGGER.error(f'discover failed .... ')
            return False

    def searchForDevicesUsingMDNS(self, type:str, subtypes:str, protocol:str):
        """
        You can search the network using mDNS. To do so, call this method
        type : string = is the type of device you are looking for. If None, then everything
        subtypes : string = is a list of subtypes [string] you are looking for. If None, then everything
        protocol : string = either udp or tcp. If None, then everything
        If any results, processMDNSResults method will be called with a list of devices and their info
        """
        self.poly.bonjour(type, subtypes, protocol)

    def processMDNSResults(self, results:[]):
        """
        If search using mDNS is successful, this method is called with an array of devices. 
        """
        try:
            # Fill out this method based on the results
            return
        except Exception as ex:
            LOGGER.error(str(ex))
'''
