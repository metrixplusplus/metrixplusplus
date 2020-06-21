#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

from metrixpp.mpp import api

class Plugin(api.Plugin,
             api.IConfigurable,
             # declare that it can subscribe on notifications
             api.Child):
    
    def declare_configuration(self, parser):
        parser.add_option("--myext.magic.numbers", "--mmn",
            action="store_true", default=False,
            help="Enables collection of magic numbers metric [default: %default]")
    
    def configure(self, options):
        self.is_active_numbers = options.__dict__['myext.magic.numbers']
    
    def initialize(self):
        if self.is_active_numbers == True:
            # subscribe to notifications from all code parsers
            self.subscribe_by_parents_interface(api.ICode, 'callback')

    # parents (code parsers) will call the callback declared
    def callback(self, parent, data, is_updated):
        print("{0} {1} {2}".format(parent.get_name(), data.get_path(), is_updated))
        
