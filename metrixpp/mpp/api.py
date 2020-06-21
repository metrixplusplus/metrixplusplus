#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

import os.path
import sys

from metrixpp.mpp.internal import dbwrap
from metrixpp.mpp.internal import api_impl

class InterfaceNotImplemented(Exception):
    def __init__(self, obj):
        Exception.__init__(self, "Method '"
                            + sys._getframe(1).f_code.co_name
                            + "' has not been implemented for "
                            + str(obj.__class__))

class IConfigurable(object):
    def configure(self, options):
        raise InterfaceNotImplemented(self)
    def declare_configuration(self, optparser):
        raise InterfaceNotImplemented(self)

class IRunable(object):
    def run(self, args):
        raise InterfaceNotImplemented(self)
    
class IParser(object):
    def process(self, parent, data, is_updated):
        raise InterfaceNotImplemented(self)

class ICode(object):
    pass

class CallbackNotImplemented(Exception):
    
    def __init__(self, obj, callback_name):
        Exception.__init__(self, "Callback '"
                           + callback_name
                           + "' has not been implemented for "
                           + str(obj.__class__))

class Child(object):
    
    def notify(self, parent, callback_name, *args):
        if hasattr(self, callback_name) == False:
            raise CallbackNotImplemented(self, callback_name)
        self.__getattribute__(callback_name)(parent, *args)

    def subscribe_by_parents_name(self, parent_name, callback_name='callback'):
        self.get_plugin(parent_name).subscribe(self, callback_name)
    
    def subscribe_by_parents_names(self, parent_names, callback_name='callback'):
        for parent_name in parent_names:
            self.get_plugin(parent_name).subscribe(self, callback_name)

    def subscribe_by_parents_interface(self, interface, callback_name='callback'):
        for plugin in self._get_plugin_loader().iterate_plugins():
            if isinstance(plugin, interface):
                plugin.subscribe(self, callback_name)


class Parent(object):
    
    def init_Parent(self):
        if hasattr(self, 'children') == False:
            self.children = []
            
    def subscribe(self, obj, callback_name):
        self.init_Parent()
        if (isinstance(obj, Child) == False):
            raise TypeError()
        self.children.append((obj,callback_name))

    def unsubscribe(self, obj, callback_name):
        self.init_Parent()
        self.children.remove((obj, callback_name))

    def notify_children(self, *args):
        self.init_Parent()
        for child in self.children:
            child[0].notify(self, child[1], *args)

    def iterate_children(self):
        self.init_Parent()
        for child in self.children:
            yield child

##############################################################################
#
# 
#
##############################################################################

class Data(object):

    def __init__(self):
        self.data = {}
        
    def get_data(self, namespace, field):
        if namespace not in list(self.data.keys()):
            return None
        if field not in list(self.data[namespace].keys()):
            return None
        return self.data[namespace][field]

    def set_data(self, namespace, field, value):
        if namespace not in self.data:
            self.data[namespace] = {}
        self.data[namespace][field] = value

    def iterate_namespaces(self):
        for namespace in list(self.data.keys()):
            yield namespace
            
    def iterate_fields(self, namespace):
        for field in list(self.data[namespace].keys()):
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
        namespace_obj = self.loader.get_namespace(namespace)
        if namespace_obj == None:
            return
        regions_supported = namespace_obj.are_regions_supported()
        if ((self.region_id == None and regions_supported == True) or 
            (self.region_id != None and regions_supported == False)):
            return
        row = self.loader.db.get_row(namespace, self.file_id, self.region_id)
        if row == None:
            return
        for column_name in list(row.keys()):
            try:
                packager = namespace_obj._get_field_packager(column_name)
            except api_impl.PackagerError:
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
    
class Region(LoadableData):
    
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
            if group == self.ANY:
                return "any"
            result = []
            if group & self.GLOBAL != 0:
                result.append("global")
            if group & self.CLASS != 0:
                result.append("class")
            if group & self.STRUCT != 0:
                result.append("struct")
            if group & self.NAMESPACE != 0:
                result.append("namespace")
            if group & self.FUNCTION != 0:
                result.append("function")
            if group & self.INTERFACE != 0:
                result.append("interface")
            assert(len(result) != 0)
            return ', '.join(result)

        def from_str(self, group):
            if group == "global":
                return self.GLOBAL
            elif group == "class":
                return self.CLASS
            elif group == "struct":
                return self.STRUCT
            elif group == "namespace":
                return self.NAMESPACE
            elif group == "function":
                return self.FUNCTION
            elif group == "interface":
                return self.INTERFACE
            elif group == "any":
                return self.ANY
            else:
                return None

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
    
    def iterate_subregion_ids(self):
        return self.children

    def _register_subregion_id(self, child_id):
        self.children.append(child_id)
        
