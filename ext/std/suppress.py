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
import mpp.cout

import re

class Plugin(mpp.api.Plugin, mpp.api.Child, mpp.api.IConfigurable):
    
    def declare_configuration(self, parser):
        parser.add_option("--std.suppress", "--ss", action="store_true", default=False,
                         help="If set (True), suppression markers are collected from comments in code. "
                              "Suppressions are used by post-processing tools, like limit, to remove false-positive warnings. "
                              "Suppressions should be in the first comment block of a region (function/class/interface). "
                              "Format of suppressions: 'metrix++: suppress metric-name'. "
                              "For example: 'metrix++: suppress std.code.complexity:cyclomatic'. "
                              " [default: %default]")
    
    def configure(self, options):
        self.is_active = options.__dict__['std.suppress']
        
    def initialize(self):
        fields = []
        if self.is_active == True:
            fields.append(self.Field('count', int, non_zero=True))
            fields.append(self.Field('list', str))
        # - init per regions table
        mpp.api.Plugin.initialize(self, fields=fields)
        # - init per file table
        mpp.api.Plugin.initialize(self,
                                   namespace = self.get_name() + '.file',
                                   support_regions = False,
                                   fields=fields)
        
        if len(fields) != 0:
            self.subscribe_by_parents_interface(mpp.api.ICode)

    # suppress pattern
    pattern = re.compile(r'''metrix[+][+][:][ \t]+suppress[ \t]+([^ \t\r\n\*]+)''')

    def callback(self, parent, data, is_updated):
        is_updated = is_updated or self.is_updated
        if is_updated == True:
            text = data.get_content()
            file_count = 0
            file_list_text = []
            for region in data.iterate_regions():
                count = 0
                list_text = []
                last_comment_end = None
                for marker in data.iterate_markers(
                                filter_group = mpp.api.Marker.T.COMMENT,
                                region_id = region.get_id(),
                                exclude_children = True):
                    
                    if last_comment_end != None and len(text[last_comment_end:marker.get_offset_begin()].strip()) > 0:
                        # check continues comment blocks
                        # stop searching, if this comment block is separated from the last by non-blank string
                        break
                    last_comment_end = marker.get_offset_end()
                    
                    matches = self.pattern.findall(text, marker.get_offset_begin(), marker.get_offset_end())
                    for m in matches:
                        namespace_name, field = m.split(':')
                        db_loader = self.get_plugin('mpp.dbf').get_loader()
                        namespace = db_loader.get_namespace(namespace_name)
                        if namespace == None or namespace.check_field(field) == False:
                            mpp.cout.notify(data.get_path(), region.get_cursor(),
                                                  mpp.cout.SEVERITY_WARNING,
                                                  "Suppressed metric '" + namespace_name + ":" + field +
                                                    "' is not being collected",
                                                  [("Metric name", namespace_name + ":" + field),
                                                   ("Region name", region.get_name())])
                            continue
                        if namespace.are_regions_supported() == False:
                            if region.get_id() != 1:
                                mpp.cout.notify(data.get_path(), region.get_cursor(),
                                                  mpp.cout.SEVERITY_WARNING,
                                                  "Suppressed metric '" + namespace_name + ":" + field +
                                                    "' is attributed to a file, not a region. "
                                                    "Remove it or move to the beginning of the file.",
                                                  [("Metric name", namespace_name + ":" + field),
                                                   ("Region name", region.get_name())])
                                continue
                            
                            if m in file_list_text:
                                mpp.cout.notify(data.get_path(), region.get_cursor(),
                                              mpp.cout.SEVERITY_WARNING,
                                              "Duplicate suppression of the metric '" +
                                               namespace_name + ":" + field + "'",
                                              [("Metric name", namespace_name + ":" + field),
                                               ("Region name", None)])
                                continue
                            
                            file_count += 1
                            file_list_text.append(m)
                            continue
                        
                        if m in list_text:
                            mpp.cout.notify(data.get_path(), region.get_cursor(),
                                          mpp.cout.SEVERITY_WARNING,
                                          "Duplicate suppression of the metric '" +
                                           namespace_name + ":" + field + "'",
                                          [("Metric name", namespace_name + ":" + field),
                                           ("Region name", region.get_name())])
                            continue
                        
                        count += 1
                        list_text.append(m)
                        continue

                if count > 0:
                    region.set_data(self.get_name(), 'count', count)
                    region.set_data(self.get_name(), 'list', '[' + ']['.join(list_text) + ']')

            if file_count > 0:
                data.set_data(self.get_name() + '.file', 'count', file_count)
                data.set_data(self.get_name() + '.file', 'list', '[' + ']['.join(file_list_text) + ']')


