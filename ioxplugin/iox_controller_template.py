CONTROLLER_TEMPLATE_HEADER='''
import udi_interface, os, sys, json, time
LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom
'''

#
#from ModbusDeviceNode import ModbusDeviceNode
#class ModbusControllerNode(udi_interface.Node):
#   id = 'modbuscontroll'
#    """This is a list of properties that were defined in the nodedef"""
#    drivers = [{'driver': 'ST', 'value': 0, 'uom': 2, 'name': 'Status'}]
#    children = [{'node_class': 'ModbusDeviceNode', 'id': 'modbus', 'name':
#        'ModbusDevice', 'parent': 'modbuscontroll'}]

#    def __init__(self, polyglot, protocolHandler, controller=
#        'modbuscontroll', address='modbuscontroll', name='Modbus Controller'):
#        super().__init__(polyglot, controller, address, name)
#        self.protocolHandler = protocolHandler
#        self.Parameters = Custom(polyglot, 'customparams')
#        self.valid_configuration = False
#        self.started = False
#        self.poly.subscribe(polyglot.START, self.start)
#        self.poly.subscribe(polyglot.CUSTOMPARAMS, self.parameter_handler)
#        self.poly.subscribe(polyglot.POLL, self.poll)
#        self.poly.subscribe(polyglot.STOP, self.stop)
#        self.poly.subscribe(polyglot.CONFIG, self.config)

CONTROLLER_TEMPLATE_BODY='''

    def setProtocolHandler(self, protocolHandler):
        self.protocolHandler = protocolHandler

    def parameter_handler(self, params):
        self.Parameters.load(params)
        return self.protocolHandler.processParams(self.Parameters)

    def config(self, param):
        try:
            if os.path.exists(DATA_PATH):
                self.protocolHandler.filesUploaded(DATA_PATH)
                shutil.rmtree(DATA_PATH)
                return
        except Exception as ex:
            LOGGER.warn(str(ex))

        self.protocolHandler.configChanged(param)
        return True

    def start(self):
        LOGGER.info(f'Starting... ')
        self.poly.addNode(self)
        self.addAllNodes()
        self.poly.updateProfile()
        self.poly.setCustomParamsDoc()
        self.updateStatus(1 if self.protocolHandler.start() else 0)
        self.poly.ready()
        return True

    def stop(self):
        LOGGER.info(f'Stopping ... ')
        self.protocolHandler.stop()
        self.updateStatus(0)
        return True

    def poll(self, polltype):
        if 'shortPoll' in polltype:
            self.protocolHandler.shortPoll()
        elif 'longPoll' in polltype:
            self.protocolHandler.longPoll()

    def addAllNodes(self):
        config = self.poly.getConfig()
        if config is None or config['nodes'] is None or len(config['nodes']
            ) <= 0:
            config = {}
            config['nodes'] = []
            for child in self.children:
                config['nodes'].append({'nodeDefId': child['id'], 'address':
                    child['node_class'], 'name': child['name'],
                    'primaryNode': child['parent']})
        for node in config['nodes']:
            if not self.__addNode(node):
                return
        LOGGER.info(f'Done adding nodes ...')
        self.valid_configuration = True

    def __addNode(self, node_info) ->bool:
        if node_info is None:
            LOGGER.error('node cannot be null')
            return False
        try:
            cls = globals()[node_info['address']]
            node = cls(self.poly, node_info['primaryNode'], node_info[
                'nodeDefId'], node_info['name'])
            if node is None:
                LOGGER.error(f'invalid noddef id ...')
                return False
            else:
                node_r = self.poly.addNode(node)
                if node_r:
                    node_r.setProtocolHandler(self.protocolHandler)
                    self.protocolHandler.nodeAdded(node_r)
                    return True
                LOGGER.error("failed adding node ... ") 
                return False
        except Exception as ex:
            LOGGER.error(str(ex))
            return False

    def updateStatus(self, value, force: bool):
        return self.setDriver("ST", value, 2, force)

    def getStatus(self):
        return self.getDriver("ST")

    def Discover(self, command):
        return self.protocolHandler.discover()

    def Query(self, command):
        nodes = self.poly.getNodes()
        if nodes is None or len(nodes) == 0:
            return True
        for n in nodes:
            node = nodes[n]
            if node is None:
                continue
            else:
                node.queryAll()

    ###
    # This is a list of commands that were defined in the nodedef
    ###
    commands = {'discover': Discover, 'query': Query}
'''
