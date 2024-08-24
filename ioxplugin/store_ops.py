###
# Adds an entry in  the local store
###

from ioxplugin import PLUGIN_LOGGER, IoXPluginLoggedException, Plugin, PluginMetaData, init_ext_logging
import requests
import urllib.parse
import argparse, os
from typing import Literal
import random
import json
import threading
import ssl
from paho.mqtt import client as mqtt_client


BROKER = 'localhost'
WS_PORT = 8881
PG_PORT = 3000
AUTH_URL = f"https://{BROKER}:{PG_PORT}/auth"

TOPIC_BASE = "udi/pg3/frontend/ns"

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60
FLAG_EXIT = False


DEVELOPER_TOKEN_URL_BASE="https://pg3store.isy.io/v2/developer?developer="
LOCAL_STORE_URL="https://localhost:3000/v1"
LOCAL_STORE_URL_INSERT=f"{LOCAL_STORE_URL}/insert"
STORE_URL_LIST=f"{LOCAL_STORE_URL}/list?store="
STORE_ENTRY_FILE='store_entry.json'

class PG3Settings:

    def __init__(self, user, settings):
        self.user=user
        self.settings=settings

    def getId(self):
        return self.user['id']
        
    def getName(self):
        return self.user['name']

    def getPassword(self):
        return self.user['password']

    def getPassword(self):
        return self.user['password']

    def getTopic(self):
        return f"{TOPIC_BASE}/{self.getName()}"

    def getUuid(self):
        return self.settings['macAddress']

    def getClientId(self):
        # generate client ID with pub prefix randomly
        return f'ioxplugin-wss-sub-{self.getName()}-{random.randint(0, 1000)}'

class PG3WebsocketConnection:

    def __init__(self):
        self.tc=None

    def publish(self, topic:str, msg:str):
        if not self.client.is_connected():
            PLUGIN_LOGGER.error("cannot publish because we are not connected ...")
            return False

        self.client.publish(topic, msg)

    def connect(self, username:str, password: str):
        if not self._authenticate(username, password):
            return False
        try:
            self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, self.settings.getClientId(), transport='websockets')
            #self.client.tls_set(certfile=self.ssl.getClientCert(), keyfile=self.ssl.getClientPrivate())
            self.client.tls_set(ca_certs='/usr/local/etc/ssl/certs/ud.ca.cert', cert_reqs=ssl.VerifyMode.CERT_NONE)
            self.client.username_pw_set(self.settings.getName(), self.settings.getPassword())
            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            self.client.on_disconnect = self._on_disconnect
            self.client.connect(BROKER, WS_PORT, keepalive=120)
            self.tc = threading.Thread(target=self._run, name="ws-thread")
            self.tc.start()
            return True
        except Exception as ex:
            IoXPluginLoggedException("connect failed", True)
            return False

    def await_completion(self):
        self.tc.join()

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0 and client.is_connected():
            PLUGIN_LOGGER.debug(f"Connected to MQTT Broker, subscribing to: ${self.settings.getTopic()}")
            client.subscribe(self.settings.getTopic())
        else:
            PLUGIN_LOGGER.error(f'Failed to connect, return code {rc}')


    def _on_disconnect(self, client, userdata, rc):
        PLUGIN_LOGGER.info(f'Disconnected from mqtt with result code:{rc}')
        reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
        while reconnect_count < MAX_RECONNECT_COUNT:
            PLUGIN_LOGGER.debug(f"Reconnecting in {reconnect_delay} seconds...")
            time.sleep(reconnect_delay)

            try:
                client.reconnect()
                PLUGIN_LOGGER.info("Reconnected successfully!")
                return
            except Exception as err:
                PLUGIN_LOGGER.error("%s. Reconnect failed. Retrying...", err)

            reconnect_delay *= RECONNECT_RATE
            reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
            reconnect_count += 1
        PLUGIN_LOGGER.info(f"Reconnect failed after {reconnect_count} attempts. Exiting...")
        global FLAG_EXIT
        FLAG_EXIT = True

    def _on_message(self, client, userdata, msg):
        PLUGIN_LOGGER.debug(f'Received `{msg.payload.decode()}` from `{msg.topic}` topic')

    def _run(self):
        try:
            self.client.loop_forever()
        except Exception as ex:
            IoXPluginLoggedException(ex)

