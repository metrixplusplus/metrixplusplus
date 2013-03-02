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

import core.api
import core.db.loader

import os
import fnmatch

class Loader(object):

    def __init__(self):
        self.plugins = []
        self.parsers = []
        self.hash    = {}
        self.exit_code = 0
        self.db = core.db.loader.Loader()
        
    def get_database_loader(self):
        return self.db

    def get_plugin(self, name):
        return self.hash[name]['instance']
    
    def iterate_plugins(self, is_reversed = False):
        if is_reversed == False:
            for item in self.plugins:
                yield item['instance']
        else:
            for item in reversed(self.plugins):
                yield item['instance']
            
    def register_parser(self, fnmatch_exp_list, parser):
        self.parsers.append((fnmatch_exp_list, parser))

    def get_parser(self, file_path):
        for parser in self.parsers:
            for fnmatch_exp in parser[0]:
                if fnmatch.fnmatch(file_path, fnmatch_exp):
                    return parser[1]
        return None

    def load(self, directory, optparser, args):
        import sys
        sys.path.append(directory)
        
        def load_recursively(manager, directory):
            import ConfigParser
            import re
        
            pattern = re.compile(r'.*[.]ini$', flags=re.IGNORECASE)
        
            dirList = os.listdir(directory)
            for fname in dirList:
                fname = os.path.join(directory, fname)
                if os.path.isdir(fname):
                    load_recursively(manager, fname)
                elif re.match(pattern, fname):
                    config = ConfigParser.ConfigParser()
                    config.read(fname)
                    item = {'package': config.get('Plugin', 'package'),
                            'module': config.get('Plugin', 'module'),
                            'class': config.get('Plugin', 'class'),
                            'version': config.get('Plugin', 'version'),
                            'depends': config.get('Plugin', 'depends'),
                            'enabled': config.getboolean('Plugin', 'enabled')}
                    if item['enabled']:
                        manager.plugins.append(item)
                        manager.hash[item['package'] + '.' + item['module']] = item

        load_recursively(self, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ext-priority'))
        load_recursively(self, directory)
        # TODO check dependencies
        for item in self.plugins:
            plugin = __import__(item['package'], globals(), locals(), [item['module']], -1)
            module_attr = plugin.__getattribute__(item['module'])
            class_attr = module_attr.__getattribute__(item['class'])
            item['instance'] = class_attr.__new__(class_attr)
            item['instance'].__init__()
            item['instance'].set_name(item['package'] + "." + item['module'])
            item['instance'].set_version(item['version'])
            item['instance'].set_plugin_loader(self)

        for item in self.iterate_plugins():
            if (isinstance(item, core.api.IConfigurable)):
                item.declare_configuration(optparser)

        (options, args) = optparser.parse_args(args)
        for item in self.iterate_plugins():
            if (isinstance(item, core.api.IConfigurable)):
                item.configure(options)

        for item in self.iterate_plugins():
            item.initialize()
            
        return args

    def unload(self):
        for item in self.iterate_plugins(is_reversed = True):
            item.terminate()

    def run(self, args):
        for item in self.iterate_plugins():
            if (isinstance(item, core.api.IRunable)):
                item.run(args)
        return self.exit_code

    def inc_exit_code(self):
        self.exit_code += 1

    def __repr__(self):
        result = object.__repr__(self) + ' with loaded:'
        for item in self.iterate_plugins():
            result += '\n\t' + item.__repr__()
            if isinstance(item, core.api.Parent):
                result += ' with subscribed:'
                for child in item.iterate_children():
                    result += '\n\t\t' + child.__repr__()
        return result

