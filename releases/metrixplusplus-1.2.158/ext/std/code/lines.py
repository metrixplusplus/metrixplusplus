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
        parser.add_option("--std.code.lines.code", "--sclc", action="store_true", default=False,
                         help="Enables collection of lines of code metric - "
                         "number of non-empty lines of code, excluding comments "
                         "[default: %default]")
        parser.add_option("--std.code.lines.preprocessor", "--sclp", action="store_true", default=False,
                         help="Enables collection of lines of preprocessor code metric - "
                         "number of non-empty lines of preprocessor code "
                         "[default: %default]")
        parser.add_option("--std.code.lines.comments", "--sclcom", action="store_true", default=False,
                         help="Enables collection of lines of comments metric - "
                         "number of non-empty lines of comments "
                         "[default: %default]")
        parser.add_option("--std.code.lines.total", "--sclt", action="store_true", default=False,
                         help="Enables collection of lines of comments metric - "
                         "number of non-empty lines of comments "
                         "[default: %default]")
    
    def configure(self, options):
        self.is_active_code = options.__dict__['std.code.lines.code']
        self.is_active_preprocessor = options.__dict__['std.code.lines.preprocessor']
        self.is_active_comments = options.__dict__['std.code.lines.comments']
        self.is_active_total = options.__dict__['std.code.lines.total']
        
    pattern_line = re.compile(r'''[^\s].*''')

    def initialize(self):
        self.declare_metric(self.is_active_code,
                       self.Field('code', int),
                       self.pattern_line,
                       mpp.api.Marker.T.CODE | mpp.api.Marker.T.STRING,
                       merge_markers=True)
        self.declare_metric(self.is_active_preprocessor,
                       self.Field('preprocessor', int),
                       self.pattern_line,
                       mpp.api.Marker.T.PREPROCESSOR)
        self.declare_metric(self.is_active_comments,
                       self.Field('comments', int),
                       self.pattern_line,
                       mpp.api.Marker.T.COMMENT)
        self.declare_metric(self.is_active_total,
                       self.Field('total', int),
                       self.pattern_line,
                       mpp.api.Marker.T.ANY,
                       merge_markers=True)

        super(Plugin, self).initialize(fields=self.get_fields())

        if self.is_active() == True:
            self.subscribe_by_parents_interface(mpp.api.ICode)
