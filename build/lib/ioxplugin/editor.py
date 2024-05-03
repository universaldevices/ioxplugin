#!/usr/bin/env python3

"""
Plugin schema processor and validator
Copyright (C) 2024 Universal Devices
"""

import json
import os
from .log import LOGGER
from .validator import validate_id

class EditorDetails:

    def __init__(self, editor):
        self.id=None
        self.uom=None
        self.min=None
        self.max=None
        self.step=None
        self.precision=None
        self.subset=None
        self.index_names=[]
        self.idref=None
        if editor == None:
            LOGGER.critical("no editor given for EditorDetails ...")
            raise
        try:
            if 'idref' in editor:
                self.idref = editor['idref']
                self.id = None
            else:
                self.id=editor['id']
                val = editor['uom'] 
                parsed_list = [item.strip() for item in val.split('|')]
                self.uom=int(parsed_list[1])

                if 'subset' in editor:
                    self.subset = editor ['subset']
                else:
                    if 'min' in editor:
                        self.min = editor['min']
                    if 'max' in editor:
                        self.max = editor['max']
                    if 'step' in editor:
                        self.step = editor['step']
                    if 'precision' in editor:
                        self.precision = editor['precision']
                if 'index_names' in editor:
                    self.index_names = editor['index_names']
        except Exception as ex:
            LOGGER.critical(str(ex))
            raise


    #returns editors + nls  
    def toIoX(self)->(str, str):
        if self.id == None:
            LOGGER.warn("editor without an id ... ")
            return None, None
        nls = ""
        editor = f"<editor id=\"{self.id}\">\n<range uom=\"{self.uom}\" "
        if self.isSubset():
            editor += (f"subset=\"{self.subset}\"")
        else:
            if self.min == None or self.max == None:
                LOGGER.warn(f"Missing min/max for editor id {self.id}")
                return None, None
            editor += (f"min=\"{self.min}\" max=\"{self.max}\"")
            if self.precision != None:
                editor += (f" prec=\"{self.precision}\"")
            if self.step != None:
                editor += (f" step=\"{self.step}\"")
            if len(self.index_names) > 0 :
                editor += (f" nls=\"NLSIX_{self.id}\"")
                for i in range(len(self.index_names)):
                    val = self.index_names[i] 
                    parsed_list = [item.strip() for item in val.split('|')]
                    nls += f"\nNLSIX_{self.id}-{parsed_list[1]} = {parsed_list[0]}"

        editor += ("/>\n</editor>\n")
        return editor, nls

    def validate(self):
        return validate_id(self.getEditorId())

    def isSubset(self):
        return self.subset != None

    def isRef(self):
        return self.idref != None

    def getEditorId(self):
        return self.idref if self.isRef() else self.id

__allEditors = None

class Editors:
    def __init__(self):
        global __allEditors
        self.editors = {}
        self.refs = [] #references
        __allEditors=self
        
    def addEditors(self, editors):
        if editors == None:
            return
        try:
            for editor in editors:
                self.addEditor(editor)
        except Exception as ex:
            raise

    def addEditor(self, editor)->EditorDetails:
        if editor == None:
            LOGGER.warn("no editors given to be added ...")
            return None
        try:
            ed=EditorDetails(editor)
            if (ed.id == None or ed.id == '') and not ed.idref:
                LOGGER.warn("the editor is missing id ... ignoring")
                return None
            if ed.isRef() :
                self.refs.append(ed.idref)
            else:
                self.editors[ed.id]=ed
            return ed
        except Exception as ex:
            raise
            return None

    #returns editor + nls
    def toIoX(self)->(str,str):
        try:
            editors = "<editors>" 
            nls = ""
            for ed in self.editors:
                editor = self.editors[ed]
                edx,nlsx=editor.toIoX()
                if edx:
                    editors += edx
                if nlsx:
                    nls += nlsx
            editors += ("</editors>")
            return editors, nls
        except Exception as ex:
            LOGGER.critical(str(ex))
            raise

    def validate(self):
        try:
            rc = True
            #warn if a ref does not exist
            for idref in self.refs:
                if idref not in self.editors:
                    LOGGER.critical(f"no editor with id of \"{idref}\" exists, so it cannot be referenced ... ")
                    rc = False

            for e in self.editors:
                if not self.editors[e].validate():
                    rc = False
            return rc
        except Exception as ex:
            LOGGER.critical(str(ex))
            return False
            
    @staticmethod
    def getEditors():
        global __allEditors
        if __allEditors == None:
            return None
        return __allEditors
