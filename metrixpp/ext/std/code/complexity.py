#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

from metrixpp.mpp import api

import re

class Plugin(api.Plugin, api.MetricPluginMixin, api.Child, api.IConfigurable):
    
    def declare_configuration(self, parser):
        parser.add_option("--std.code.complexity.cyclomatic", "--sccc", action="store_true", default=False,
                         help="Enables collection of cyclomatic complexity metric (McCabe) [default: %default]")
        parser.add_option("--std.code.complexity.cyclomatic_switch_case_once", "--scccnsc", action="store_true", default=False,
                         help="Enables collection of cyclomatic complexity metric (McCabe) switch case is only counted once [default: %default]")
        parser.add_option("--std.code.complexity.maxindent", "--sccmi", action="store_true", default=False,
                         help="Enables collection of maximum indent level metric [default: %default]")
    
    def configure(self, options):
        self.is_active_cyclomatic = options.__dict__['std.code.complexity.cyclomatic']
        self.is_active_cyclomatic_switch_case_once = options.__dict__['std.code.complexity.cyclomatic_switch_case_once']
        self.is_active_maxindent = options.__dict__['std.code.complexity.maxindent']
        
    # cyclomatic complexity pattern
    # - C/C++
    regex_cpp = r'''([^0-9A-Za-z_]((if)|(case)|(for)|(while)|(catch))[^0-9A-Za-z_])|[&][&]|[|][|]|[?]'''
    # - C#
    #   supports Null-coalescing '??' and conditional '?:'
    regex_cs = r'''([^0-9A-Za-z_]((if)|(case)|(for)|(foreach)|(while)|(catch))[^0-9A-Za-z_])|[&][&]|[|][|]|[?][?]?'''
    # - Java
    regex_java = r'''([^0-9A-Za-z_]((if)|(case)|(for)|(while)|(catch))[^0-9A-Za-z_])|[&][&]|[|][|]|[?]'''


    pattern_indent = re.compile(r'''[}{]''')

    def initialize(self):
        self.declare_metric(self.is_active_cyclomatic,
                            self.Field('cyclomatic', int),
                            {
                                'std.code.cpp': re.compile(self.regex_cpp),
                                'std.code.cs': re.compile(self.regex_cs),
                                'std.code.java': re.compile(self.regex_java)
                            },
                            marker_type_mask=api.Marker.T.CODE,
                            region_type_mask=api.Region.T.FUNCTION)
        # add the identical regex again but replace case with switch to count switch cases only once
        self.declare_metric(self.is_active_cyclomatic_switch_case_once,
                            self.Field('cyclomatic_switch_case_once', int),
                            {
                                'std.code.cpp': re.compile(self.regex_cpp.replace("(case)", "(switch)")),
                                'std.code.cs': re.compile(self.regex_cs.replace("(case)", "(switch)")),
                                'std.code.java': re.compile(self.regex_java.replace("(case)", "(switch)"))
                            },
                            marker_type_mask=api.Marker.T.CODE,
                            region_type_mask=api.Region.T.FUNCTION)
        self.declare_metric(self.is_active_maxindent,
                            self.Field('maxindent', int),
                            {
                                'std.code.cpp': (self.pattern_indent, self.MaxIndentCounter),
                                'std.code.cs': (self.pattern_indent, self.MaxIndentCounter),
                                'std.code.java': (self.pattern_indent, self.MaxIndentCounter),
                            },
                            marker_type_mask=api.Marker.T.CODE,
                            region_type_mask=api.Region.T.FUNCTION)
        
        super(Plugin, self).initialize(fields=self.get_fields())
        
        if self.is_active() == True:
            self.subscribe_by_parents_names([
                'std.code.cpp',
                'std.code.cs',
                'std.code.java'
            ])

    class MaxIndentCounter(api.MetricPluginMixin.IterAssignCounter):
        
        def __init__(self, *args, **kwargs):
            super(Plugin.MaxIndentCounter, self).__init__(*args, **kwargs)
            self.current_level = 0
            
        def assign(self, match):
            result = self.result
            if match.group(0) == '{':
                self.current_level += 1
                if self.current_level > self.result:
                    result = self.current_level
            elif match.group(0) == '}':
                self.current_level -= 1
            else:
                assert False
            return result
