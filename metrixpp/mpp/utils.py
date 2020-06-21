#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

from metrixpp.mpp.internal import py2xml
from metrixpp.mpp.internal import py2txt

import logging
import re
import os

class FileRegionsMatcher(object):

    class FileRegionsDisposableGetter(object):
        
        def __init__(self, file_data):
            self.checksums = {}
            self.names = {}
            
            for each in file_data.iterate_regions():
                if each.get_checksum() not in self.checksums:
                    self.checksums[each.get_checksum()] = []
                self.checksums[each.get_checksum()].append((each.get_id(), each.get_name())) 
                
                if each.get_name() not in self.names:
                    self.names[each.get_name()] = []
                self.names[each.get_name()].append((each.get_id(), each.get_checksum())) 
            
        def get_next_id_once_by_checksum(self, checksum):
            if checksum not in list(self.checksums.keys()):
                return None
    
            if len(self.checksums[checksum]) == 0:
                return None
            
            elem = self.checksums[checksum].pop(0)
            next_id = elem[0]
            next_name = elem[1]
    
            self.names[next_name].remove((next_id, checksum))
            return next_id
    
        def get_next_id_once_by_name(self, name):
            if name not in list(self.names.keys()):
                return None
            
            if len(self.names[name]) == 0:
                return None
            
            elem = self.names[name].pop(0)
            next_id = elem[0]
            next_checksum = elem[1]
    
            self.checksums[next_checksum].remove((next_id, name))
            return next_id
    
    def __init__(self, file_data, prev_file_data):
        self.ids = [None] # add one to shift id from zero
        
        once_filter = self.FileRegionsDisposableGetter(prev_file_data)
        unmatched_region_ids = []
        for (ind, region) in enumerate(file_data.iterate_regions()):
            assert(ind + 1 == region.get_id())
            # Identify corresponding region in previous database (attempt by checksum)
            prev_id = once_filter.get_next_id_once_by_checksum(region.checksum)
            if prev_id != None:
                self.ids.append((prev_id, False))
            else:
                unmatched_region_ids.append(region.get_id())
                self.ids.append((None, True))
                            
        # Identify corresponding region in previous database (attempt by name)
        for region_id in unmatched_region_ids: 
            prev_id = once_filter.get_next_id_once_by_name(file_data.get_region(region_id).name)
            if prev_id != None:
                self.ids[region_id] = (prev_id, True)
    
    def get_prev_id(self, curr_id):
        return self.ids[curr_id][0]

    def is_matched(self, curr_id):
        return (self.ids[curr_id][0] != None)

    def is_modified(self, curr_id):
        return self.ids[curr_id][1]

def preprocess_path(path):
    path = re.sub(r'''[\\]+''', "/", path)
    if os.path.isabs(path) == False and path.startswith('./') == False:
        path = './' + path
    logging.info("Processing: " + path)
    return path

def report_bad_path(path):
    logging.error("Specified path '" + path + "' is invalid: not found in the database records.")

def serialize_to_xml(data, root_name = None, digitCount = None):
    serializer = py2xml.Py2XML(digitCount)
    return serializer.parse(data, objName=root_name)

def serialize_to_python(data, root_name = None):
    prefix = ""
    postfix = ""
    if root_name != None:
        prefix = "{'" + root_name + "': " 
        postfix = "}"
    return prefix + data.__repr__() + postfix

def serialize_to_txt(data, root_name = None):
    serializer = py2txt.Py2TXT()
    return serializer.parse(data, objName=root_name, indent = -1)
