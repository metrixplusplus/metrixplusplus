#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

from metrixpp.mpp import api

import os
import sys
try:
    from configparser import ConfigParser
except:
    from ConfigParser import ConfigParser
  
import re
import optparse

class MultiOptionParser(optparse.OptionParser):
    
    class MultipleOption(optparse.Option):
        ACTIONS = optparse.Option.ACTIONS + ("multiopt",)
        STORE_ACTIONS = optparse.Option.STORE_ACTIONS + ("multiopt",)
        TYPED_ACTIONS = optparse.Option.TYPED_ACTIONS + ("multiopt",)
        ALWAYS_TYPED_ACTIONS = optparse.Option.ALWAYS_TYPED_ACTIONS + ("multiopt",)
    
        def take_action(self, action, dest, opt, value, values, parser):
            if action == "multiopt":
                values.ensure_value(dest, []).append(value)
            else:
                optparse.Option.take_action(self, action, dest, opt, value, values, parser)

    
    def __init__(self, *args, **kwargs):
        optparse.OptionParser.__init__(self, *args, option_class=self.MultipleOption, **kwargs)

class Loader(object):

    def __init__(self):
        self.plugins = []
        self.hash    = {}
        self.action = None
    
    def get_action(self):
        return self.action
    
    def get_plugin(self, name):
        return self.hash[name]['instance']
    
    def iterate_plugins(self, is_reversed = False):
        if is_reversed == False:
            for item in self.plugins:
                yield item['instance']
        else:
            for item in reversed(self.plugins):
                yield item['instance']
            
    def load(self, command, directories, args):

        class IniContainer(object):
            def __init__(self):
                self.plugins = []
                self.actions = []
                self.hash    = {}

        def load_plugin_config(inicontainer, fname):
            active_plugins = []
            config = ConfigParser()
            config.read(fname)
            item = {'package': config.get('Plugin', 'package'),
                    'module': config.get('Plugin', 'module'),
                    'class': config.get('Plugin', 'class'),
                    'version': config.get('Plugin', 'version'),
                    'depends': config.get('Plugin', 'depends'),
                    'actions': config.get('Plugin', 'actions'),
                    'enabled': config.getboolean('Plugin', 'enabled'),
                    'instance': None}
            if item['enabled']:
                item['actions'] = item['actions'].split(',')
                for (ind, action) in enumerate(item['actions']):
                    action = action.strip()
                    item['actions'][ind] = action
                    if action not in inicontainer.actions + ['*', 'None', 'none', 'False', 'false']:
                        inicontainer.actions.append(action)
                    if action == '*' or action == command:
                        active_plugins.append(item['package'] + '.' + item['module'])
                inicontainer.plugins.append(item)
                inicontainer.hash[item['package'] + '.' + item['module']] = item
            return active_plugins

        def load_recursively(inicontainer, directory):
            active_plugins = []
            if os.path.exists(directory) == False or os.path.isdir(directory) == False:
                return active_plugins

            pattern = re.compile(r'.*[.]ini$', flags=re.IGNORECASE)
            dirList = sorted(os.listdir(directory))
            for fname in dirList:
                fname = os.path.join(directory, fname)
                if os.path.isdir(fname):
                    active_plugins += load_recursively(inicontainer, fname)
                elif re.match(pattern, fname):
                    active_plugins += load_plugin_config(inicontainer, fname)
            return active_plugins
                        
        def list_dependants_recursively(inicontainer, required_plugin_name):
            assert required_plugin_name in list(inicontainer.hash.keys()), \
                "depends section requires unknown plugin: " + required_plugin_name
            item = inicontainer.hash[required_plugin_name]
            if item['depends'] in ('None', 'none', 'False', 'false'):
                return []
            result = []
            for child in item['depends'].split(','):
                child = child.strip()
                result += list_dependants_recursively(inicontainer, child)
                result.append(child)
            return result

        # configure python path for loading
        std_ext_dir = os.path.join(os.environ['METRIXPLUSPLUS_INSTALL_DIR'], 'ext')
        std_ext_priority_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for each in [std_ext_dir] + directories:
            sys.path.append(each)

        inicontainer = IniContainer()
        # load available plugin ini files
        required_plugins = []
        for each in ([std_ext_priority_dir, std_ext_dir] + directories):
            required_plugins += load_recursively(inicontainer, each)

        # append the tests dir if it exists - not on the pypi packet
        tests_dir = os.path.join(os.environ['METRIXPLUSPLUS_INSTALL_DIR'], 'tests')
        if os.path.exists(tests_dir):
            sys.path.append(tests_dir)
            required_plugins += load_plugin_config(inicontainer, os.path.join(tests_dir, "test.ini"))
        
        required_plugins.sort();    # sort the plugin list to get similar results independant of the os
            
        # upgrade the list of required plugins
        required_and_dependant_plugins = []
        for name in required_plugins:
            for each in list_dependants_recursively(inicontainer, name):
                if each not in required_and_dependant_plugins:
                    required_and_dependant_plugins.append(each)
            if name not in required_and_dependant_plugins:
                required_and_dependant_plugins.append(name)
            
        # load
        for plugin_name in required_and_dependant_plugins:
            item = inicontainer.hash[plugin_name]
            plugin = __import__(item['package'], globals(), locals(), [str(item['module'])])
            module_attr = plugin.__getattribute__(item['module'])
            class_attr = module_attr.__getattribute__(item['class'])
            item['instance'] = class_attr.__new__(class_attr)
            item['instance'].__init__()
            item['instance'].set_name(item['package'] + "." + item['module'])
            item['instance'].set_version(item['version'])
            item['instance']._set_plugin_loader(self)
            self.plugins.append(item)
            self.hash[plugin_name] = item

        optparser = MultiOptionParser(
            usage = "Usage: python %prog --help\n" +
                    "       python %prog <action> --help\n" +
                    "       python %prog <action> [options] -- [path 1] ... [path N]\n" +
                    "\n" +
                    "Actions: \n  " + "\n  ".join(sorted(inicontainer.actions)))
        if command in ['--help', '--h', '-h']:
            optparser.print_help()
            exit(0)
        if command.strip() == "":
            optparser.error("Mandatory action argument required")
        if command not in inicontainer.actions:
            optparser.error("action {action}: Unknown command".format(action=command))

        self.action = command

        optparser = MultiOptionParser(
            usage="Usage: python %prog --help\n"
                  "       python %prog {command} --help\n"
                  "       python %prog {command} [options] -- [path 1] ... [path N]".format(command=command))

        for item in self.iterate_plugins():
            if (isinstance(item, api.IConfigurable)):
                item.declare_configuration(optparser)

        (options, args) = optparser.parse_args(args)
        for item in self.iterate_plugins():
            if (isinstance(item, api.IConfigurable)):
                item.configure(options)

        for item in self.iterate_plugins():
            item.initialize()
            
        return args

    def unload(self):
        for item in self.iterate_plugins(is_reversed = True):
            item.terminate()

    def run(self, args):
        exit_code = 0
        for item in self.iterate_plugins():
            if (isinstance(item, api.IRunable)):
                exit_code += item.run(args)
        return exit_code

    def __repr__(self):
        result = object.__repr__(self) + ' with loaded:'
        for item in self.iterate_plugins():
            result += '\n\t' + item.__repr__()
            if isinstance(item, api.Parent):
                result += ' with subscribed:'
                for child in item.iterate_children():
                    result += '\n\t\t' + child.__repr__()
        return result

