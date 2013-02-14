'''
Created on 26/06/2012

@author: konstaa
'''

import core.api

class Plugin(core.api.Plugin, core.api.Child, core.api.IConfigurable):
    
    def declare_configuration(self, parser):
        parser.add_option("--std.code.brackets.on", action="store_true", default=False,
                         help="If enabled, counts number of mismatched brackets '{}' [default: %default]")
    
    def configure(self, options):
        self.is_active = options.__dict__['std.code.brackets.on']
        
    def initialize(self):
        if self.is_active == True:
            namespace = self.get_plugin_loader().get_database_loader().create_namespace(self.get_name())
            namespace.add_field('curly', int)
            core.api.subscribe_by_parents_name('std.code.cpp', self, 'callback_cpp')

    def callback_cpp(self, parent, data):
        if data.get_data(self.get_name(), 'curly') != None:
            return # data is available from cloned database, skip collection
        data.set_data(self.get_name(), 'curly', data.get_data(parent.get_name(), 'mismatched_brackets'))
