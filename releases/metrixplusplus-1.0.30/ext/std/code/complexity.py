#
#    Metrix++, Copyright 2009-2013, Metrix++ Project
#    Link: http://swi.sourceforge.net
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
        parser.add_option("--std.code.complexity.on", action="store_true", default=False,
                         help="Enables processing of complexity metrics: cyclomatic by McCabe [default: %default]")
    
    def configure(self, options):
        self.is_active = options.__dict__['std.code.complexity.on']
        
    def initialize(self):
        if self.is_active == True:
            namespace = self.get_plugin_loader().get_database_loader().create_namespace(self.get_name(), support_regions = True)
            namespace.add_field('cyclomatic', int)
            core.api.subscribe_by_parents_name('std.code.cpp', self, 'callback_cpp')

    # cyclomatic complexity pattern
    pattern = re.compile(r'''([^0-9A-Za-z_]((if)|(case)|(for)|(while))[^0-9A-Za-z_])|[&][&]|[|][|]|[?]''')

    def callback_cpp(self, parent, data):
        
        text = None
        for (ind, region) in enumerate(data.iterate_regions(filter_group=data.get_region_types().FUNCTION)):
            # cyclomatic complexity
            if ind == 0 and region.get_data(self.get_name(), 'cyclomatic') != None:
                return # data is available in first from cloned database, skip collection
            if text == None: # lazy loading for performance benefits
                text = data.get_content(exclude = data.get_marker_types().ALL_EXCEPT_CODE)
            
            count = 0
            start_pos = region.get_offset_begin()
            for sub_id in region.iterate_subregion_ids():
                # exclude sub regions, like enclosed classes
                count += len(self.pattern.findall(text, start_pos, data.get_region(sub_id).get_offset_begin()))
                start_pos = data.get_region(sub_id).get_offset_end()
            count += len(self.pattern.findall(text, start_pos, region.get_offset_end()))
            region.set_data(self.get_name(), 'cyclomatic', count)

