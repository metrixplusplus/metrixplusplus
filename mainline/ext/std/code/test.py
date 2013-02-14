'''
Created on 26/06/2012

@author: konstaa
'''

import core.api

class Plugin(core.api.Plugin, core.api.Child, core.api.IConfigurable):
    
    def declare_configuration(self, parser):
        parser.add_option("--std.code.test.on", action="store_true", default=False,
                         help="Enables test plugin (for development purposes) [default: %default]")
    
    def configure(self, options):
        self.is_active = options.__dict__['std.code.test.on']
        
    def initialize(self):
        if self.is_active == True:
            core.api.subscribe_by_parents_interface(core.api.ICode, self)

    def callback(self, parent, data):
        
        def print_rec(data, indent, region_id):
            print ("   ." * indent) + str(data.get_region(region_id).get_type()) + " " + data.get_region(region_id).get_name() + " " + str(data.get_region(region_id).get_cursor())
            for sub_id in data.get_region(region_id).iterate_subregion_ids():
                print_rec(data, indent + 1, sub_id) 
        
        print_rec(data, 0, 1)
        