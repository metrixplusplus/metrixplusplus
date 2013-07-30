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

import logging
import os.path

import core.api
import core.db.sqlite

####################################
# Data Interface
####################################

class Data(object):

    def __init__(self):
        self.data = {}

    def get_data(self, namespace, field):
        if namespace not in self.data.keys():
            return None
        if field not in self.data[namespace].keys():
            return None
        return self.data[namespace][field]

    def set_data(self, namespace, field, value):
        if namespace not in self.data:
            self.data[namespace] = {}
        self.data[namespace][field] = value
    
    def iterate_namespaces(self):
        for namespace in self.data.keys():
            yield namespace
            
    def iterate_fields(self, namespace):
        for field in self.data[namespace].keys():
            yield (field, self.data[namespace][field])

    def get_data_tree(self, namespaces=None):
        return self.data

    def __repr__(self):
        return object.__repr__(self) + " with data " + self.data.__repr__()


class LoadableData(Data):
    
    def __init__(self, loader, file_id, region_id):
        Data.__init__(self)
        self.loader = loader
        self.file_id = file_id
        self.region_id = region_id
        self.loaded_namespaces = []
        self.changed_namespaces = []

    def load_namespace(self, namespace):
        try:
            row = self.loader.db.get_row(namespace, self.file_id, self.region_id)
        except Exception:
            logging.debug("No data in the database for namespace: " + namespace)
            return
        if row == None:
            return 
        for column_name in row.keys():
            packager = self.loader.get_namespace(namespace).get_field_packager(column_name)
            if packager == None:
                continue
            if row[column_name] == None:
                continue
            Data.set_data(self, namespace, column_name, packager.unpack(row[column_name]))
        
    def set_data(self, namespace, field, value):
        if namespace not in self.changed_namespaces:
            self.changed_namespaces.append(namespace)
        return Data.set_data(self, namespace, field, value)

    def get_data(self, namespace, field):
        if namespace not in self.loaded_namespaces:
            self.loaded_namespaces.append(namespace)
            self.load_namespace(namespace)
        return Data.get_data(self, namespace, field)
    
    def is_namespace_updated(self, namespace):
        return namespace in self.changed_namespaces

    def is_namespace_loaded(self, namespace):
        return namespace in self.loaded_namespaces

    def get_data_tree(self, namespaces=None):
        if namespaces == None:
            namespaces = self.loader.iterate_namespace_names()
        for each in namespaces:
            self.load_namespace(each)
        return Data.get_data_tree(self)
    
class FileRegionData(LoadableData):
    class T(object):
        NONE      = 0x00
        GLOBAL    = 0x01
        CLASS     = 0x02
        STRUCT    = 0x04
        NAMESPACE = 0x08
        FUNCTION  = 0x10
        INTERFACE = 0x20
        ANY       = 0xFF
        
        def to_str(self, group):
            if group == self.NONE:
                return "none"
            elif group == self.GLOBAL:
                return "global"
            elif group == self.CLASS:
                return "class"
            elif group == self.STRUCT:
                return "struct"
            elif group == self.NAMESPACE:
                return "namespace"
            elif group == self.FUNCTION:
                return "function"
            elif group == self.INTERFACE:
                return "interface"
            else:
                assert(False)
    
    def __init__(self, loader, file_id, region_id, region_name, offset_begin, offset_end, line_begin, line_end, cursor_line, group, checksum):
        LoadableData.__init__(self, loader, file_id, region_id)
        self.name = region_name
        self.begin = offset_begin
        self.end = offset_end
        self.line_begin = line_begin
        self.line_end = line_end
        self.cursor = cursor_line
        self.group = group
        self.checksum = checksum
        
        self.children = []
    
    def get_id(self):
        return self.region_id

    def get_name(self):
        return self.name

    def get_offset_begin(self):
        return self.begin

    def get_offset_end(self):
        return self.end

    def get_line_begin(self):
        return self.line_begin

    def get_line_end(self):
        return self.line_end

    def get_cursor(self):
        return self.cursor

    def get_type(self):
        return self.group

    def get_checksum(self):
        return self.checksum
    
    def register_subregion_id(self, child_id):
        self.children.append(child_id)

    def iterate_subregion_ids(self):
        return self.children

