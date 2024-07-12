###
# Installs in local store
###

from .log import LOGGER
from .plugin import Plugin
from .plugin_meta import PluginMetaData
import requests
import urllib.parse


DEVELOPER_TOKEN_URL_BASE="https://pg3store.isy.io/v2/developer?developer="
LOCAL_STORE_URL="https://localhost:3000/v1/insert"


class StoreEntry:

    def __init__(self, plugin: Plugin ):
        if plugin == None:
            raise ValueError("need the plugin")

        self.meta = plugin.meta


    def getDevelperToken(self, emailAddress:str):

        try:
            if emailAddress == None:
                LOGGER.error("need an a verified/vetted developer email address")
                return False

            url = f"{DEVELOPER_TOKEN_URL_BASE}{emailAddress}"

            response = requests.get(url)

            if response.status_code != 200:
                LOGGER.error(f"failed getting a token for {self.meta.getPublisher()}, status = {response.status_code}")
                return False

            content = response.json()

            self.token = content ["token"]
            return True 

        except Exception as ex:
            LOGGER.critical("excetpion in getting developer token ...")
            raise 

    def addToStore(self, developerEmail, developerUser, pluginPath):
        '''
            email address to get the token
            developerUser is the local user name on the development machine
            pluginPath is the path to the local plugin directory
        '''
        if developerEmail == None or developerUser == None or pluginPath == None:
            LOGGER.error("need develper email and local user")
            return False
        if not self.getDevelperToken(developerEmail):
            return False
        if not self.meta:
            return False
        
        plugin_meta = self.meta.getStoreEntryContent()
        if plugin_meta == None:
            return False
        plugin_meta['developer']=developerEmail
        plugin_meta['devMode']=True
        plugin_meta['devPath']=pluginPath
        plugin_meta['devUser']=developerUser
        plugin_meta['store']='Local'
        plugin_meta['from_store']='Local'
        plugin_meta['prem']=True
        plugin_meta['purchaseOpetions']=[]
        plugin_meta['token']=self.token

        post_content:str = urllib.parse.urlencode(plugin_meta)
        post_content=post_content.replace("=True","=true")
        post_content=post_content.replace("=False","=false")

        headers = {
            "Content-Type":"application/x-www-form-urlencoded", 
        } 

        response = requests.post(LOCAL_STORE_URL, headers=headers, data=post_content, verify=False)
        if response.status_code != 200:
            LOGGER.error(f"failed creating store entry (status={response.status_code}): {response.text}")
            return False
        return True

def add_plugin():
    project_path = "/usr/home/admin/ioxplugin/tests"
    json_file = f"{project_path}/dimmer.iox_plugin.json"
    email = "n/a"
    devUser = "n/a"
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
        plugin=Plugin(json_file, project_path)
        store=StoreEntry(plugin)
        store.addToStore(email, devUser, project_path)
    except Exception as ex:
        LOGGER.error("Failed creating store entry ..", exc_info=True)


if __name__ == "__main__":
    add_plugin()
