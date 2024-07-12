#!/usr/bin/env python3

"""
Class for handling plugin metadata 
Copyright (C) 2024 Universal Devices
"""

from .log import LOGGER
import os
import uuid

DEFAULT_REQ_PKGS=["udi_interface>=3.0.57", "ioxplugin"]

class PluginMetaData:

    def __init__(self, metadata):
        self.metadata=metadata
        self.plugin_file = None

    def setPluginFile(self, plugin_file:str):
        self.plugin_file = os.path.basename(plugin_file) 

    def getName(self):
        try:
            return self.metadata['name']
        except Exception as ex:
            LOGGER.critical(str(ex))
            return None

    def getDescription(self):
        try:
            return self.metadata['description']
        except Exception as ex:
            LOGGER.critical(str(ex))
            return None

    def getPublisher(self):
        try:
            return self.metadata['publisher']
        except Exception as ex:
            LOGGER.critical(str(ex))
            return None

    def getLanguage(self):
        try:
            return self.metadata['language']
        except Exception as ex:
            LOGGER.critical(str(ex))
            return None

    def getExecutableName(self):
        try:
            return self.metadata['executableName']
        except Exception as ex:
            LOGGER.critical(str(ex))
            return None

    def getInstallScript(self):
        try:
            return self.metadata['installScript']
        except Exception as ex:
            LOGGER.critical(str(ex))
            return None

    def getDocumentationLink(self):
        try:
            return self.metadata['documentationLink']
        except Exception as ex:
            LOGGER.critical(str(ex))
            return None

    def getLicenseLink(self):
        try:
            return self.metadata['licenseLink']
        except Exception as ex:
            LOGGER.critical(str(ex))
            return None

    def getShortPoll(self):
        try:
            return self.metadata['shortPoll']
        except Exception as ex:
            LOGGER.critical(str(ex))
            return None

    def getLongPoll(self):
        try:
            return self.metadata['longPoll']
        except Exception as ex:
            LOGGER.critical(str(ex))
            return None

    def getProfileVersion(self):
        try:
            return self.metadata['profileVersion']
        except Exception as ex:
            LOGGER.critical(str(ex))
            return None

    def getInitialLogLevel(self):
        try:
            return self.metadata['initialLogLevel']
        except Exception as ex:
            LOGGER.critical(str(ex))
            return "INFO"

    def getStatus(self):
        try:
            return (self.metadata['status']).lower()
        except Exception as ex:
            LOGGER.critical(str(ex))
            return None

    def getEnableFileUpload(self):
        try:
            return bool(self.metadata['enableFileUpload'])
        except Exception as ex:
            LOGGER.critical(str(ex))
            return False

    def getEnableOAUTH2(self):
        try:
            return bool(self.metadata['enableOAUTH2'])
        except Exception as ex:
            LOGGER.critical(str(ex))
            return False

    def getWorksOnPolisy(self):
        try:
            return bool(self.metadata['worksOnPolisy'])
        except Exception as ex:
            LOGGER.critical(str(ex))
            return False

    def getWorksOnEisy(self):
        try:
            return bool(self.metadata['worksOnEisy'])
        except Exception as ex:
            LOGGER.critical(str(ex))
            return False

    def getRequiresIoXAccess(self):
        try:
            return bool(self.metadata['requiresIoXAccess'])
        except Exception as ex:
            LOGGER.critical(str(ex))
            return False

    def getRequirements(self):
        out = DEFAULT_REQ_PKGS
        try:
            return out + self.metadata['requirements']
        except Exception as ex:
            LOGGER.warn(str(ex))
            return out

    def getVersion(self):
        try:
            return f"ud_plugin_version=\"{self.metadata['version']}\""
        except Exception as ex:
            LOGGER.warn(str(ex))
            return "ud_plugin_version=\"1.0.0\""

    def areNodesStatic(self):
        try:
            return self.metadata['nodesAreStatic']
        except Exception as ex:
            return True #default

    def getPythonPHClassName(self):
        name= f'{self.getName()}ProtocolHandler'.replace(' ','').replace('_','')
        return name[0].upper()+name[1:]

    def getPythonPHFileName(self):
        return f'{self.getPythonPHClassName()}.py'

    def getStoreEntryContent(self):
        uuid1 = uuid.uuid4()

        if not self.getName() :
            LOGGER.error("plugin needs a name")
            return None

        if not self.getPublisher() :
            LOGGER.error("plugin needs an author")
            return None

        if not self.getExecutableName():
            LOGGER.error("plugin needs an executable name")
            return None

        install_script = "install.sh"
        if self.getInstallScript():
            install_script = self.getInstallScript()

        profileVersion = "3.0.0"
        if self.getProfileVersion():
            profileVersion = self.getProfileVersion()

        language = "python3"
        slang = self.getLanguage()
        if self.getLanguage() != language:
            LOGGER.warning(f"{self.getLanguage()} is not a valid language ... defaulting to {language}")

        status = "active"
        if self.getStatus():
            status = self.getStatus()

        shortPoll = 300
        if self.getShortPoll():
            shortPoll = self.getShortPoll()

        longPoll = 900
        if self.getLongPoll():
            longPoll = self.getLongPoll()

        desc = "Generated bo IoX Plugin Develper"
        if self.getDescription():
            desc = self.getDescription()
        
        docs =  "https://developer.isy.io"
        if self.getDocumentationLink():
            docs = self.getDocumentationLink()

        lic = "https://developer.isy.io"
        if self.getLicenseLink():
            lic = self.getLicenseLink()

        return {
            "uuid":str(uuid1),
            "name":self.getName(),
            "author":self.getPublisher(),
            "profile_version":profileVersion,
            "language":language,
            "install":install_script,
            "executable":self.getExecutableName(),
            "status":status,
            "shortPoll":shortPoll,
            "logLevel":self.getInitialLogLevel(),
            "authorize":'true' if self.getEnableOAUTH2() else 'false',
            "polisy":'true' if self.getWorksOnPolisy() else 'false',
            "eisy":'true' if self.getWorksOnEisy() else 'false',
            "isyAccess":'true' if self.getRequiresIoXAccess() else 'false',
            "fileUpload":'true' if self.getEnableFileUpload() else 'false', 
            "docs":docs,
            "license":lic,
            "desc":desc
        }