class Marker(object):
    class T(object):
        NONE            = 0x00
        COMMENT         = 0x01
        STRING          = 0x02
        PREPROCESSOR    = 0x04
        CODE            = 0x08
        ALL_EXCEPT_CODE = 0x07
        ANY             = 0xFF

        def to_str(self, group):
            if group == self.NONE:
                return "none"
            elif group == self.COMMENT:
                return "comment"
            elif group == self.STRING:
                return "string"
            elif group == self.PREPROCESSOR:
                return "preprocessor"
            elif group == self.CODE:
                return "code"
            else:
                assert(False)
        
    def __init__(self, offset_begin, offset_end, group):
        self.begin = offset_begin
        self.end = offset_end
        self.group = group
        
    def get_offset_begin(self):
        return self.begin

    def get_offset_end(self):
        return self.end

    def get_type(self):
        return self.group

class FileData(LoadableData):
    
    def __init__(self, loader, path, file_id, checksum, content):
        LoadableData.__init__(self, loader, file_id, None)
        self.path = path
        self.checksum = checksum
        self.content = content
        self.regions = None
        self.markers = None
        self.loader = loader
        self.loading_tmp = []
        
    def get_id(self):
        return self.file_id

    def get_path(self):
        return self.path

    def get_checksum(self):
        return self.checksum
    
    def get_content(self, exclude = Marker.T.NONE):
        if exclude == Marker.T.NONE:
            return self.content
        
        if exclude == (Marker.T.COMMENT | Marker.T.STRING | Marker.T.PREPROCESSOR):
            # optimise frequent queries of this type
            if hasattr(self, 'content_cache'):
                return self.content_cache
        
        last_pos = 0
        content = ""
        for marker in self.iterate_markers(exclude):
            content += self.content[last_pos:marker.begin]
            content += " " * (marker.end - marker.begin)
            last_pos = marker.end
        content += self.content[last_pos:]

        if exclude == (Marker.T.COMMENT | Marker.T.STRING | Marker.T.PREPROCESSOR):
            self.content_cache = content
        
        assert(len(content) == len(self.content))
        return content

    def internal_append_region(self, region):
        # here we apply some magic - we rely on special ordering of coming regions,
        # which is supported by code parsers
        prev_id = None
        while True:
            if len(self.loading_tmp) == 0:
                break
            prev_id = self.loading_tmp.pop()
            if self.get_region(prev_id).get_offset_end() > region.get_offset_begin():
                self.loading_tmp.append(prev_id) # return back
                break
        self.loading_tmp.append(region.get_id())
        if prev_id != None:
            self.get_region(prev_id).register_subregion_id(region.get_id())
        self.regions.append(region)

    def load_regions(self):
        if self.regions == None:
            self.regions = []
            for each in self.loader.db.iterate_regions(self.get_id()):
                self.internal_append_region(FileRegionData(self.loader,
                                                   self.get_id(),
                                                   each.region_id,
                                                   each.name,
                                                   each.begin,
                                                   each.end,
                                                   each.line_begin,
                                                   each.line_end,
                                                   each.cursor,
                                                   each.group,
                                                   each.checksum))
                assert(len(self.regions) == each.region_id)
        
    def add_region(self, region_name, offset_begin, offset_end, line_begin, line_end, cursor_line, group, checksum):
        if self.regions == None:
            self.regions = [] # do not load in time of collection
        new_id = len(self.regions) + 1
        self.internal_append_region(FileRegionData(self.loader, self.get_id(), new_id, region_name, offset_begin, offset_end, line_begin, line_end, cursor_line, group, checksum))
        self.loader.db.create_region(self.file_id, new_id, region_name, offset_begin, offset_end, line_begin, line_end, cursor_line, group, checksum)
        return new_id
        
    def get_region(self, region_id):
        self.load_regions()
        return self.regions[region_id - 1]
    
    def get_region_types(self):
        return FileRegionData.T

    def iterate_regions(self, filter_group = FileRegionData.T.ANY):
        self.load_regions()
        for each in self.regions:
            if each.group & filter_group:
                yield each

    def are_regions_loaded(self):
        return self.regions != None

    def load_markers(self):
        if self.markers == None:
            self.markers = []
            for each in self.loader.db.iterate_markers(self.get_id()):
                self.markers.append(Marker(each.begin, each.end, each.group))
        
    def add_marker(self, offset_begin, offset_end, group):
        if self.markers == None:
            self.markers = [] # do not load in time of collection
        self.markers.append(Marker(offset_begin, offset_end, group))
        self.loader.db.create_marker(self.file_id, offset_begin, offset_end, group)
        
    def iterate_markers(self, filter_group = Marker.T.COMMENT |
                         Marker.T.STRING | Marker.T.PREPROCESSOR,
                         region_id = None, exclude_children = True, merge = False):
        self.load_markers()
        
        if merge == True:
            next_marker = None
            for marker in self.iterate_markers(filter_group, region_id, exclude_children, merge = False):
                if next_marker != None:
                    if next_marker.get_offset_end() == marker.get_offset_begin():
                        # sequential markers
                        next_marker = Marker(next_marker.get_offset_begin(),
                                             marker.get_offset_end(),
                                             next_marker.get_type() | marker.get_type())
                    else:
                        yield next_marker
                        next_marker = None
                if next_marker == None:
                    next_marker = Marker(marker.get_offset_begin(),
                                         marker.get_offset_end(),
                                         marker.get_type())

        if region_id == None:
            next_code_marker_start = 0
            for marker in self.markers:
                if Marker.T.CODE & filter_group and next_code_marker_start < marker.get_offset_begin():
                    yield Marker(next_code_marker_start, marker.get_offset_begin(), Marker.T.CODE)
                if marker.group & filter_group:
                    yield marker
                next_code_marker_start = marker.get_offset_end()
            if Marker.T.CODE & filter_group and next_code_marker_start < len(self.get_content()):
                yield Marker(next_code_marker_start, len(self.get_content()), Marker.T.CODE)
            
        else:
            # per region
            region = self.get_region(region_id)
            if region != None:
                
                # code parsers and database know about non-code markers
                # clients want to iterate code as markers as well
                # so, we embed code markers in run-time
                class CodeMarker(Marker):
                    pass
                
                # cache markers for all regions if it does not exist
                if hasattr(region, '_markers_list') == False:
                    # subroutine to populate _markers_list attribute
                    # _markers_list does include code markers
                    def cache_markers_list_rec(data, region_id, marker_start_ind, next_code_marker_start):
                        region = data.get_region(region_id)
                        region._markers_list = []
                        region._first_marker_ind = marker_start_ind
                        #next_code_marker_start = region.get_offset_begin()
                        
                        for sub_id in region.iterate_subregion_ids():
                            subregion = data.get_region(sub_id)
                            # cache all markers before the subregion
                            while len(data.markers) > marker_start_ind and \
                                subregion.get_offset_begin() > data.markers[marker_start_ind].get_offset_begin():
                                    if next_code_marker_start < data.markers[marker_start_ind].get_offset_begin():
                                        # append code markers coming before non-code marker
                                        region._markers_list.append(CodeMarker(next_code_marker_start,
                                                                               data.markers[marker_start_ind].get_offset_begin(),
                                                                               Marker.T.CODE))
                                    next_code_marker_start = data.markers[marker_start_ind].get_offset_end()
                                    region._markers_list.append(marker_start_ind)
                                    marker_start_ind += 1
                                    
                            # cache all code markers before the subregion but after the last marker
                            if next_code_marker_start < subregion.get_offset_begin():
                                region._markers_list.append(CodeMarker(next_code_marker_start,
                                                                       subregion.get_offset_begin(),
                                                                       Marker.T.CODE))
                            next_code_marker_start = subregion.get_offset_begin()
                                
                            # here is the recursive call for all sub-regions
                            (marker_start_ind, next_code_marker_start) = cache_markers_list_rec(data,
                                                                      sub_id,
                                                                      marker_start_ind,
                                                                      next_code_marker_start)
                            
                        # cache all markers after the last subregion
                        while len(data.markers) > marker_start_ind and \
                            region.get_offset_end() > data.markers[marker_start_ind].get_offset_begin():
                                # append code markers coming before non-code marker
                                if next_code_marker_start < data.markers[marker_start_ind].get_offset_begin():
                                    region._markers_list.append(CodeMarker(next_code_marker_start,
                                                                           data.markers[marker_start_ind].get_offset_begin(),
                                                                           Marker.T.CODE))
                                next_code_marker_start = data.markers[marker_start_ind].get_offset_end()
                                region._markers_list.append(marker_start_ind)
                                marker_start_ind += 1
                        
                        # cache the last code segment after the last marker
                        if next_code_marker_start < region.get_offset_end():
                            region._markers_list.append(CodeMarker(next_code_marker_start,
                                                                   region.get_offset_end(),
                                                                   Marker.T.CODE))
                        next_code_marker_start = region.get_offset_end()
                        
                        # return the starting point for the next call of this function
                        return (marker_start_ind, next_code_marker_start)
                    
                    # append markers list to all regions recursively
                    (next_marker_pos, next_code_marker_start) = cache_markers_list_rec(self, 1, 0, 0)
                    assert(next_marker_pos == len(self.markers))
                
                # excluding subregions
                if exclude_children == True:
                    for marker_ind in region._markers_list:
                        if isinstance(marker_ind, int):
                            marker = self.markers[marker_ind]
                        else:
                            marker = marker_ind # CodeMarker
                        if marker.group & filter_group:
                            yield marker
                            
                            
                # including subregions
                else:
                    next_code_marker_start = region.get_offset_begin()
                    for marker in self.markers[region._first_marker_ind:]:
                        if marker.get_offset_begin() >= region.get_offset_end():
                            break
                        if region.get_offset_begin() > marker.get_offset_begin():
                            continue
                        if Marker.T.CODE & filter_group and next_code_marker_start < marker.get_offset_begin():
                            yield Marker(next_code_marker_start, marker.get_offset_begin(), Marker.T.CODE)
                        if marker.group & filter_group:
                            yield marker
                        next_code_marker_start = marker.get_offset_end()
                    if Marker.T.CODE & filter_group and next_code_marker_start < region.get_offset_end():
                        yield Marker(next_code_marker_start, region.get_offset_end(), Marker.T.CODE)

    def get_marker_types(self):
        return Marker.T

    def are_markers_loaded(self):
        return self.markers != None

    def __repr__(self):
        return Data.__repr__(self) + " and regions " + self.regions.__repr__()

