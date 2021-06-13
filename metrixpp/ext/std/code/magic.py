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
        parser.add_option("--std.code.magic.numbers", "--scmn",
            action="store_true", default=False,
            help="Enables collection of magic numbers metric [default: %default]")
        parser.add_option("--std.code.magic.numbers.simplier", "--scmns",
            action="store_true", default=False,
            help="Is set, 0, -1 and 1 numbers are not counted "
            "in 'std.code.magic.numbers' metric [default: %default]")
    
    def configure(self, options):
        self.is_active_numbers = options.__dict__['std.code.magic.numbers']
        self.is_active_numbers_simplier = options.__dict__['std.code.magic.numbers.simplier']
    
    def initialize(self):
        # C++ Source: https://en.cppreference.com/w/cpp/language/integer_literal
        # C Source: https://en.cppreference.com/w/c/language/integer_constant
        cpp_number_patterns = []
        cpp_number_patterns.append(r'''[1-9]('?[0-9])*''')
        cpp_number_patterns.append(r'''0('?[0-7])*''')  # 0 is here
        cpp_number_patterns.append(r'''0[xX][0-9a-fA-F]('?[0-9a-fA-F])*''')
        cpp_number_patterns.append(r'''0[bB][01]('?[01])*''')

        cpp_number_suffix = r'(ll|LL|[lLzZ])'
        cpp_number_suffix = r'([uU]?{s}?|{s}[uU])'.format(s=cpp_number_suffix)

        cpp_number_pattern = r'({}){}'.format(r'|'.join(cpp_number_patterns),
                                              cpp_number_suffix)

        pattern_to_search_java = re.compile(
            r'''((const(\s+[_$a-zA-Z][_$a-zA-Z0-9]*)+\s*[=]\s*)[-+]?[0-9]+\b)'''
            r'''|(\b[0-9]+\b)''')
        pattern_to_search_cpp = re.compile(
            r'''((const(expr)?(\s+[_a-zA-Z][_a-zA-Z0-9]*)+\s*[=]\s*)[-+]?''' +
            cpp_number_pattern + r'''\b)'''
            r'''|(virtual\s+.*\s*[=]\s*[0]\s*[,;])'''
            r'''|(override\s+[=]\s*[0]\s*[,;])'''
            r'''|(\b''' + cpp_number_pattern + r'''\b)''')
        pattern_to_search_cs = re.compile(
            r'''((const(\s+[_a-zA-Z][_a-zA-Z0-9]*)+\s*[=]\s*)[-+]?[0-9]+\b)'''
            r'''|(\b[0-9]+\b)''')
        self.declare_metric(self.is_active_numbers,
                            self.Field('numbers', int,
                                non_zero=True),
                            {
                             'std.code.java': (pattern_to_search_java, self.NumbersCounter),
                             'std.code.cpp': (pattern_to_search_cpp, self.NumbersCounter),
                             'std.code.cs': (pattern_to_search_cs, self.NumbersCounter),
                            },
                            marker_type_mask=api.Marker.T.CODE,
                            region_type_mask=api.Region.T.ANY)
        
        super(Plugin, self).initialize(fields=self.get_fields(),
            properties=[self.Property('number.simplier', self.is_active_numbers_simplier)])
        
        if self.is_active() == True:
            self.subscribe_by_parents_interface(api.ICode)

    class NumbersCounter(api.MetricPluginMixin.IterIncrementCounter):
        def increment(self, match):
            if (match.group(0).startswith('const') or
                match.group(0).startswith('virtual') or
                match.group(0).startswith('override') or
                (self.plugin.is_active_numbers_simplier == True and
                 match.group(0) in ['0', '1', '-1', '+1'])):
                return 0
            return 1
