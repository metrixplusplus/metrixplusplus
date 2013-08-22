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
        self.parser = parser
        parser.add_option("--std.code.todo.comments", "--sctc",
            action="store_true", default=False,
            help="Enables collection of number of todo/fixme/etc markers in comments [default: %default]")
        parser.add_option("--std.code.todo.strings", "--scts",
            action="store_true", default=False,
            help="Enables collection of number of todo/fixme/etc markers in strings [default: %default]")
        parser.add_option("--std.code.todo.tags", "--sctt", type=str,
            default="TODO,ToDo,FIXME,FixMe,TBD,HACK,XXX",
            help="A list of typical todo markers to search, separated by comma [default: %default]")
    
    def configure(self, options):
        self.is_active_comments = options.__dict__['std.code.todo.comments']
        self.is_active_strings = options.__dict__['std.code.todo.strings']
        self.tags_list = options.__dict__['std.code.todo.tags'].split(',')
        self.tags_list.sort()
        for tag in self.tags_list:
            if re.match(r'''^[A-Za-z0-9]+$''', tag) == None:
                self.parser.error('option --std.code.todo.tags: tag {0} includes not allowed symbols'.
                                  format(tag))
        self.pattern_to_search = re.compile(
            r'\b({0})\b'.
            format('|'.join(self.tags_list)))

    def initialize(self):
        self.declare_metric(self.is_active_comments,
                            self.Field('comments', int, non_zero=True),
                            self.pattern_to_search,
                            marker_type_mask=mpp.api.Marker.T.COMMENT,
                            region_type_mask=mpp.api.Region.T.ANY)
        self.declare_metric(self.is_active_strings,
                            self.Field('strings', int, non_zero=True),
                            self.pattern_to_search,
                            marker_type_mask=mpp.api.Marker.T.STRING,
                            region_type_mask=mpp.api.Region.T.ANY)
        
        super(Plugin, self).initialize(fields=self.get_fields(),
            properties=[self.Property('tags', ','.join(self.tags_list))])
        
        if self.is_active() == True:
            self.subscribe_by_parents_interface(mpp.api.ICode)