class AggregatedData(Data):
    
    def __init__(self, loader, path):
        Data.__init__(self)
        self.path = path
        self.loader = loader
        self.subdirs = None
        self.subfiles = None
        
    def get_subdirs(self):
        if self.subdirs != None:
            return self.subdirs
        self.subdirs = []
        if self.path != None:
            for subdir in self.loader.db.iterate_dircontent(self.path, include_subdirs = True, include_subfiles = False):
                self.subdirs.append(subdir)
        return self.subdirs
    
    def get_subfiles(self):
        if self.subfiles != None:
            return self.subfiles
        self.subfiles = []
        if self.path != None:
            for subfile in self.loader.db.iterate_dircontent(self.path, include_subdirs = False, include_subfiles = True):
                self.subfiles.append(subfile)
        return self.subfiles


class SelectData(Data):

    def __init__(self, loader, path, file_id, region_id):
        Data.__init__(self)
        self.loader = loader
        self.path = path
        self.file_id = file_id
        self.region_id = region_id
        self.region = None
    
    def get_path(self):
        return self.path
    
    def get_region(self):
        if self.region == None and self.region_id != None:
            row = self.loader.db.get_region(self.file_id, self.region_id)
            if row != None:
                self.region = FileRegionData(self.loader,
                                             self.file_id,
                                             self.region_id,
                                             row.name,
                                             row.begin,
                                             row.end,
                                             row.line_begin,
                                             row.line_end,
                                             row.cursor,
                                             row.group,
                                             row.checksum)
        return self.region


