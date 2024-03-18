#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

from metrixpp.mpp import api
import re

class Plugin(api.Plugin,
             api.IConfigurable,
             api.Child,
             api.MetricPluginMixin):
    
    def declare_configuration(self, parser):
        parser.add_option("--myext.magic.numbers", "--mmn",
            action="store_true", default=False,
            help="Enables collection of magic numbers metric [default: %default]")
    
    def configure(self, options):
        self.is_active_numbers = options.__dict__['myext.magic.numbers']
    
    def initialize(self):
        # improve pattern to find declarations of constants
        pattern_to_search = re.compile(
            r'''((const(\s+[_a-zA-Z][_a-zA-Z0-9]*)+\s*[=]\s*)[-+]?[0-9]+\b)|(\b[0-9]+\b)''')
        self.declare_metric(self.is_active_numbers,
                            self.Field('numbers', int),
                            # give a pair of pattern + custom counter logic class
                            (pattern_to_search, self.NumbersCounter),
                            marker_type_mask=api.Marker.T.CODE,
                            region_type_mask=api.Region.T.ANY)
        
        super(Plugin, self).initialize(fields=self.get_fields())
        
        if self.is_active() == True:
            self.subscribe_by_parents_interface(api.ICode)
    
    # implement custom counter behavior:
    # increments counter by 1 only if single number spotted,
    # but not declaration of a constant
    class NumbersCounter(api.MetricPluginMixin.IterIncrementCounter):
        def increment(self, match):
            if match.group(0).startswith('const'):
                return 0
            return 1
