#Universal Devices
#MIT License
import logging
import os
from typing import Literal
import traceback

# Create a logger instance
PLUGIN_LOGGER = logging.getLogger('iox_p_logger')
PLUGIN_LOGGER.setLevel(logging.DEBUG)
logging_inited = False

def init_ext_logging(path:str):
    global logging_inited
    global PLUGIN_LOGGER
    if logging_inited:
        return
    if path == None:
        raise Exception ("need the path for logger to create the log file ...")
    logging_inited = True

    # Create a file handler to write logs to a file
    file_handler = logging.FileHandler(os.path.join(path, 'iox_plugin_ext.log'))
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    # Create a stream handler to output logs to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    # Add the file handler and stream handler to the logger
    PLUGIN_LOGGER.addHandler(file_handler)
    PLUGIN_LOGGER.addHandler(console_handler)

def ioxp_log(level:Literal['debug', 'info', 'warning', 'error', 'critical'], message:str, traceback:bool=False):
    if message == None:
        return
    try:
        method = getattr(PLUGIN_LOGGER, level)
        if method == None:
            return
        method(message, exc_info=traceback)
    except Exception as ex:
        PLUGIN_LOGGER.exception("Critical Exception ...")

def p_log_debug(message:str):
    ioxp_log('debug', message)

def p_log_info(message:str):
    ioxp_log('info', message)

def p_log_warning(message:str):
    ioxp_log('warning', message)

def p_log_error(message:str, traceback:bool=False):
    ioxp_log('warning', message, traceback)

def p_log_critical(message:str, traceback:bool=True): ioxp_log('critical', message, traceback)

class IoXPluginLoggedException():

    '''
        Use this class to log exceptions including traceback
        log + level + include traceback.
        level can only be debug, info, warning, error, criticalsuper.__init__(message)
    '''
    def __init__(self, level:Literal['debug', 'info', 'warning', 'error', 'critical'], message:str, traceback:bool=True):
        ioxp_log(level, message, traceback)