class DiffData(Data):
    
    def __init__(self, new_data, old_data):
        Data.__init__(self)
        self.new_data = new_data
        self.old_data = old_data
    
    def get_data(self, namespace, field):
        new_data = self.new_data.get_data(namespace, field)
        old_data = self.old_data.get_data(namespace, field)
        if new_data == None:
            return None
        if old_data == None:
            # non_zero fields has got zero value by default if missed
            # the data can be also unavailable,
            # because previous collection does not include that
            # but external tools (like limit.py) should warn about this,
            # using list of registered database properties
            old_data = 0
        return new_data - old_data

####################################
# Packager Interface
####################################

class PackagerError(Exception):
    def __init__(self):
        Exception.__init__(self, "Failed to pack or unpack.")

class PackagerFactory(object):

    def create(self, python_type, non_zero):
        if python_type == None:
            return PackagerFactory.SkipPackager()
        if python_type == int:
            if non_zero == False:
                return PackagerFactory.IntPackager()
            else:
                return PackagerFactory.IntNonZeroPackager()
        if python_type == float and non_zero == False:
            return PackagerFactory.FloatPackager()
        if python_type == str:
            return PackagerFactory.StringPackager()
        
        class PackagerFactoryError(Exception):
            def __init__(self, python_type):
                Exception.__init__(self, "Python type '" + str(python_type) + "' is not supported by the factory.")
        raise PackagerFactoryError(python_type)
    
    def get_python_type(self, sql_type):
        if sql_type == "integer":
            return int
        if sql_type == "real":
            return float
        if sql_type == "text":
            return str

        class PackagerFactoryError(Exception):
            def __init__(self, sql_type):
                Exception.__init__(self, "SQL type '" + str(sql_type) + "' is not supported by the factory.")
        raise PackagerFactoryError(sql_type)

    class IPackager(object):
        def pack(self, unpacked_data):
            raise core.api.InterfaceNotImplemented(self)
        def unpack(self, packed_data):
            raise core.api.InterfaceNotImplemented(self)
        def get_sql_type(self):
            raise core.api.InterfaceNotImplemented(self)
        def get_python_type(self):
            raise core.api.InterfaceNotImplemented(self)
        def is_non_zero(self):
            return False
        
    class IntPackager(IPackager):
        def pack(self, unpacked_data):
            if not isinstance(unpacked_data, int):
                raise PackagerError()
            return str(unpacked_data)
            
        def unpack(self, packed_data): 
            try:
                return int(packed_data)
            except ValueError:
                raise PackagerError()
    
        def get_sql_type(self):
            return "integer"
        
        def get_python_type(self):
            return int
    
    class IntNonZeroPackager(IntPackager):
        def pack(self, unpacked_data):
            if unpacked_data == 0:
                raise PackagerError()
            return PackagerFactory.IntPackager.pack(self, unpacked_data)
        def is_non_zero(self):
            return True

    class FloatPackager(IPackager):
        def pack(self, unpacked_data):
            if not isinstance(unpacked_data, float):
                raise PackagerError()
            return str(unpacked_data)
            
        def unpack(self, packed_data): 
            try:
                return float(packed_data)
            except ValueError:
                raise PackagerError()
    
        def get_sql_type(self):
            return "real"

        def get_python_type(self):
            return float

    class FloatNonZeroPackager(FloatPackager):
        def pack(self, unpacked_data):
            if unpacked_data == 0:
                raise PackagerError()
            return PackagerFactory.FloatPackager.pack(self, unpacked_data)
        def is_non_zero(self):
            return True

    class StringPackager(IPackager):
        def pack(self, unpacked_data):
            if not isinstance(unpacked_data, str):
                raise PackagerError()
            return str(unpacked_data)
            
        def unpack(self, packed_data): 
            try:
                return str(packed_data)
            except ValueError:
                raise PackagerError()
    
        def get_sql_type(self):
            return "text"

        def get_python_type(self):
            return str
    
    class SkipPackager(IPackager):
        def pack(self, unpacked_data):
            return None
            
        def unpack(self, packed_data): 
            return None
    
        def get_sql_type(self):
            return None
            
        def get_python_type(self):
            return None
            
