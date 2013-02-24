#
#    Metrix++, Copyright 2009-2013, Metrix++ Project
#    Link: http://metrixplusplus.sourceforge.net
#    
#    This file is a part of Metrix++ Tool.
#    
#    Metrix++ is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License.
#    
#    Metrix++ is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with Metrix++.  If not, see <http://www.gnu.org/licenses/>.
#

import core.api
import logging
import os

class Plugin(core.api.Plugin, core.api.IConfigurable):
    
    def declare_configuration(self, parser, default_value='INFO'):
        allowed_values = ['DEBUG','INFO','WARNING','ERROR']
        default_value_cur = default_value
        if os.environ.has_key('general.log-level') and os.environ['general.log-level'] in allowed_values:
            default_value_cur = os.environ['general.log-level']
        parser.add_option("--general.log-level", default=default_value_cur, choices=allowed_values,
                         help="Defines log level. Possible values are 'DEBUG','INFO','WARNING' or 'ERROR'. "
                         "Default value is inherited from environment variable 'general.log-level' if set. "
                         "Otherwise, it is '" + default_value_cur +  "' [default: %default]")
    
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
        
        self.level = log_level
        logging.getLogger().setLevel(self.level)
        os.environ['general.log-level'] = options.__dict__['general.log_level']
        logging.warn("Logging enabled with " + options.__dict__['general.log_level'] + " level")



def set_default_format():
    logging.basicConfig(format="[LOG]: %(levelname)s:\t%(message)s", level=logging.WARN)