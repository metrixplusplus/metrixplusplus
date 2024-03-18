#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

from metrixpp.mpp import api
import logging

# used for testing and development purposes
class Plugin(api.Plugin, api.Child):
    
    def initialize(self):
        return
        # do not trigger version property set, it is a module for testing purposes
        self.subscribe_by_parents_interface(api.ICode)

    def callback(self, parent, data, is_updated):

        text = data.get_content()
        text_comb = ""
        for region in data.iterate_regions():
            logging.warn(region.get_name() + " " + str(region.get_cursor()))
            for marker in data.iterate_markers(region_id=region.get_id(),
                                               filter_group = api.Marker.T.ANY,
                                               exclude_children = True):
                logging.warn("\tMarker: " + api.Marker.T().to_str(marker.get_type()) +
                             " " + str(marker.get_offset_begin()) + " " + str(marker.get_offset_end()) +
                             " >>>" + text[marker.get_offset_begin():marker.get_offset_end()] + "<<<")
                text_comb += text[marker.get_offset_begin():marker.get_offset_end()]
        print("LENGTH:", len(text), len(text_comb))

        text_comb = ""
        for marker in data.iterate_markers(region_id=1,
                                           filter_group = api.Marker.T.ANY,
                                           exclude_children = False):
            logging.warn("\tMarker: " + api.Marker.T().to_str(marker.get_type()) +
                         " " + str(marker.get_offset_begin()) + " " + str(marker.get_offset_end()) +
                         " >>>" + text[marker.get_offset_begin():marker.get_offset_end()] + "<<<")
            text_comb += text[marker.get_offset_begin():marker.get_offset_end()]
        print("LENGTH:", len(text), len(text_comb))

        text_comb = ""
        for region in data.iterate_regions():
            logging.warn(region.get_name() + " " + str(region.get_cursor()))
            for marker in data.iterate_markers(region_id=region.get_id(),
                                               filter_group = api.Marker.T.ANY,
                                               exclude_children = True,
                                               merge = True):
                logging.warn("\tMarker: merged" + 
                             " " + str(marker.get_offset_begin()) + " " + str(marker.get_offset_end()) +
                             " >>>" + text[marker.get_offset_begin():marker.get_offset_end()] + "<<<")
                text_comb += text[marker.get_offset_begin():marker.get_offset_end()]
        print("LENGTH:", len(text), len(text_comb))