####################################
# Loader
####################################

class NamespaceError(Exception):
    def __init__(self, namespace, reason):
        Exception.__init__(self, "Namespace '"
                        + namespace 
                        + "': '"
                        + reason
                        + "'")

class FieldError(Exception):
    def __init__(self, field, reason):
        Exception.__init__(self, "Field '"
                    + field 
                    + "': '"
                    + reason
                    + "'")

class Namespace(object):
    
    def __init__(self, db_handle, name, support_regions = False, version='1.0'):
        if not isinstance(name, str):
            raise NamespaceError(name, "name not a string")
        self.name = name
        self.support_regions = support_regions
        self.fields = {}
        self.db = db_handle
        
        if self.db.check_table(name) == False:        
            self.db.create_table(name, support_regions, version)
        else:
            for column in self.db.iterate_columns(name):
                self.add_field(column.name, PackagerFactory().get_python_type(column.sql_type), non_zero=column.non_zero)
        
    def get_name(self):
        return self.name

    def are_regions_supported(self):
        return self.support_regions
    
    def add_field(self, field_name, python_type, non_zero=False):
        if not isinstance(field_name, str):
            raise FieldError(field_name, "field_name not a string")
        packager = PackagerFactory().create(python_type, non_zero)
        if field_name in self.fields.keys():
            raise FieldError(field_name, "double used")
        self.fields[field_name] = packager
        
        if self.db.check_column(self.get_name(), field_name) == False:        
            # - False if cloned
            # - True if created
            return self.db.create_column(self.name, field_name, packager.get_sql_type(), non_zero=non_zero)
        return None # if double request
    
    def iterate_field_names(self):
        for name in self.fields.keys():
            yield name
    
    def get_field_packager(self, field_name):
        if field_name in self.fields.keys():
            return self.fields[field_name]
        else:
            return None
        
    def get_field_sql_type(self, field_name):
        return self.get_field_packager(field_name).get_sql_type()

    def get_field_python_type(self, field_name):
        return self.get_field_packager(field_name).get_python_type()
    
