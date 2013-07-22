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

import core.api

import re

class Plugin(core.api.Plugin, core.api.Child, core.api.IConfigurable):
    
    def declare_configuration(self, parser):
        parser.add_option("--std.code.complexity.cyclomatic", "--sccc", action="store_true", default=False,
                         help="Enables collection of cyclomatic complexity metric (McCabe) [default: %default]")
    
    def configure(self, options):
        self.is_active = options.__dict__['std.code.complexity.cyclomatic']
        
    def initialize(self):
        fields = []
        if self.is_active == True:
            fields.append(self.Field('cyclomatic', int))
        core.api.Plugin.initialize(self, fields=fields)
        
        if len(fields) != 0:
            core.api.subscribe_by_parents_name('std.code.cpp', self, 'callback_cpp')
            core.api.subscribe_by_parents_name('std.code.cs', self, 'callback_cs')
            core.api.subscribe_by_parents_name('std.code.java', self, 'callback_java')

    # cyclomatic complexity pattern
    # - C/C++
    pattern_cpp = re.compile(r'''([^0-9A-Za-z_]((if)|(case)|(for)|(while)|(catch))[^0-9A-Za-z_])|[&][&]|[|][|]|[?]''')
    # - C#
    #   supports Null-coalescing '??' and conditional '?:'
    pattern_cs = re.compile(r'''([^0-9A-Za-z_]((if)|(case)|(for)|(foreach)|(while)|(catch))[^0-9A-Za-z_])|[&][&]|[|][|]|[?][?]?''')
    # - Java
    pattern_java = re.compile(r'''([^0-9A-Za-z_]((if)|(case)|(for)|(while)|(catch))[^0-9A-Za-z_])|[&][&]|[|][|]|[?]''')

    def callback_cpp(self, parent, data, is_updated):
        self.callback_common(parent, data, is_updated, self.pattern_cpp)

    def callback_cs(self, parent, data, is_updated):
        self.callback_common(parent, data, is_updated, self.pattern_cs)

    def callback_java(self, parent, data, is_updated):
        self.callback_common(parent, data, is_updated, self.pattern_java)

    def callback_common(self, parent, data, is_updated, pattern):
        is_updated = is_updated or self.is_updated
        if is_updated == True:
            text = data.get_content(exclude = data.get_marker_types().ALL_EXCEPT_CODE)
            for region in data.iterate_regions(filter_group=data.get_region_types().FUNCTION):
                # cyclomatic complexity
                count = 0
                start_pos = region.get_offset_begin()
                for sub_id in region.iterate_subregion_ids():
                    # exclude sub regions, like enclosed classes
                    count += len(pattern.findall(text, start_pos, data.get_region(sub_id).get_offset_begin()))
                    start_pos = data.get_region(sub_id).get_offset_end()
                count += len(pattern.findall(text, start_pos, region.get_offset_end()))
                region.set_data(self.get_name(), 'cyclomatic', count)

