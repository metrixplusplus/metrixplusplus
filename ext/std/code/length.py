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

class Plugin(mpp.api.Plugin, mpp.api.Child, mpp.api.IConfigurable):
    
    def declare_configuration(self, parser):
        parser.add_option("--std.code.length.total", "--sclent", action="store_true", default=False,
                         help="Enables collection of size metric (in number of symbols per region) [default: %default]")
    
    def configure(self, options):
        self.is_active = options.__dict__['std.code.length.total']
        
    def initialize(self):
        fields = []
        if self.is_active == True:
            fields.append(self.Field('total', int))
        mpp.api.Plugin.initialize(self, fields=fields)
        
        if len(fields) != 0:
            self.subscribe_by_parents_interface(mpp.api.ICode)

    def callback(self, parent, data, is_updated):
        is_updated = is_updated or self.is_updated
        if is_updated == True:
            for region in data.iterate_regions():
                size = 0
                start_pos = region.get_offset_begin()
                for sub_id in region.iterate_subregion_ids():
                    # exclude sub regions, like enclosed classes
                    size += data.get_region(sub_id).get_offset_begin() - start_pos
                    start_pos = data.get_region(sub_id).get_offset_end()
                size += region.get_offset_end() - start_pos
                region.set_data(self.get_name(), 'total', size)

