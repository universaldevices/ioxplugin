
#!/usr/bin/env python3

"""
Manage profiles (editor, nls, and nodedef)
Copyright (C) 2024 Universal Devices
"""
from .log import LOGGER
import os

NLS_PATH="nls"
EDITOR_PATH="editor"
NODEDEF_PATH="nodedef"

NLS_FILE="en_us.txt"
EDITOR_FILE="editor.xml"
NODEDEF_FILE="nodedef.xml"

class ProfileWriter:

    def __init__(self, is_new:bool=True, path="./profile"):
        try:
            self.path = f"{path}/profile" if path != "./profile" else path
            self.nls_path=f"{self.path}/{NLS_PATH}"
            self.editor_path=f"{self.path}/{EDITOR_PATH}"
            self.nodedef_path=f"{self.path}/{NODEDEF_PATH}"
            self.nls_file=f"{self.nls_path}/{NLS_FILE}"
            self.editor_file=f"{self.editor_path}/{EDITOR_FILE}"
            self.nodedef_file=f"{self.nodedef_path}/{NODEDEF_FILE}"

            self.__preferfs(is_new)  

        except Exception as ex:
            LOGGER.critical(str(ex))

    def __preferfs(self, is_new:bool):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        
        if not os.path.exists(self.nls_path):
            os.makedirs(self.nls_path)
        elif is_new:
            os.remove(self.nls_file)

        if not os.path.exists(self.editor_path):
            os.makedirs(self.editor_path)
        elif is_new:
            os.remove(self.editor_file)

        if not os.path.exists(self.nodedef_path):
            os.makedirs(self.nodedef_path)
        elif is_new:
            os.remove(self.nodedef_file)

    def writeToNLS(self,nls:str)->bool:
        try:
            with open(self.nls_file, 'a') as file:
                file.write(nls)
            return True
        except Exception as ex:
            LOGGER.critical(str(ex))
            return False 

    def writeToEditor(self,editor:str)->bool:
        try:
            with open(self.editor_file, 'a') as file:
                file.write(editor)
            return True
        except Exception as ex:
            LOGGER.critical(str(ex))
            return False 

    def writeToNodeDef(self,nodedef:str)->bool:
        try:
            with open(self.nodedef_file, 'a') as file:
                file.write(nodedef)
            return True
        except Exception as ex:
            LOGGER.critical(str(ex))
            return False 
