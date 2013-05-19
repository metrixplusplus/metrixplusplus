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

import re
import os
import logging
import time
import binascii

class Plugin(core.api.Plugin, core.api.Parent, core.api.IConfigurable, core.api.IRunable):
    
    def __init__(self):
        self.reader = DirectoryReader()
        self.exclude_rules = []
    
    def declare_configuration(self, parser):
        parser.add_option("--general.non-recursively", action="store_true", default=False,
                         help="If the option is set (True), sub-directories are not processed [default: %default]")
        parser.add_option("--general.exclude-files", default=r'^[.]',
                         help="Defines the pattern to exclude files from processing [default: %default]")
        parser.add_option("--general.proctime-on", action="store_true", default=False,
                         help="If the option is set (True), the tool measures processing time per file [default: %default]")
        parser.add_option("--general.procerrors-on", action="store_true", default=False,
                         help="If the option is set (True), the tool counts number of processing/parsing errors per file [default: %default]")
        parser.add_option("--general.size-on", action="store_true", default=False,
                         help="If the option is set (True), the tool collects file size metric (in bytes) [default: %default]")
    
    def configure(self, options):
        self.non_recursively = options.__dict__['general.non_recursively']
        self.add_exclude_rule(re.compile(options.__dict__['general.exclude_files']))
        self.is_proctime_enabled = options.__dict__['general.proctime_on']
        self.is_procerrors_enabled = options.__dict__['general.procerrors_on']
        self.is_size_enabled = options.__dict__['general.size_on']

    def initialize(self):
        namespace = self.get_plugin_loader().get_database_loader().create_namespace('general')
        if self.is_proctime_enabled == True:
            namespace.add_field('proctime', float)
        if self.is_procerrors_enabled == True:
            namespace.add_field('procerrors', int)
        if self.is_size_enabled == True:
            namespace.add_field('size', int)
        
    def run(self, args):
        if len(args) == 0:
            return self.reader.run(self, "./")
        for directory in args:
            return self.reader.run(self, directory)
        
    def add_exclude_rule(self, re_compiled_pattern):
        # TODO file name may have special regexp symbols what causes an exception
        # For example try to run a collection with "--general.db-file=metrix++" option
        self.exclude_rules.append(re_compiled_pattern)
        
    def is_file_excluded(self, file_name):
        for each in self.exclude_rules:
            if re.match(each, file_name) != None:
                return True
        return False 
        
class DirectoryReader():
    
    def run(self, plugin, directory):
        
        def run_recursively(plugin, directory):
            exit_code = 0
            for fname in os.listdir(directory):
                full_path = os.path.join(directory, fname)
                norm_path = re.sub(r'''[\\]''', "/", full_path)
                if plugin.is_file_excluded(fname) == False:
                    if os.path.isdir(full_path):
                        if plugin.non_recursively == False:
                            exit_code += run_recursively(plugin, full_path)
                    else:
                        parser = plugin.get_plugin_loader().get_parser(full_path)
                        if parser == None:
                            logging.info("Skipping: " + norm_path)
                        else:
                            logging.info("Processing: " + norm_path)
                            ts = time.time()
                            f = open(full_path, 'r');
                            text = f.read();
                            f.close()
                            checksum = binascii.crc32(text) & 0xffffffff # to match python 3
    
                            (data, is_updated) = plugin.get_plugin_loader().get_database_loader().create_file_data(full_path, checksum, text)
                            procerrors = parser.process(plugin, data, is_updated)
                            if plugin.is_proctime_enabled == True:
                                data.set_data('general', 'proctime', time.time() - ts)
                            if plugin.is_procerrors_enabled == True and procerrors != None and procerrors != 0:
                                data.set_data('general', 'procerrors', procerrors)
                            if plugin.is_size_enabled == True:
                                data.set_data('general', 'size', len(text))
                            plugin.get_plugin_loader().get_database_loader().save_file_data(data)
                            logging.debug("-" * 60)
                            exit_code += procerrors
                else:
                    logging.info("Excluding: " + norm_path)
                    logging.debug("-" * 60)
            return exit_code
        
        total_errors = run_recursively(plugin, directory)
        total_errors = total_errors # used, warnings are per file if not zero
        return 0 # ignore errors, collection is successful anyway
    


    