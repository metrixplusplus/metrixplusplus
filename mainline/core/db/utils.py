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
        if checksum not in self.checksums.keys():
            return None

        if len(self.checksums[checksum]) == 0:
            return None
        
        elem = self.checksums[checksum].pop(0)
        next_id = elem[0]
        next_name = elem[1]

        self.names[next_name].remove((next_id, checksum))
        return next_id

    def get_next_id_once_by_name(self, name):
        if name not in self.names.keys():
            return None
        
        if len(self.names[name]) == 0:
            return None
        
        elem = self.names[name].pop(0)
        next_id = elem[0]
        next_checksum = elem[1]

        self.checksums[next_checksum].remove((next_id, name))
        return next_id
    
class FileRegionsMatcher(object):
    
    def __init__(self, file_data, prev_file_data):
        self.ids = [None] # add one to shift id from zero
        
        once_filter = FileRegionsDisposableGetter(prev_file_data)
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
