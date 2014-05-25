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
        parser.add_option("--std.code.member.fields", "--scmf",
            action="store_true", default=False,
            help="Enables collection of number of data members / fields "
            "per classes, structs and interfaces [default: %default]")
        parser.add_option("--std.code.member.globals", "--scmg",
            action="store_true", default=False,
            help="Enables collection of number of global variables / fields "
            "per global regions and namespaces [default: %default]")
        parser.add_option("--std.code.member.classes", "--scmc",
            action="store_true", default=False,
            help="Enables collection of number of classes defined "
            "per any region [default: %default]")
        parser.add_option("--std.code.member.structs", "--scms",
            action="store_true", default=False,
            help="Enables collection of number of structs defined "
            "per any region [default: %default]")
        parser.add_option("--std.code.member.interfaces", "--scmi",
            action="store_true", default=False,
            help="Enables collection of number of interfaces defined "
            "per any region [default: %default]")
        parser.add_option("--std.code.member.methods", "--scmm",
            action="store_true", default=False,
            help="Enables collection of number of methods (functions) defined "
            "per any region [default: %default]")
        parser.add_option("--std.code.member.namespaces", "--scmn",
            action="store_true", default=False,
            help="Enables collection of number of namespaces defined "
            "globally and enclosed (sub-namespaces) [default: %default]")
    
    def configure(self, options):
        self.is_active_fields = options.__dict__['std.code.member.fields']
        self.is_active_globals = options.__dict__['std.code.member.globals']
        self.is_active_classes = options.__dict__['std.code.member.classes']
        self.is_active_structs = options.__dict__['std.code.member.structs']
        self.is_active_interfaces = options.__dict__['std.code.member.interfaces']
        self.is_active_methods = options.__dict__['std.code.member.methods']
        self.is_active_namespaces = options.__dict__['std.code.member.namspaces']
    
    def initialize(self):
        # counts fields and properties with default getter/setter
        pattern_to_search_cs = re.compile(
            r'''([_a-zA-Z][_a-zA-Z0-9]*\s+[_a-zA-Z][_a-zA-Z0-9])\s*([=;]|[{]\s*(public\s+|private\s+|protected\s+|internal\s+)?(get|set)\s*[;])''')
        pattern_to_search_cpp_java = re.compile(
            r'''([_a-zA-Z][_a-zA-Z0-9]*\s+[_a-zA-Z][_a-zA-Z0-9])\s*[=;]''')
        self.declare_metric(self.is_active_fields,
                            self.Field('fields', int, _zero=True),
                            {
                             'std.code.java': pattern_to_search_cpp_java,
                             'std.code.cpp': pattern_to_search_cpp_java,
                             'std.code.cs': pattern_to_search_cs,
                            },
                            marker_type_mask=mpp.api.Marker.T.CODE,
                            region_type_mask=mpp.api.Region.T.CLASS |
                            mpp.api.Region.T.STRUCT | mpp.api.Region.T.INTERFACE)
        self.declare_metric(self.is_active_fields,
                            self.Field('globals', int, _zero=True),
                            {
                             'std.code.java': pattern_to_search_cpp_java,
                             'std.code.cpp': pattern_to_search_cpp_java,
                             'std.code.cs': pattern_to_search_cs,
                            },
                            marker_type_mask=mpp.api.Marker.T.CODE,
                            region_type_mask=mpp.api.Region.T.GLOBAL |
                            mpp.api.Region.T.NAMESPACE)
        
        super(Plugin, self).initialize(fields=self.get_fields())
        
        if self.is_active() == True:
            self.subscribe_by_parents_interface(mpp.api.ICode)

    class NumbersCounter(mpp.api.MetricPluginMixin.IterIncrementCounter):
        def increment(self, match):
            if (match.group(0).startswith('const') or
                (self.plugin.is_active_numbers_simplier == True and
                 match.group(0) in ['0', '1', '-1', '+1'])):
                return 0
            return 1
