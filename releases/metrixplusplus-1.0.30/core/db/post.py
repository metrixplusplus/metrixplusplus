#
#    Metrix++, Copyright 2009-2013, Metrix++ Project
#    Link: http://swi.sourceforge.net
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

import os.path
import re

class Plugin(core.api.Plugin, core.api.IConfigurable):
    
    def declare_configuration(self, parser):
        parser.add_option("--general.db-file", default='./metrixpp.db',
                         help="Primary database file to write (by the collector) and post-process (by other tools) [default: %default]")
        parser.add_option("--general.db-file-prev", default=None,
                         help="Database file with data collected for the past/previous revision [default: %default].")
    
    def configure(self, options):
        self.dbfile = options.__dict__['general.db_file']
        self.dbfile_prev = options.__dict__['general.db_file_prev']
        
    def initialize(self):
        
        self.get_plugin_loader().get_database_loader().create_database(self.dbfile, previous_db = self.dbfile_prev)    
        
        # do not process files dumped by this module
        self.get_plugin_loader().get_plugin('core.dir').add_exclude_rule(re.compile(r'^' + os.path.basename(self.dbfile) + r'$'))
        if self.dbfile_prev != None:
            self.get_plugin_loader().get_plugin('core.dir').add_exclude_rule(re.compile(r'^' + os.path.basename(self.dbfile_prev) + r'$'))
        
        


    