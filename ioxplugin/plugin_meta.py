#!/usr/bin/env python3

"""
Class for handling plugin metadata 
Copyright (C) 2024 Universal Devices
"""

from log import LOGGER

class PluginMetaData:

    def __init__(self, metadata):
        self.metadata=metadata

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
        try:
            return self.metadata['requirements']
        except Exception as ex:
            LOGGER.critical(str(ex))
            return None
