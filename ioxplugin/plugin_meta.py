#!/usr/bin/env python3

"""
Class for handling plugin metadata 
Copyright (C) 2024 Universal Devices
"""

from .log import LOGGER
import os

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

    def getAuthor(self):
        try:
            return self.metadata['author']
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

    def geLicenseLink(self):
        try:
            return self.metadata['licenseLink']
        except Exception as ex:
            LOGGER.critical(str(ex))
            return None

    def geeShortPoll(self):
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
            return None

    def getEnableDiscovery(self):
        try:
            return self.metadata['enableDiscovery']
        except Exception as ex:
            LOGGER.critical(str(ex))
            return None

    def getEnableOAUTH2(self):
        try:
            return self.metadata['enableOAUTH2']
        except Exception as ex:
            LOGGER.critical(str(ex))
            return None

    def getWorksOnPolisy(self):
        try:
            return self.metadata['worksOnPolisy']
        except Exception as ex:
            LOGGER.critical(str(ex))
            return None

    def getWorksOnEisy(self):
        try:
            return self.metadata['worksOnEisy']
        except Exception as ex:
            LOGGER.critical(str(ex))
            return None

    def getRequiresIoXAccess(self):
        try:
            return self.metadata['requiresIoXAccess']
        except Exception as ex:
            LOGGER.critical(str(ex))
            return None

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

    def getPythonPHClassName(self):
        name= f'{self.getName()}ProtocolHandler'.replace(' ','').replace('_','')
        return name[0].upper()+name[1:]

    def getPythonPHFileName(self):
        return f'{self.getPythonPHClassName()}.py'