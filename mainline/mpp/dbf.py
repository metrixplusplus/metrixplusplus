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

import mpp.api

import os.path
import logging

class Plugin(mpp.api.Plugin, mpp.api.IConfigurable):
    
    def declare_configuration(self, parser):
        if self.get_action() == 'collect':
            dbfile_help = "Path to a database file to create and write [default: %default]."
            dbfile_prev_help = ("Path to database file with data collected for the past/previous code revision."
                             " If it is set, the tool will do an incremental/iterative collection."
                             " It may reduce the time of processing significantly [default: %default].")
        else:
            dbfile_help = "Path to a database file to read and process [default: %default]."
            dbfile_prev_help = ("Path to database file with data collected for the past/previous code revision."
                                " It is used to identify and evaluate/analyze change trends. [default: %default].")
        parser.add_option("--db-file", "--dbf", default='./metrixpp.db',
                         help=dbfile_help)
        parser.add_option("--db-file-prev", "--dbfp", default=None,
                         help=dbfile_prev_help)
        self.parser = parser
    
    def configure(self, options):
        self.dbfile = options.__dict__['db_file']
        self.dbfile_prev = options.__dict__['db_file_prev']
        
        if self.dbfile_prev != None and os.path.exists(self.dbfile_prev) == False:
            self.parser.error("option --db-file-prev: File '{0}' does not exist".format(self.dbfile_prev))

        
    def initialize(self):
        
        if self.get_action() == 'collect':
            if os.path.exists(self.dbfile):
                logging.warn("Removing existing file: " + self.dbfile)
                try:
                    os.unlink(self.dbfile)
                except:
                    logging.warn("Failure in removing file: " + self.dbfile)
    
            self.loader = mpp.api.Loader()
            created = self.loader.create_database(self.dbfile, previous_db = self.dbfile_prev)
            if created == False:
                self.parser.error("option --db-file: Can not create file '{0}'".format(self.dbfile))
            
        else:
            self.loader = mpp.api.Loader()
            if self.loader.open_database(self.dbfile) == False:
                self.parser.error("option --db-file: Can not open file '{0}'".format(self.dbfile))
            self.loader_prev = mpp.api.Loader()
            if self.dbfile_prev != None:
                if self.loader_prev.open_database(self.dbfile_prev) == False:
                    self.parser.error("option --db-file-prev: Can not open file '{0}'".format(self.dbfile_prev))
                self._warn_on_metadata()

    def _warn_on_metadata(self):
        for each in self.loader.iterate_properties():
            prev = self.loader_prev.get_property(each.name)
            if prev != each.value:
                logging.warn("Data files have been created by different versions of the tool or with different settings.")
                logging.warn(" - identification of some change trends can be not reliable")
                logging.warn(" - use 'info' action to view more details")

    def get_dbfile_path(self):
        return self.dbfile

    def get_dbfile_prev_path(self):
        return self.dbfile_prev

    def get_loader(self):
        return self.loader

    def get_loader_prev(self, none_if_empty=False):
        if none_if_empty == True and self.dbfile_prev == None:
            return None
        return self.loader_prev
