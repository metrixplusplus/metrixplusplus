#
#    Metrix++, Copyright 2009-2013, Metrix++ Project
#    Link: http://metrixplusplus.sourceforge.net
#    
#    This file is a part of Metrix++ Tool.
#    
#    Metrix++ is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License.
#    
#    Metrix++ is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with Metrix++.  If not, see <http://www.gnu.org/licenses/>.
#

import mpp.api

import re

class Plugin(mpp.api.Plugin, mpp.api.MetricPluginMixin, mpp.api.Child, mpp.api.IConfigurable):
    
    def declare_configuration(self, parser):
        parser.add_option("--std.code.complexity.cyclomatic", "--sccc", action="store_true", default=False,
                         help="Enables collection of cyclomatic complexity metric (McCabe) [default: %default]")
        parser.add_option("--std.code.complexity.maxindent", "--sccmi", action="store_true", default=False,
                         help="Enables collection of maximum indent level metric [default: %default]")
    
    def configure(self, options):
        self.is_active_cyclomatic = options.__dict__['std.code.complexity.cyclomatic']
        self.is_active_maxindent = options.__dict__['std.code.complexity.maxindent']
        
    # cyclomatic complexity pattern
    # - C/C++
    pattern_cpp = re.compile(r'''([^0-9A-Za-z_]((if)|(case)|(for)|(while)|(catch))[^0-9A-Za-z_])|[&][&]|[|][|]|[?]''')
    # - C#
    #   supports Null-coalescing '??' and conditional '?:'
    pattern_cs = re.compile(r'''([^0-9A-Za-z_]((if)|(case)|(for)|(foreach)|(while)|(catch))[^0-9A-Za-z_])|[&][&]|[|][|]|[?][?]?''')
    # - Java
    pattern_java = re.compile(r'''([^0-9A-Za-z_]((if)|(case)|(for)|(while)|(catch))[^0-9A-Za-z_])|[&][&]|[|][|]|[?]''')

    pattern_indent = re.compile(r'''[}{]''')

    def initialize(self):
        self.declare_metric(self.is_active_cyclomatic,
                            self.Field('cyclomatic', int),
                            {
                                'std.code.cpp': self.pattern_cpp,
                                'std.code.cs': self.pattern_cs,
                                'std.code.java': self.pattern_java
                            },
                            marker_type_mask=mpp.api.Marker.T.CODE,
                            region_type_mask=mpp.api.Region.T.FUNCTION)
        self.declare_metric(self.is_active_maxindent,
                            self.Field('maxindent', int),
                            {
                                'std.code.cpp': (self.pattern_indent, self.MaxIndentCounter),
                                'std.code.cs': (self.pattern_indent, self.MaxIndentCounter),
                                'std.code.java': (self.pattern_indent, self.MaxIndentCounter),
                            },
                            marker_type_mask=mpp.api.Marker.T.CODE,
                            region_type_mask=mpp.api.Region.T.FUNCTION)
        
        super(Plugin, self).initialize(fields=self.get_fields())
        
        if self.is_active() == True:
            self.subscribe_by_parents_names([
                'std.code.cpp',
                'std.code.cs',
                'std.code.java'
            ])

    class MaxIndentCounter(mpp.api.MetricPluginMixin.IterAssignCounter):
        
        def __init__(self, plugin, alias, data, region):
            super(Plugin.MaxIndentCounter, self).__init__(plugin, alias, data, region)
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