class Marker(object):
    class T(object):
        NONE            = 0x00
        COMMENT         = 0x01
        STRING          = 0x02
        PREPROCESSOR    = 0x04
        CODE            = 0x08
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
    
    def get_content(self):
        return self.content

    def _internal_append_region(self, region):
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
            self.get_region(prev_id)._register_subregion_id(region.get_id())
        self.regions.append(region)

    def load_regions(self):
        if self.regions == None:
            self.regions = []
            for each in self.loader.db.iterate_regions(self.get_id()):
                self._internal_append_region(Region(self.loader,
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
            # # do not load regions and markers in time of collection
            # if region is added first by parser, set markers to empty list as well
            # because if there are no markers in a file, it forces loading of markers
            # during iterate_markers call
            self.regions = []
            self.markers = []
        new_id = len(self.regions) + 1
        self._internal_append_region(Region(self.loader, self.get_id(), new_id, region_name, offset_begin, offset_end, line_begin, line_end, cursor_line, group, checksum))
        self.loader.db.create_region(self.file_id, new_id, region_name, offset_begin, offset_end, line_begin, line_end, cursor_line, group, checksum)
        return new_id
        
    def get_region(self, region_id):
        self.load_regions()
        return self.regions[region_id - 1]
    
    def iterate_regions(self, filter_group = Region.T.ANY, region_id = None):
        self.load_regions()
        if region_id == None:
            for each in self.regions:
                if each.group & filter_group:
                    yield each
        else:
            for sub_id in self.get_region(region_id).iterate_subregion_ids():
                each = self.get_region(sub_id)
                if each.group & filter_group:
                    yield each

    def are_regions_loaded(self):
        return self.regions != None

    def load_markers(self):
        if self.markers == None:
            # TODO add assert in case of an attempt to load data during collection
            assert(False) # TODO not used in post-processing tools for while, need to be fixed
            self.markers = []
            for each in self.loader.db.iterate_markers(self.get_id()):
                self.markers.append(Marker(each.begin, each.end, each.group))
        
    def add_marker(self, offset_begin, offset_end, group):
        if self.markers == None:
            # # do not load regions and markers in time of collection
            # if marker is added first by parser, set regions to empty list as well
            # because if there are no regions in a file, it forces loading of regions
            # during iterate_regions call
            self.regions = []
            self.markers = []
        self.markers.append(Marker(offset_begin, offset_end, group))
        # TODO drop collecting markers, it is faster to double parse
        # it is not the same with regions, it is faster to load regions
        # on iterative re-run
        #self.loader.db.create_marker(self.file_id, offset_begin, offset_end, group)
        
    def iterate_markers(self, filter_group = Marker.T.ANY,
                         region_id = None, exclude_children = True, merge = False):
        self.load_markers()
        
        # merged markers
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
            if next_marker != None:
                yield next_marker
        
        # all markers per file
        elif region_id == None:
            next_code_marker_start = 0
            for marker in self.markers:
                if Marker.T.CODE & filter_group and next_code_marker_start < marker.get_offset_begin():
                    yield Marker(next_code_marker_start, marker.get_offset_begin(), Marker.T.CODE)
                if marker.group & filter_group:
                    yield marker
                next_code_marker_start = marker.get_offset_end()
            if Marker.T.CODE & filter_group and next_code_marker_start < len(self.get_content()):
                yield Marker(next_code_marker_start, len(self.get_content()), Marker.T.CODE)

        # markers per region
        else:
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
                self.region = Region(self.loader,
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
# Loader
####################################

class Namespace(object):
    
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

    def __init__(self, db_handle, name, support_regions = False, version='1.0'):
        if not isinstance(name, str):
            raise Namespace.NamespaceError(name, "name not a string")
        self.name = name
        self.support_regions = support_regions
        self.fields = {}
        self.db = db_handle
        
        if self.db.check_table(name) == False:        
            self.db.create_table(name, support_regions, version)
        else:
            for column in self.db.iterate_columns(name):
                self.add_field(column.name,
                               api_impl.PackagerFactory().get_python_type(column.sql_type),
                               non_zero=column.non_zero)
        
    def get_name(self):
        return self.name

    def are_regions_supported(self):
        return self.support_regions
    
    def add_field(self, field_name, python_type, non_zero=False):
        if not isinstance(field_name, str):
            raise Namespace.FieldError(field_name, "field_name not a string")
        packager = api_impl.PackagerFactory().create(python_type, non_zero)
        if field_name in list(self.fields.keys()):
            raise Namespace.FieldError(field_name, "double used")
        self.fields[field_name] = packager
        
        if self.db.check_column(self.get_name(), field_name) == False:        
            # - False if cloned
            # - True if created
            return self.db.create_column(self.name, field_name, packager.get_sql_type(), non_zero=non_zero)
        return None # if double request
    
    def iterate_field_names(self):
        for name in list(self.fields.keys()):
            yield name
    
    def check_field(self, field_name):
        try:
            self._get_field_packager(field_name)
        except api_impl.PackagerError:
            return False
        return True

    def get_field_sql_type(self, field_name):
        try:
            return self._get_field_packager(field_name).get_sql_type()
        except api_impl.PackagerError:
            raise Namespace.FieldError(field_name, 'does not exist')

    def get_field_python_type(self, field_name):
        try:
            return self._get_field_packager(field_name).get_python_type()
        except api_impl.PackagerError:
            raise Namespace.FieldError(field_name, 'does not exist')


    def is_field_non_zero(self, field_name):
        try:
            return self._get_field_packager(field_name).is_non_zero()
        except api_impl.PackagerError:
            raise Namespace.FieldError(field_name, 'does not exist')

    def _get_field_packager(self, field_name):
        if field_name in list(self.fields.keys()):
            return self.fields[field_name]
        else:
            raise api_impl.PackagerError("unknown field " + field_name + " requested")
    
class Loader(object):
    
    def __init__(self):
        self.namespaces = {}
        self.db = None
        self.last_file_data = None # for performance boost reasons
    
    def create_database(self, dbfile, previous_db = None):
        self.db = dbwrap.Database()
        try:
            self.db.create(dbfile, clone_from=previous_db)
        except:
            return False
        return True
        
    def open_database(self, dbfile, read_only = True):
        self.db = dbwrap.Database()
        if os.path.exists(dbfile) == False:
            return False
        try:
            self.db.connect(dbfile, read_only=read_only)
        except:
            return False
        
        for table in self.db.iterate_tables():
            self.create_namespace(table.name, table.support_regions)

        return True

    def set_property(self, property_name, value):
        if self.db == None:
            return None
        return self.db.set_property(property_name, str(value))
    
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
        
        if name in list(self.namespaces.keys()):
            raise Namespace.NamespaceError(name, "double used")
        new_namespace = Namespace(self.db, str(name), support_regions, version)
        self.namespaces[name] = new_namespace
        return new_namespace
    
    def iterate_namespace_names(self):
        for name in list(self.namespaces.keys()):
            yield name

    def get_namespace(self, name):
        if name in list(self.namespaces.keys()):
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

    def save_file_data(self, file_data):
        if self.db == None:
            return None

        class DataIterator(object):

            def iterate_packed_values(self, data, namespace, support_regions = False):
                for each in data.iterate_fields(namespace):
                    space = self.loader.get_namespace(namespace)
                    if space == None:
                        raise Loader.DataNotPackable(namespace, each[0], each[1], None, "The namespace has not been found")
                    
                    try:
                        packager = space._get_field_packager(each[0])
                    except api_impl.PackagerError:
                        raise Loader.DataNotPackable(namespace, each[0], each[1], None, "The field has not been found")
        
                    if space.support_regions != support_regions:
                        raise Loader.DataNotPackable(namespace, each[0], each[1], packager, "Incompatible support for regions")
                    
                    try:
                        packed_data = packager.pack(each[1])
                        if packed_data == None:
                            continue
                    except api_impl.PackagerError:
                        raise Loader.DataNotPackable(namespace, each[0], each[1], packager, "Packager raised exception")
                    
                    yield (each[0], packed_data)
            
            def __init__(self, loader, data, namespace, support_regions = False):
                self.loader = loader
                self.iterator = self.iterate_packed_values(data, namespace, support_regions)
    
            def __iter__(self):
                return self.iterator
        
        # TODO can construct to add multiple rows at one sql query
        # to improve the performance
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
            namespaces = list(self.namespaces.keys())
        
        result = AggregatedData(self, path)
        for name in namespaces:
            namespace = self.get_namespace(name)
            data = self.db.aggregate_rows(name, path_like = final_path_like)
            for field in list(data.keys()):
                if namespace.get_field_python_type(field) == str:
                    continue
                data[field]['nonzero'] = namespace.is_field_non_zero(field)
                distribution = self.db.count_rows(name, path_like = final_path_like, group_by_column = field)
                data[field]['distribution-bars'] = []
                for each in distribution:
                    if each[0] == None:
                        continue
                    assert(float(data[field]['count'] != 0))
                    data[field]['distribution-bars'].append({'metric': each[0],
                                                             'count': each[1],
                                                             'ratio': (float(each[1]) / float(data[field]['count']))})
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





class BasePlugin(object):
    
    def initialize(self):
        pass

    def terminate(self):
        pass
    
    def set_name(self, name):
        self.name = name

    def get_name(self):
        if hasattr(self, 'name') == False:
            return None
        return self.name

    def get_namespace(self):
        return self.get_name()

    def set_version(self, version):
        self.version = version

    def get_version(self):
        if hasattr(self, 'version') == False:
            return None
        return self.version

    def _set_plugin_loader(self, loader):
        self.plugin_loader = loader

    def _get_plugin_loader(self):
        if hasattr(self, 'plugin_loader') == False:
            return None
        return self.plugin_loader
    
    def get_plugin(self, plugin_name):
        return self._get_plugin_loader().get_plugin(plugin_name)

    def get_action(self):
        return self._get_plugin_loader().get_action()

class Plugin(BasePlugin):

    class Field(object):
        def __init__(self, name, ftype, non_zero=False):
            self.name = name
            self.type = ftype
            self.non_zero = non_zero
            self._regions_supported = True

    class Property(object):
        def __init__(self, name, value):
            self.name = name
            self.value = value
    
    def initialize(self, namespace=None, support_regions=True, fields=[], properties=[]):
        super(Plugin, self).initialize()
        
        if hasattr(self, 'is_updated') == False:
            self.is_updated = False # original initialization

        db_loader = self.get_plugin('metrixpp.mpp.dbf').get_loader()

        if namespace == None:
            namespace = self.get_name()

        if (len(fields) != 0 or len(properties) != 0):
            prev_version = db_loader.set_property(self.get_name() + ":version", self.get_version())
            if str(prev_version) != str(self.get_version()):
                self.is_updated = True

        for prop in properties:
            assert(prop.name != 'version')
            prev_prop = db_loader.set_property(self.get_name() + ":" + prop.name, prop.value)
            if str(prev_prop) != str(prop.value):
                self.is_updated = True

        if len(fields) != 0:
            namespace_obj = db_loader.create_namespace(namespace,
                                                       support_regions=support_regions,
                                                       version=self.get_version())
            for field in fields:
                is_created = namespace_obj.add_field(field.name, field.type, non_zero=field.non_zero)
                field._regions_supported = support_regions
                assert(is_created != None)
                # if field is created (not cloned from the previous db),
                # mark the plug-in as updated in order to trigger full rescan
                self.is_updated = self.is_updated or is_created

class MetricPluginMixin(Parent):

    class AliasError(Exception):
        def __init__(self, alias):
            Exception.__init__(self, "Unknown pattern alias: " + str(alias))
            
    class PlainCounter(object):
        
        def __init__(self, namespace, field, plugin, alias, data, region):
            self.namespace = namespace
            self.field = field
            self.plugin = plugin
            self.alias = alias
            self.data = data
            self.region = region
            self.result = 0
            
        def count(self, marker, pattern_to_search):
            self.result += len(pattern_to_search.findall(self.data.get_content(),
                                                       marker.get_offset_begin(),
                                                       marker.get_offset_end()))
        
        def get_result(self):
            return self.result

    class IterIncrementCounter(PlainCounter):
        
        def count(self, marker, pattern_to_search):
            self.marker = marker
            self.pattern_to_search = pattern_to_search
            for match in pattern_to_search.finditer(self.data.get_content(),
                                                    marker.get_offset_begin(),
                                                    marker.get_offset_end()):
                self.result += self.increment(match)
        
        def increment(self, match):
            return 1

    class IterAssignCounter(PlainCounter):
        
        def count(self, marker, pattern_to_search):
            self.marker = marker
            self.pattern_to_search = pattern_to_search
            for match in pattern_to_search.finditer(self.data.get_content(),
                                                    marker.get_offset_begin(),
                                                    marker.get_offset_end()):
                self.result = self.assign(match)
        
        def assign(self, match):
            return self.result

    class RankedCounter(PlainCounter):
        
        def __init__(self, *args, **kwargs):
            super(MetricPluginMixin.RankedCounter, self).__init__(*args, **kwargs)
            self.result = self.region.get_data(self.namespace, self.field)
            if self.result == None:
                self.result = 1
        
        def get_result(self):
            sourced_metric = self.region.get_data(self.rank_source[0], self.rank_source[1])
            # necessary with python3
            if sourced_metric == None:
                assert(self.region.get_type() != Region.T.FUNCTION);
                assert(self.rank_source == ('std.code.complexity', 'cyclomatic'));
                return None;
            for (ind, range_pair) in enumerate(self.rank_ranges):
                if ((range_pair[0] == None or sourced_metric >= range_pair[0])
                    and
                    (range_pair[1] == None or sourced_metric <= range_pair[1])):
                    self.result = self.result * (ind + 1)
                    break
            return self.result

    def declare_metric(self, is_active, field,
                       pattern_to_search_or_map_of_patterns,
                       marker_type_mask=Marker.T.ANY,
                       region_type_mask=Region.T.ANY,
                       exclude_subregions=True,
                       merge_markers=False):
        if hasattr(self, '_fields') == False:
            self._fields = {}
        
        if isinstance(pattern_to_search_or_map_of_patterns, dict):
            map_of_patterns = pattern_to_search_or_map_of_patterns
        else:
            map_of_patterns = {'*': pattern_to_search_or_map_of_patterns}
        # client may suply with pattern or pair of pattern + counter class
        for key in list(map_of_patterns.keys()):
            if isinstance(map_of_patterns[key], tuple) == False:
                # if it is not a pair, create a pair using default counter class
                map_of_patterns[key] = (map_of_patterns[key],
                                        MetricPluginMixin.PlainCounter)

        if is_active == True:
            self._fields[field.name] = (field,
                                        marker_type_mask,
                                        exclude_subregions,
                                        merge_markers,
                                        map_of_patterns,
                                        region_type_mask)
            
    def is_active(self, metric_name = None):
        if metric_name == None:
            return (len(list(self._fields.keys())) > 0)
        return (metric_name in list(self._fields.keys()))
    
    def get_fields(self):
        result = []
        for key in list(self._fields.keys()):
            result.append(self._fields[key][0])
        return result
    
    def callback(self, parent, data, is_updated):
        # count if metric is enabled, 
        # and (optimization for the case of iterative rescan:)
        # if file is updated or this plugin's settings are updated
        is_updated = is_updated or self.is_updated
        if is_updated == True:
            for field in self.get_fields():
                self.count_if_active(self.get_namespace(),
                                     field.name,
                                     data,
                                     alias=parent.get_name())
        # this mixin implements parent interface
        self.notify_children(data, is_updated)

    def count_if_active(self, namespace, field, data, alias='*'):
        if self.is_active(field) == False:
            return
        
        field_data = self._fields[field]
        if alias not in list(field_data[4].keys()):
            if '*' not in list(field_data[4].keys()):
                raise self.AliasError(alias)
            else:
                alias = '*'
        (pattern_to_search, counter_class) = field_data[4][alias]
        
        if field_data[0]._regions_supported == True:
            for region in data.iterate_regions(filter_group=field_data[5]):
                counter = counter_class(namespace, field, self, alias, data, region)
                if field_data[1] != Marker.T.NONE:
                    for marker in data.iterate_markers(
                                    filter_group = field_data[1],
                                    region_id = region.get_id(),
                                    exclude_children = field_data[2],
                                    merge=field_data[3]):
                        counter.count(marker, pattern_to_search)
                count = counter.get_result()
                if count != 0 or field_data[0].non_zero == False:
                    region.set_data(namespace, field, count)
        else:
            counter = counter_class(namespace, field, self, alias, data, None)
            if field_data[1] != Marker.T.NONE:
                for marker in data.iterate_markers(
                                filter_group = field_data[1],
                                region_id = None,
                                exclude_children = field_data[2],
                                merge=field_data[3]):
                    counter.count(marker, pattern_to_search)
            count = counter.get_result()
            if count != 0 or field_data[0].non_zero == False:
                data.set_data(namespace, field, count)
            



