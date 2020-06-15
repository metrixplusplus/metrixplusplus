#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

class PackagerError(Exception):
    def __init__(self, message=None):
        if message == None:
            Exception.__init__(self, "Failed to pack or unpack.")
        else:
            Exception.__init__(self, message)

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
            assert False, "Internal interface not implemented"
        def unpack(self, packed_data):
            assert False, "Internal interface not implemented"
        def get_sql_type(self):
            assert False, "Internal interface not implemented"
        def get_python_type(self):
            assert False, "Internal interface not implemented"
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
            try:
                return str(unpacked_data)
            except ValueError:
                raise PackagerError()
            
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
