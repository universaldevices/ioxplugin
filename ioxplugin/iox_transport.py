
#!/usr/bin/env python3

"""
Configuration parameters for transport
Copyright (C) 2024 Universal Devices
"""
from .log import LOGGER

class IoXTCPTransport():
    def __init__(self, comm_params):
        if comm_params == None:
            raise Exception ("Need communication parameters for TCP (host/port)")
        self.name = "TCP"
        self.host = None
        self.port = None
        self.timeout = None
        self.keepAlive = None
        try:
            if 'host' in comm_params:
                self.host = comm_params['host'] 
            if 'port' in comm_params:
                self.port = comm_params['port']
            if 'timeout' in comm_params:
                self.timeout = comm_params['timeout']
            if 'keepAlive' in comm_params:
                self.timeout = comm_params['keepAlive']

            if host == None or port == None:
                raise Exception ("Both host and ports are mandatory for connection ...")

        except Exception as ex:
            raise

    def connect(self)->bool:
        #make a connection and return 
        pass

class IoXSerialTransport():
    def __init__(self, comm_params):
        if comm_params == None:
            raise Exception ("Need communication parameters for serial (port/baudrate)")

        self.name = "Serial"
        self.port = None
        self.baudrate = 115200
        self.timeout=1
        self.databits=serial.EIGHTBITS
        self.parity=serial.PARITY_NONE 
        self.stopbits=serial.STOPBITS_ONE
        self.flowcontrol=None

        try:
            if 'port' in comm_params:
                self.port = comm_params['port']
            if 'baudrate' in comm_params:
                self.baudrate = comm_params['baudrate'] 
            if 'timeout' in comm_params:
                self.baudrate = comm_params['timeout'] 
            if 'databits' in comm_params:
                self.databits = comm_params['databits'] 
            if 'parity' in comm_params:
                self.baudrate = comm_params['parity'] 
            if 'stopbits' in comm_params:
                self.baudrate = comm_params['stopbits'] 
            if 'flowcontrol' in comm_params:
                self.flowcontrol = comm_params['flowcontrol'] 

            if port == None:
                raise Exception ("Need port such as ttyU0 ...")

        except Exception as ex:
            raise

    def connect(self)->bool:
        #make a connection and return 
        pass

class IoXTransport:
    def __init__(self, transport_params):
        if transport_params == None:
            raise Exception ("Need communication parameters for TCP (host/port)")

        if not transport_params['mode']:
            raise Exception ("Missing communication mode")

        self.is_connected=False
        self.params=transport_params
        self.mode=self.params['mode']

    def getMode(self):
        return self.mode

    def getTransport(self):

        if self.mode == 'Serial':
            return IoXSerialTransport(self.params)

        if self.mode == 'TCP':
            return IoXTCPTransport(self.params)

        return None

