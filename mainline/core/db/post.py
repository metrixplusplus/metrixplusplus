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

import os.path
import re

import logging

class Plugin(core.api.Plugin, core.api.IConfigurable):
    
    def declare_configuration(self, parser):
        parser.add_option("--db-file", "--dbf", default='./metrixpp.db',
                         help="Primary database file to write (by the collector) and post-process (by other tools) [default: %default]")
        parser.add_option("--db-file-prev", "--dbfp", default=None,
                         help="Database file with data collected for the past/previous revision."
                             " If it is set for the collector tool to perform an incremental/iterative collection,"
                             " it may reduce the processing time significantly."
                             " Post-processing tools use it in order to recognise/evaluate change trends. [default: %default].")
        self.parser = parser
    
    def configure(self, options):
        self.dbfile = options.__dict__['db_file']
        self.dbfile_prev = options.__dict__['db_file_prev']
        
        if self.dbfile_prev != None and os.path.exists(self.dbfile_prev) == False:
            self.parser.error("File does not exist:" + self.dbfile_prev)

        
    def initialize(self):
        
        if self.get_plugin_loader() != None:
            if os.path.exists(self.dbfile):
                logging.warn("Removing existing file: " + self.dbfile)
                # TODO can reuse existing db file to speed up the processing?
                # TODO add option to choose to remove or to overwrite?
                try:
                    os.unlink(self.dbfile)
                except:
                    logging.warn("Failure in removing file: " + self.dbfile)
    
            created = self.get_plugin_loader().get_database_loader().create_database(self.dbfile, previous_db = self.dbfile_prev)
            if created == False:
                self.parser.error("Failure in creating file: " + self.dbfile)
            
            # do not process files dumped by this module
            self.get_plugin_loader().get_plugin('core.dir').add_exclude_rule(re.compile(r'^' + os.path.basename(self.dbfile) + r'$'))
            if self.dbfile_prev != None:
                self.get_plugin_loader().get_plugin('core.dir').add_exclude_rule(re.compile(r'^' + os.path.basename(self.dbfile_prev) + r'$'))

        else:
            self.loader_prev = core.api.Loader()
            if self.dbfile_prev != None:
                if self.loader_prev.open_database(self.dbfile_prev) == False:
                    self.parser.error("Can not open file: " + self.dbfile_prev)
            self.loader = core.api.Loader()
            if self.loader.open_database(self.dbfile) == False:
                self.parser.error("Can not open file: " + self.dbfile)

    def get_loader(self):
        return self.loader

    def get_loader_prev(self):
        return self.loader_prev
