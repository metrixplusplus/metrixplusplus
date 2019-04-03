#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

import mpp.api

class Plugin(mpp.api.Plugin,
             # make this instance configurable...
             mpp.api.IConfigurable):
    # ... and implement 2 interfaces
    
    def declare_configuration(self, parser):
        parser.add_option("--myext.magic.numbers", "--mmn",
            action="store_true", default=False,
            help="Enables collection of magic numbers metric [default: %default]")
        
    def configure(self, options):
        self.is_active_numbers = options.__dict__['myext.magic.numbers']
    
    def initialize(self):
        # use configuration option here
        if self.is_active_numbers == True:
            print "Hello world"

