'''
Created on 25/07/2012

@author: konstaa
'''

class Plugin(object):
    
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

    def set_plugin_loader(self, loader):
        self.plugin_loader = loader

    def get_plugin_loader(self):
        if hasattr(self, 'plugin_loader') == False:
            return None
        return self.plugin_loader

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

class ExitError(Exception):
    def __init__(self, plugin, reason):
        Exception.__init__(self, "Plugin '"
                           + plugin.get_name()
                           + "' requested abnormal termination: "
                           + reason)

def subscribe_by_parents_name(parent_name, child, callback_name='callback'):
    child.get_plugin_loader().get_plugin(parent_name).subscribe(child, callback_name)


# interfaces for subscription
class ICode(object):
    pass

def subscribe_by_parents_interface(interface, child, callback_name='callback'):
    for plugin in child.get_plugin_loader().iterate_plugins():
        if isinstance(plugin, interface):
            plugin.subscribe(child, callback_name)




