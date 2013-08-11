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

class Plugin(mpp.api.Plugin,
             mpp.api.IConfigurable,
             mpp.api.Child,
             mpp.api.MetricPluginMixin):
    
    def declare_configuration(self, parser):
        parser.add_option("--myext.magic.numbers", "--mmn",
            action="store_true", default=False,
            help="Enables collection of magic numbers metric [default: %default]")
    
    def configure(self, options):
        self.is_active_numbers = options.__dict__['myext.magic.numbers']
    
    def initialize(self):
        # specialized pattern for java
        pattern_to_search_java = re.compile(
            r'''(const\s+([_$a-zA-Z][_$a-zA-Z0-9]*\s+)+[=]\s*)?[-+]?[0-9]+''')
        # pattern for C++ and C# languages
        pattern_to_search_cpp_cs = re.compile(
            r'''(const\s+([_a-zA-Z][_a-zA-Z0-9]*\s+)+[=]\s*)?[-+]?[0-9]+''')
        # pattern for all other languages
        pattern_to_search = re.compile(
            r'''[0-9]+''')
        self.declare_metric(self.is_active_numbers,
                            self.Field('numbers', int),
                            # dictionary of patterns instead of a single one
                            {
                             'std.code.java': pattern_to_search_java,
                             'std.code.cpp': pattern_to_search_cpp_cs,
                             'std.code.cs': pattern_to_search_cpp_cs,
                             '*': pattern_to_search
                            },
                            marker_type_mask=mpp.api.Marker.T.CODE,
                            region_type_mask=mpp.api.Region.T.ANY)
        
        super(Plugin, self).initialize(fields=self.get_fields())
        
        if self.is_active() == True:
            self.subscribe_by_parents_interface(mpp.api.ICode)

    def _numbers_count(self, alias, data, region, marker, match, count, counter_data):
        if match.group(0).startswith('const'):
            return count
        return count + 1