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

    def set_version(self, version):
        self.version = version

    def get_version(self):
        if hasattr(self, 'version') == False:
            return None
        return self.version

    def set_plugin_loader(self, loader):
        self.plugin_loader = loader

    def get_plugin_loader(self):
        if hasattr(self, 'plugin_loader') == False:
            return None
        return self.plugin_loader

class Plugin(BasePlugin):

    class Field(object):
        def __init__(self, name, ftype, non_zero=False):
            self.name = name
            self.type = ftype
            self.non_zero = non_zero

    class Property(object):
        def __init__(self, name, value):
            self.name = name
            self.value = value
    
    def initialize(self, namespace=None, support_regions=True, fields=[], properties=[]):
        super(Plugin, self).initialize()
        
        if hasattr(self, 'is_updated') == False:
            self.is_updated = False # original initialization
            
        db_loader = self.get_plugin_loader().get_database_loader()
        
        if namespace == None:
            namespace = self.get_name()

        if (len(fields) != 0 or len(properties) != 0):
            prev_version = db_loader.set_property(self.get_name() + ":version", self.get_version())
            if prev_version != self.get_version():
                self.is_updated = True

        for prop in properties:
            assert(prop.name != 'version')
            prev_prop = db_loader.set_property(self.get_name() + ":" + prop.name, prop.value)
            if prev_prop != prop.value:
                self.is_updated = True

        if len(fields) != 0:
            namespace_obj = db_loader.create_namespace(namespace,
                                                       support_regions=support_regions,
                                                       version=self.get_version())
            for field in fields:
                is_created = namespace_obj.add_field(field.name, field.type, non_zero=field.non_zero)
                assert(is_created != None)
                # if field is created (not cloned from the previous db),
                # mark the plug-in as updated in order to trigger full rescan
                self.is_updated = self.is_updated or is_created

class MetricPlugin(Plugin):
    
    def add_field(self, is_active, field,
                       pattern_to_search,
                       marker_type_mask=Marker.T.ANY,
                       exclude_subregions=True,
                       merge_markers=False):
        if hasattr(self, '_fields') == False:
            self._fields = {}
        if is_active == True:
            self._fields[field.name] = (field,
                                        marker_type_mask,
                                        exclude_subregions,
                                        merge_markers,
                                        pattern_to_search)
            
    def is_active(self, field_name = None):
        if field_name == None:
            return (len(self._fields.keys()) > 0)
        return (field_name in self._fields.keys())
    
    def get_fields(self):
        result = []
        for key in self._fields.keys():
            result.append(self._fields[key][0])
        return result
    
    def count_if_active(self, field_name, data, namespace=None):
        if self.is_active(field_name) == False:
            return
        
        if namespace == None:
            namespace = self.get_name()
            
        field_data = self._fields[field_name]
        text = data.get_content()
        for region in data.iterate_regions():
            count = 0
            for marker in data.iterate_markers(
                            filter_group = field_data[1],
                            region_id = region.get_id(),
                            exclude_children = field_data[2],
                            merge=field_data[3]):
                count += len(field_data[4].findall(text, marker.get_offset_begin(), marker.get_offset_end()))
            region.set_data(namespace, field_name, count)

class InterfaceNotImplemented(Exception):
    def __init__(self, obj):
        import sys
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

class ITool(object):
    def run(self, tool_args):
        raise InterfaceNotImplemented(self)

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
        self.get_plugin_loader().get_plugin(parent_name).subscribe(self, callback_name)
    
    def subscribe_by_parents_interface(self, interface, callback_name='callback'):
        for plugin in self.get_plugin_loader().iterate_plugins():
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

# TODO re-factor and remove this
class ExitError(Exception):
    def __init__(self, plugin, reason):
        if plugin != None:
            Exception.__init__(self, "Plugin '"
                               + plugin.get_name()
                               + "' requested abnormal termination: "
                               + reason)
        else:
            Exception.__init__(self, "'Abnormal termination requested: "
                               + reason)
            




