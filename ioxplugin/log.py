import logging
import os

# Set up the basic configuration for the logger
#logging.basicConfig(level=logging.DEBUG,
#                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a logger instance
LOGGER = logging.getLogger('IoX-Plugin-Ext-Logger')
logging_inited = False

def init_ext_logging(path:str):
    global logging_inited
    if logging_inited:
        return
    if path == None:
        raise Exception ("need the path for logger to create the log file ...")
    logging_inited = True
    # Create a file handler to write logs to a file
    file_handler = logging.FileHandler(os.path.join(path, 'iox-plugin-ext.log'))
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    # Create a stream handler to output logs to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    # Add the file handler and stream handler to the logger
    LOGGER.addHandler(file_handler)
    LOGGER.addHandler(console_handler)

    # Use the logger in your extension
    #logger.debug('Debug message')
    #logger.info('Information message')
    #logger.warning('Warning message')
    #logger.error('Error message')
    #logger.critical('Critical message')
