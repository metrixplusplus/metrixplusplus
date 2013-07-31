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

class Plugin(mpp.api.Plugin, mpp.api.SimpleMetricMixin, mpp.api.Child, mpp.api.IConfigurable):
    
    def declare_configuration(self, parser):
        parser.add_option("--std.code.complexity.cyclomatic", "--sccc", action="store_true", default=False,
                         help="Enables collection of cyclomatic complexity metric (McCabe) [default: %default]")
    
    def configure(self, options):
        self.is_active_cyclomatic = options.__dict__['std.code.complexity.cyclomatic']
        
    # cyclomatic complexity pattern
    # - C/C++
    pattern_cpp = re.compile(r'''([^0-9A-Za-z_]((if)|(case)|(for)|(while)|(catch))[^0-9A-Za-z_])|[&][&]|[|][|]|[?]''')
    # - C#
    #   supports Null-coalescing '??' and conditional '?:'
    pattern_cs = re.compile(r'''([^0-9A-Za-z_]((if)|(case)|(for)|(foreach)|(while)|(catch))[^0-9A-Za-z_])|[&][&]|[|][|]|[?][?]?''')
    # - Java
    pattern_java = re.compile(r'''([^0-9A-Za-z_]((if)|(case)|(for)|(while)|(catch))[^0-9A-Za-z_])|[&][&]|[|][|]|[?]''')

    def initialize(self):
        self.declare_metric(self.is_active_cyclomatic,
                            self.Field('cyclomatic', int),
                            {
                                'cpp': self.pattern_cpp,
                                'cs': self.pattern_cs,
                                'java': self.pattern_java
                            },
                            marker_type_mask=mpp.api.Marker.T.CODE,
                            region_type_mask=mpp.api.Region.T.FUNCTION)
        
        super(Plugin, self).initialize(fields=self.get_fields())
        
        if self.is_active() == True:
            self.subscribe_by_parents_name('std.code.cpp', 'callback_cpp')
            self.subscribe_by_parents_name('std.code.cs', 'callback_cs')
            self.subscribe_by_parents_name('std.code.java', 'callback_java')

    def callback_cpp(self, parent, data, is_updated):
        self.callback_common(parent, data, is_updated, 'cpp')

    def callback_cs(self, parent, data, is_updated):
        self.callback_common(parent, data, is_updated, 'cs')

    def callback_java(self, parent, data, is_updated):
        self.callback_common(parent, data, is_updated, 'java')

    def callback_common(self, parent, data, is_updated, alias):
        is_updated = is_updated or self.is_updated
        if is_updated == True:
            self.count_if_active('cyclomatic', data, alias=alias)