class DataNotPackable(Exception):
    def __init__(self, namespace, field, value, packager, extra_message):
        Exception.__init__(self, "Data '"
                           + str(value)
                           + "' of type "
                           + str(value.__class__) 
                           + " referred by '"
                           + namespace
                           + "=>"
                           + field
                           + "' is not packable by registered packager '"
                           + str(packager.__class__)
                           + "': " + extra_message)

class Loader(object):
    
    def __init__(self):
        self.namespaces = {}
        self.db = None
        self.last_file_data = None # for performance boost reasons
    
    def create_database(self, dbfile, previous_db = None):
        self.db = core.db.sqlite.Database()
        if os.path.exists(dbfile):
            logging.warn("Removing existing file: " + dbfile)
            # TODO can reuse existing db file to speed up the processing?
            # TODO add option to choose to remove or to overwrite?
            os.unlink(dbfile)
        if previous_db != None and os.path.exists(previous_db) == False:
            raise core.api.ExitError(None, "Database file '" + previous_db + "'  does not exist")

        self.db.create(dbfile, clone_from=previous_db)
        
    def open_database(self, dbfile, read_only = True):
        self.db = core.db.sqlite.Database()
        if os.path.exists(dbfile) == False:
            raise core.api.ExitError(None, "Database file '" + dbfile + "'  does not exist")
        self.db.connect(dbfile, read_only=read_only)
        
        for table in self.db.iterate_tables():
            self.create_namespace(table.name, table.support_regions)
            
    def set_property(self, property_name, value):
        if self.db == None:
            return None
        return self.db.set_property(property_name, value)
    
    def get_property(self, property_name):
        if self.db == None:
            return None
        return self.db.get_property(property_name)

    def iterate_properties(self):
        if self.db == None:
            return None
        return self.db.iterate_properties()
            
    def create_namespace(self, name, support_regions = False, version='1.0'):
        if self.db == None:
            return None
        
        if name in self.namespaces.keys():
            raise NamespaceError(name, "double used")
        new_namespace = Namespace(self.db, name, support_regions, version)
        self.namespaces[name] = new_namespace
        return new_namespace
    
    def iterate_namespace_names(self):
        for name in self.namespaces.keys():
            yield name

    def get_namespace(self, name):
        if name in self.namespaces.keys():
            return self.namespaces[name]
        else:
            return None

    def create_file_data(self, path, checksum, content):
        if self.db == None:
            return None

        (new_id, is_updated) = self.db.create_file(path, checksum)
        result = FileData(self, path, new_id, checksum, content) 
        self.last_file_data = result
        return (result, is_updated)

    def load_file_data(self, path):
        if self.db == None:
            return None

        if self.last_file_data != None and self.last_file_data.get_path() == path:
            return self.last_file_data
        
        data = self.db.get_file(path)
        if data == None:
            return None
        
        result = FileData(self, data.path, data.id, data.checksum, None)
        self.last_file_data = result
        return result

    def save_file_data(self, file_data):
        if self.db == None:
            return None

        class DataIterator(object):

            def iterate_packed_values(self, data, namespace, support_regions = False):
                for each in data.iterate_fields(namespace):
                    space = self.loader.get_namespace(namespace)
                    if space == None:
                        raise DataNotPackable(namespace, each[0], each[1], None, "The namespace has not been found")
                    
                    packager = space.get_field_packager(each[0])
                    if packager == None:
                        raise DataNotPackable(namespace, each[0], each[1], None, "The field has not been found")
        
                    if space.support_regions != support_regions:
                        raise DataNotPackable(namespace, each[0], each[1], packager, "Incompatible support for regions")
                    
                    try:
                        packed_data = packager.pack(each[1])
                        if packed_data == None:
                            continue
                    except PackagerError:
                        raise DataNotPackable(namespace, each[0], each[1], packager, "Packager raised exception")
                    
                    yield (each[0], packed_data)
            
            def __init__(self, loader, data, namespace, support_regions = False):
                self.loader = loader
                self.iterator = self.iterate_packed_values(data, namespace, support_regions)
    
            def __iter__(self):
                return self.iterator
        
        for namespace in file_data.iterate_namespaces():
            if file_data.is_namespace_updated(namespace) == False:
                continue
            self.db.add_row(namespace,
                            file_data.get_id(),
                            None,
                            DataIterator(self, file_data, namespace))
        
        if file_data.are_regions_loaded():
            for region in file_data.iterate_regions():
                for namespace in region.iterate_namespaces():
                    if region.is_namespace_updated(namespace) == False:
                        continue
                    self.db.add_row(namespace,
                                    file_data.get_id(),
                                    region.get_id(),
                                    DataIterator(self, region, namespace, support_regions = True))

    def iterate_file_data(self, path = None, path_like_filter = "%"):
        if self.db == None:
            return None
        
        final_path_like = path_like_filter
        if path != None:
            if self.db.check_dir(path) == False and self.db.check_file(path) == False:
                return None
            final_path_like = path + path_like_filter

        class FileDataIterator(object):
            def iterate_file_data(self, loader, final_path_like):
                for data in loader.db.iterate_files(path_like=final_path_like):
                    yield FileData(loader, data.path, data.id, data.checksum, None)
            
            def __init__(self, loader, final_path_like):
                self.iterator = self.iterate_file_data(loader, final_path_like)
    
            def __iter__(self):
                return self.iterator

        if self.db == None:
            return None
        return FileDataIterator(self, final_path_like)

    def load_aggregated_data(self, path = None, path_like_filter = "%", namespaces = None):
        if self.db == None:
            return None

        final_path_like = path_like_filter
        if path != None:
            if self.db.check_dir(path) == False and self.db.check_file(path) == False:
                return None
            final_path_like = path + path_like_filter
        
        if namespaces == None:
            namespaces = self.namespaces.keys()
        
        result = AggregatedData(self, path)
        for name in namespaces:
            namespace = self.get_namespace(name)
            data = self.db.aggregate_rows(name, path_like = final_path_like)
            for field in data.keys():
                if namespace.get_field_packager(field).get_python_type() == str:
                    continue
                if namespace.get_field_packager(field).is_non_zero() == True:
                    data[field]['min'] = None
                    data[field]['avg'] = None
                distribution = self.db.count_rows(name, path_like = final_path_like, group_by_column = field)
                data[field]['distribution-bars'] = []
                for each in distribution:
                    if each[0] == None:
                        continue
                    assert(float(data[field]['count'] != 0))
                    data[field]['distribution-bars'].append({'metric': each[0],
                                                             'count': each[1],
                                                             'ratio': round((float(each[1]) / float(data[field]['count'])), 4)})
                result.set_data(name, field, data[field])
        return result
    
    def load_selected_data(self, namespace, fields = None, path = None, path_like_filter = "%", filters = [],
                           sort_by = None, limit_by = None):
        if self.db == None:
            return None
        
        final_path_like = path_like_filter
        if path != None:
            if self.db.check_dir(path) == False and self.db.check_file(path) == False:
                return None
            final_path_like = path + path_like_filter
        
        namespace_obj = self.get_namespace(namespace)
        if namespace_obj == None:
            return None
        
        class SelectDataIterator(object):
        
            def iterate_selected_values(self, loader, namespace_obj, final_path_like, fields, filters, sort_by, limit_by):
                for row in loader.db.select_rows(namespace_obj.get_name(), path_like=final_path_like, filters=filters,
                                                 order_by=sort_by, limit_by=limit_by):
                    region_id = None
                    if namespace_obj.are_regions_supported() == True:
                        region_id = row['region_id']
                    data = SelectData(loader, row['path'], row['id'], region_id)
                    field_names = fields
                    if fields == None:
                        field_names = namespace_obj.iterate_field_names()
                    for field in field_names:
                        data.set_data(namespace, field, row[field])
                    yield data
            
            def __init__(self, loader, namespace_obj, final_path_like, fields, filters, sort_by, limit_by):
                self.iterator = self.iterate_selected_values(loader, namespace_obj, final_path_like, fields, filters, sort_by, limit_by)
    
            def __iter__(self):
                return self.iterator

        return SelectDataIterator(self, namespace_obj, final_path_like, fields, filters, sort_by, limit_by)
    