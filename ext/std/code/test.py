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
import logging

# used for testing and development purposes
class Plugin(mpp.api.Plugin, mpp.api.Child):
    
    def initialize(self):
        return
        # do not trigger version property set, it is a module for testing purposes
        self.subscribe_by_parents_interface(mpp.api.ICode)

    def callback(self, parent, data, is_updated):

        text = data.get_content()
        text_comb = ""
        for region in data.iterate_regions():
            logging.warn(region.get_name() + " " + str(region.get_cursor()))
            for marker in data.iterate_markers(region_id=region.get_id(),
                                               filter_group = mpp.api.Marker.T.ANY,
                                               exclude_children = True):
                logging.warn("\tMarker: " + mpp.api.Marker.T().to_str(marker.get_type()) +
                             " " + str(marker.get_offset_begin()) + " " + str(marker.get_offset_end()) +
                             " >>>" + text[marker.get_offset_begin():marker.get_offset_end()] + "<<<")
                text_comb += text[marker.get_offset_begin():marker.get_offset_end()]
        print "LENGTH:", len(text), len(text_comb)

        text_comb = ""
        for marker in data.iterate_markers(region_id=1,
                                           filter_group = mpp.api.Marker.T.ANY,
                                           exclude_children = False):
            logging.warn("\tMarker: " + mpp.api.Marker.T().to_str(marker.get_type()) +
                         " " + str(marker.get_offset_begin()) + " " + str(marker.get_offset_end()) +
                         " >>>" + text[marker.get_offset_begin():marker.get_offset_end()] + "<<<")
            text_comb += text[marker.get_offset_begin():marker.get_offset_end()]
        print "LENGTH:", len(text), len(text_comb)

        text_comb = ""
        for region in data.iterate_regions():
            logging.warn(region.get_name() + " " + str(region.get_cursor()))
            for marker in data.iterate_markers(region_id=region.get_id(),
                                               filter_group = mpp.api.Marker.T.ANY,
                                               exclude_children = True,
                                               merge = True):
                logging.warn("\tMarker: merged" + 
                             " " + str(marker.get_offset_begin()) + " " + str(marker.get_offset_end()) +
                             " >>>" + text[marker.get_offset_begin():marker.get_offset_end()] + "<<<")
                text_comb += text[marker.get_offset_begin():marker.get_offset_end()]
        print "LENGTH:", len(text), len(text_comb)
