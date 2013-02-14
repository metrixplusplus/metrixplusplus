'''
Created on 26/06/2012

@author: konstaa
'''

import core.api
import logging

class Plugin(core.api.Plugin, core.api.IConfigurable):
    
    def declare_configuration(self, parser):
        parser.add_option("--general.log-level", default=r'INFO', choices=['DEBUG','INFO','WARNING','ERROR'],
                         help="Defines log level. Possible values are 'DEBUG','INFO','WARNING' or 'ERROR' [default: %default]")
    
    def configure(self, options):
        if options.__dict__['general.log_level'] == 'ERROR':
            log_level = logging.ERROR
        elif options.__dict__['general.log_level'] == 'WARNING':
            log_level = logging.WARNING
        elif options.__dict__['general.log_level'] == 'INFO':
            log_level = logging.INFO
        elif options.__dict__['general.log_level'] == 'DEBUG':
            log_level = logging.DEBUG
        else:
            raise AssertionError("Unhandled choice of log level")
        
        logging.getLogger().setLevel(log_level)
        logging.warn("Logging enabled with " + options.__dict__['general.log_level'] + " level")



def set_default_format():
    logging.basicConfig(format="[LOG]: %(levelname)s:\t%(message)s", level=logging.WARN)