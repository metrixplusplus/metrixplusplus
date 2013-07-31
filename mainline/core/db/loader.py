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

from core.api import Data, FileRegionData, Marker, FileData

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
    