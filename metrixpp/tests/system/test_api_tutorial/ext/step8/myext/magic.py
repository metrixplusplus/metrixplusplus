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
        # Add new option
        parser.add_option("--myext.magic.numbers.simplier", "--mmns",
            action="store_true", default=False,
            help="Is set, 0, -1 and 1 numbers are not counted [default: %default]")
    
    def configure(self, options):
        self.is_active_numbers = options.__dict__['myext.magic.numbers']
        # remember the option here
        self.is_active_numbers_simplier = options.__dict__['myext.magic.numbers.simplier']
    
    def initialize(self):
        pattern_to_search_java = re.compile(
            r'''((const(\s+[_$a-zA-Z][_$a-zA-Z0-9]*)+\s*[=]\s*)[-+]?[0-9]+\b)|(\b[0-9]+\b)''')
        pattern_to_search_cpp_cs = re.compile(
            r'''((const(\s+[_a-zA-Z][_a-zA-Z0-9]*)+\s*[=]\s*)[-+]?[0-9]+\b)|(\b[0-9]+\b)''')
        pattern_to_search = re.compile(
            r'''\b[0-9]+\b''')
        self.declare_metric(self.is_active_numbers,
                            self.Field('numbers', int,
                                non_zero=True),
                            {
                             'std.code.java': (pattern_to_search_java, self.NumbersCounter),
                             'std.code.cpp': (pattern_to_search_cpp_cs, self.NumbersCounter),
                             'std.code.cs': (pattern_to_search_cpp_cs, self.NumbersCounter),
                             '*': pattern_to_search
                            },
                            marker_type_mask=api.Marker.T.CODE,
                            region_type_mask=api.Region.T.ANY)
        
        super(Plugin, self).initialize(fields=self.get_fields(),
            # remember option settings in data file properties
            # in order to detect changes in settings on iterative re-run
            properties=[self.Property('number.simplier', self.is_active_numbers_simplier)])
        
        if self.is_active() == True:
            self.subscribe_by_parents_interface(api.ICode)

    class NumbersCounter(api.MetricPluginMixin.IterIncrementCounter):
        def increment(self, match):
            if (match.group(0).startswith('const') or
                (self.plugin.is_active_numbers_simplier == True and
                 match.group(0) in ['0', '1', '-1', '+1'])):
                return 0
            return 1
