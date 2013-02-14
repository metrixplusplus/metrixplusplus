'''
Created on 26/06/2012

@author: konstaa
'''

import core.api

import os.path
import re

class Plugin(core.api.Plugin, core.api.IConfigurable):
    
    def declare_configuration(self, parser):
        parser.add_option("--general.db-file", default=r'./source-metrics.db',
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
        
        


    