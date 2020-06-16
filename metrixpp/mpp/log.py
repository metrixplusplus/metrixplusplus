#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

from metrixpp.mpp import api
import logging
import os

class Plugin(api.BasePlugin, api.IConfigurable):
    
    def declare_configuration(self, parser, default_value='INFO'):
        allowed_values = ['DEBUG','INFO','WARNING','ERROR']
        default_value_cur = default_value
        if '__import__' in os.environ and os.environ['METRIXPLUSPLUS_LOG_LEVEL'] in allowed_values:
            default_value_cur = os.environ['METRIXPLUSPLUS_LOG_LEVEL']
        parser.add_option("--log-level", "--ll", default=default_value_cur, choices=allowed_values,
                         help="Defines log level. Possible values are 'DEBUG','INFO','WARNING' or 'ERROR'. "
                         "Default value is inherited from environment variable 'METRIXPLUSPLUS_LOG_LEVEL' if set. "
                         "[default: " + default_value + "]")
    
    def configure(self, options):
        if options.__dict__['log_level'] == 'ERROR':
            log_level = logging.ERROR
        elif options.__dict__['log_level'] == 'WARNING':
            log_level = logging.WARNING
        elif options.__dict__['log_level'] == 'INFO':
            log_level = logging.INFO
        elif options.__dict__['log_level'] == 'DEBUG':
            log_level = logging.DEBUG
        else:
            raise AssertionError("Unhandled choice of log level")
        
        self.level = log_level
        logging.getLogger().setLevel(self.level)
        os.environ['METRIXPLUSPLUS_LOG_LEVEL'] = options.__dict__['log_level']
        logging.warn("Logging enabled with " + options.__dict__['log_level'] + " level")

    def initialize(self):
        super(Plugin, self).initialize()
        set_default_format()

def set_default_format():
    logging.basicConfig(format="[LOG]: %(levelname)s:\t%(message)s", level=logging.WARN)
