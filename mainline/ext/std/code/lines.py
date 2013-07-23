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
        
    def initialize(self):
        fields = []
        if self.is_active_code == True:
            fields.append(self.Field('code', int))
        if self.is_active_preprocessor == True:
            fields.append(self.Field('preprocessor', int))
        if self.is_active_comments == True:
            fields.append(self.Field('comments', int))
        if self.is_active_total == True:
            fields.append(self.Field('total', int))
        core.api.Plugin.initialize(self, fields=fields)
        
        if len(fields) != 0:
            core.api.subscribe_by_parents_interface(core.api.ICode, self, 'callback')

    pattern_line = re.compile(r'''[^\s].*''')

    def callback(self, parent, data, is_updated):
        is_updated = is_updated or self.is_updated
        if is_updated == True:
            if self.is_active_code == True:
                self.count_in_code(data,
                                   data.get_marker_types().ALL_EXCEPT_CODE,
                                   'code')
            if self.is_active_preprocessor == True:
                self.count_in_markers(data,
                                      data.get_marker_types().PREPROCESSOR,
                                      'preprocessor')
            if self.is_active_comments == True:
                self.count_in_markers(data,
                                      data.get_marker_types().COMMENT,
                                      'comments')
            if self.is_active_total == True:
                self.count_in_code(data,
                                   data.get_marker_types().NONE,
                                   'total')
    
    def count_in_code(self, data, exclude, field_name):
        text = data.get_content(exclude=exclude)
        for region in data.iterate_regions():
            count = 0
            start_pos = region.get_offset_begin()
            for sub_id in region.iterate_subregion_ids():
                count += len(self.pattern_line.findall(text, start_pos, data.get_region(sub_id).get_offset_begin()))
                start_pos = data.get_region(sub_id).get_offset_end()
            count += len(self.pattern_line.findall(text, start_pos, region.get_offset_end()))
            region.set_data(self.get_name(), field_name, count)
        
    def count_in_markers(self, data, marker_type, field_name):
        text = data.get_content()
        for region in data.iterate_regions():
            count = 0
            for marker in data.iterate_markers(
                            filter_group = marker_type,
                            region_id = region.get_id(),
                            exclude_children = True):
                count += len(self.pattern_line.findall(text, marker.get_offset_begin(), marker.get_offset_end()))
            region.set_data(self.get_name(), field_name, count)
            