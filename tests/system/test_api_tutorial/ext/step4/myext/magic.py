#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

import mpp.api
import re

class Plugin(mpp.api.Plugin,
             mpp.api.IConfigurable,
             mpp.api.Child,
             # reuse by inheriting standard metric facilities
             mpp.api.MetricPluginMixin):
    
    def declare_configuration(self, parser):
        parser.add_option("--myext.magic.numbers", "--mmn",
            action="store_true", default=False,
            help="Enables collection of magic numbers metric [default: %default]")
    
    def configure(self, options):
        self.is_active_numbers = options.__dict__['myext.magic.numbers']
    
    def initialize(self):
        # declare metric rules
        self.declare_metric(
            self.is_active_numbers, # to count if active in callback
            self.Field('numbers', int), # field name and type in the database
            re.compile(r'''\b[0-9]+\b'''), # pattern to search
            marker_type_mask=mpp.api.Marker.T.CODE, # search in code
            region_type_mask=mpp.api.Region.T.ANY) # search in all types of regions
        
        # use superclass facilities to initialize everything from declared fields
        super(Plugin, self).initialize(fields=self.get_fields())
        
        # subscribe to all code parsers if at least one metric is active
        if self.is_active() == True:
            self.subscribe_by_parents_interface(mpp.api.ICode)