class PluginStoreOps:

    def __init__(self, store:Literal['Local', 'Production', 'Beta']):
        self.store=store
        self.settings:PG3Settings=None
        self.plugins=[]

    '''
        gets an array of all the plugins for this store
    '''
    def _getPlugins(self):
        try:
            url=f"{STORE_URL_LIST}{self.store}"    
            response = requests.get(url,verify=False)
            if response.status_code != 200:
                PLUGIN_LOGGER.error(f"failed getting {self.store} store list, status = {response.status_code}")
                return None

            contents = response.json()
            self.plugins = []

            for plugin in contents:
                self.plugins.append(PluginMetaData(plugin))
            return self.plugins
        except Exception as ex:
            IoXPluginLoggedException()
            return None

    def findByName(self, name:str)->PluginMetaData:
        '''
            find a plugin by name. If one is found, return it
            otherwise, return None
        '''
        if self.plugins == None or len(self.plugins) == 0:
            return None

        for plugin in self.plugins:
            if plugin.getName() == name:
                return plugin

        return None

    def findByUuid(self, uuid:str)->PluginMetaData:
        '''
            find a plugin by uuid. If one is found, return it
            otherwise, return None
        '''
        if self.plugins == None or len(self.plugins) == 0:
            return None

        for plugin in self.plugins:
            if plugin.getUuid() == uuid:
                return plugin

        return None


    def addToStore(self, jsonFile:str, developerEmail:str, developerUser:str, pluginPath:str):
        '''
            json = the definition 
            email address to get the token
            developerUser is the local user name on the development machine
            pluginPath is the path to the local plugin directory
            returns a PluginMetaData object in case of success, None otherwise
        ''' 
        store_entry_file_path = os.path.join(pluginPath, STORE_ENTRY_FILE) 
        if os.path.exists(store_entry_file_path):
            PLUGIN_LOGGER.error(f"store entry already exists for this project {store_entry_file_path}. If you want to start fresh, remove this file")
            return None
        try:
            meta=Plugin(jsonFile, pluginPath).meta

            token = self._getDevelperToken(developerEmail)
            if token == None :
                return None

            if self.findByName(meta.getName()):
                PLUGIN_LOGGER.error(f"A plugin with the same name already in store: {meta.getName()}")
                return None
            
            plugin_meta = meta.getStoreEntryContent()
            if plugin_meta == None:
                return None
            plugin_meta['developer']=developerEmail
            plugin_meta['devMode']=True
            plugin_meta['devPath']=pluginPath
            plugin_meta['devUser']=developerUser
            plugin_meta['store']='Local'
            plugin_meta['from_store']='Local'
            plugin_meta['prem']=True
            plugin_meta['purchaseOpetions']=[]
            plugin_meta['token']=token

            post_content:str = urllib.parse.urlencode(plugin_meta)
            post_content=post_content.replace("=True","=true")
            post_content=post_content.replace("=False","=false")

            headers = {
                "Content-Type":"application/x-www-form-urlencoded", 
            } 

            response = requests.post(LOCAL_STORE_URL_INSERT, headers=headers, data=post_content, verify=False)
            if response.status_code != 200:
                PLUGIN_LOGGER.error(f"failed creating store entry (status={response.status_code}): {response.text}")
                return None

            #refresh
            self._getPlugins()

            new_plugin=self.findByUuid(plugin_meta['uuid'])
            if new_plugin:
                new_plugin.save(store_entry_file_path)
            return new_plugin
        except Exception as ex:
            IoXPluginLoggedException()
            return None

    def installPlugin(self, username, password):
        '''
            @username = pg3 username
            @password = pg3 password
            installs the plugin in the next available slot.
            it uses the last store_entry.json for installation.
            It checks the store_entry.json file to make sure this 
            plugin was not installed before ['slot'] and ['installed']. 
            If it was already installed, it will return -1.
        '''
        store_entry_file_path = os.path.join(pluginPath, STORE_ENTRY_FILE) 
        if not os.path.exists(store_entry_file_path):
            PLUGIN_LOGGER.error(f"store entry does not exists for this project {store_entry_file_path}. First, you need to add the plugin to the store")
            return -1

        if not self._authenticate(username, password):
            PLUGIN_LOGGER.error(f"failed authenticating {username}")
            return -1

        try:
            store_entry=json.load(store_entry_file_path)
            meta=PluginMetaData(store_entry)

            if meta.getInstalledSlot() != -1:
                PLUGIN_LOGGER.error(f"{store_entry['name']} is already installed ")
                return -1

            slot = self._getNextFreeSlot()
            if slot <= 0:
                PLUGIN_LOGGER.error("no more free slots to install the plugin ....")
                return -1
    
            PLUGIN_LOGGER.info(f"trying to install in slot {slot} ...")

            installPayload={
                "installNs":
                {
                    "nsid": meta.getUuid(),
                    "thestore":self.store,
                    "name": meta.getName(),
                    "option":"",
                    "edition":"Free",
                    "uuid":self.settings.getUuid(),
                    "profileNum":slot,
                    "nolicense":0
                }
            }

        except Exception as ex:
            IoXPluginLoggedException()
            return -1

    def _authenticate(self, username:str, password: str):

        headers={
            'Content-Type': 'application/json',
            'Accept':'*/*'
        }

        body={
            "username": username,
            "password": password
        }

        response = requests.post(url=AUTH_URL, headers=headers, json=body, verify=False )
        if response.status_code != 200:
            PLUGIN_LOGGER.error(f"failed authenticating with error code = ${response.status_code}")
            return False

        data = response.json()
        if not data['success']:
            PLUGIN_LOGGER.error(f"pg3 returned an error ...") 
            return False

        self.settings=PG3Settings(data['user'], data['settings'])
        return True

    def _getNextFreeSlot(self):
        '''
            Finds the next free slot in which a plugin can be installed
            returns -1 if none (> 100)
        '''
        import re
        # Define the directory path
        directory = '/var/polyglot/pg3/ns'
        # List all files in the directory
        filenames = os.listdir(directory)

        if len(filenames) == 0:
            return 1 #first slot
        slots=[]
        # Print all filenames
        for filename in filenames:
            match = re.search(r'_(\d+)$', filename)
            try:
                slots.append(int(match.group(1)))

            except Exception as ex:
                IoXPluginLoggedException("invalid ns", True)
                return -1

        slot = -1
        for slot in range(1,100):
            if slot in slots:
                continue
            break;

        return slot        


    def _getDevelperToken(self, emailAddress:str):
        try:
            if emailAddress == None:
                PLUGIN_LOGGER.error("need an a verified/vetted developer email address")
                return None

            url = f"{DEVELOPER_TOKEN_URL_BASE}{emailAddress}"

            response = requests.get(url, verify=False )

            if response.status_code != 200:
                PLUGIN_LOGGER.error(f"failed getting a token for {emailAddress}, status = {response.status_code}")
                return None

            content = response.json()

            return content ['token']
        except Exception as ex:
            IoXPluginLoggedException("excetpion in getting developer token ...")
            return None


def add_plugin():
    project_path = "/usr/home/admin/workspace/ioxplugin/tests"
    init_ext_logging(project_path)
    json_file = f"{project_path}/dimmer.iox_plugin.json"
    email = "tech@universal-devices.com"
    devUser = "admin"
    try:
        parser = argparse.ArgumentParser(description="the path IoX Plugin json file")
    
        parser.add_argument('project_path', type=str, help='path to the project directory')
        parser.add_argument('json_file', type=str, help='path to the json file')
        parser.add_argument('email', type=str, help='developer account email address')
        parser.add_argument('devUser', type=str, help='local user on the development machine')
        
        args = parser.parse_args()

        project_path = args.project_path
        json_file = args.json_file
    except SystemExit as ex:
        pass

    try:
        storeOps=PluginStoreOps('Local')
        #plugin=Plugin(json_file, project_path)
        storeOps.addToStore(json_file, email, devUser, project_path)
    except Exception as ex:
        PLUGIN_LOGGER.error("Failed creating store entry ..", exc_info=True)


if __name__ == "__main__":
    add_plugin()
