#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    


from metrixpp.mpp import api

import re
import os
import sys
import logging
import time
import binascii
import fnmatch
import multiprocessing.pool

class Plugin(api.Plugin, api.Parent, api.IConfigurable, api.IRunable):
    
    def __init__(self):
        self.reader = DirectoryReader()
        self.include_rules = []
        self.exclude_rules = []
        self.exclude_files = []
        self.parsers       = []
        super(Plugin, self).__init__()

    def declare_configuration(self, parser):
        parser.add_option("--std.general.proctime", "--sgpt", action="store_true", default=False,
                         help="If the option is set (True), the tool measures processing time per file [default: %default]")
        parser.add_option("--std.general.procerrors", "--sgpe", action="store_true", default=False,
                         help="If the option is set (True), the tool counts number of processing/parsing errors per file [default: %default]")
        parser.add_option("--std.general.size", "--sgs", action="store_true", default=False,
                         help="If the option is set (True), the tool collects file size metric (in bytes) [default: %default]")
        parser.add_option("--include-files", "--if", action='append',
                         help="Adds a regular expression pattern to include files in processing (files have to match any rule to be included)")
        parser.add_option("--exclude-files", "--ef", action='append',
                         help="Adds a regular expression pattern to exclude files or directories from processing")
        parser.add_option("--non-recursively", "--nr", action="store_true", default=False,
                         help="If the option is set (True), sub-directories are not processed [default: %default]")
        self.optparser = parser
    
    def configure(self, options):
        self.is_proctime_enabled = options.__dict__['std.general.proctime']
        self.is_procerrors_enabled = options.__dict__['std.general.procerrors']
        self.is_size_enabled = options.__dict__['std.general.size']
        # check if any include rule is given
        if options.__dict__['include_files']:
            try:
                for include_rule in options.__dict__['include_files']:
                    self.add_include_rule(re.compile(include_rule))
            except Exception as e:
                self.optparser.error("option --include-files: " + str(e))
        else:
            self.add_include_rule(re.compile(r'.*'))
        
        # check if any exclude rule is given
        if options.__dict__['exclude_files']:
            try:
                for exclude_rule in options.__dict__['exclude_files']:
                    self.add_exclude_rule(re.compile(exclude_rule))
            except Exception as e:
                self.optparser.error("option --exclude-files: " + str(e))
        else:
            self.add_exclude_rule(re.compile(r'^[.]'))
        self.non_recursively = options.__dict__['non_recursively']

    def initialize(self):
        fields = []
        if self.is_proctime_enabled == True:
            fields.append(self.Field('proctime', float))
        if self.is_procerrors_enabled == True:
            fields.append(self.Field('procerrors', int))
        if self.is_size_enabled == True:
            fields.append(self.Field('size', int))
        super(Plugin, self).initialize(namespace='std.general', support_regions=False, fields=fields)
        self.add_exclude_file(self.get_plugin('metrixpp.mpp.dbf').get_dbfile_path())
        self.add_exclude_file(self.get_plugin('metrixpp.mpp.dbf').get_dbfile_prev_path())
        
    def run(self, args):
        if len(args) == 0:
            return self.reader.run(self, "./")
        retcode = 0
        for directory in args:
            retcode += self.reader.run(self, directory)
        return retcode
        
    def register_parser(self, fnmatch_exp_list, parser):
        self.parsers.append((fnmatch_exp_list, parser))

    def get_parser(self, file_path):
        for parser in self.parsers:
            for fnmatch_exp in parser[0]:
                if fnmatch.fnmatch(file_path, fnmatch_exp):
                    return parser[1]
        return None

    def add_include_rule(self, re_compiled_pattern):
        self.include_rules.append(re_compiled_pattern)

    def add_exclude_rule(self, re_compiled_pattern):
        self.exclude_rules.append(re_compiled_pattern)

    def add_exclude_file(self, file_path):
        if file_path == None:
            return
        self.exclude_files.append(file_path)

    def is_file_excluded(self, file_name):
        # only apply the include rules to files - skip directories
        if os.path.isfile(file_name):
            for each in self.include_rules:
                if re.match(each, os.path.basename(file_name)) != None:
                    break;
            # file is excluded if no include rule matches
            else:
                return True
        # check exclude rules for both, files and directories
        for each in self.exclude_rules:
            if re.match(each, os.path.basename(file_name)) != None:
                return True
        # finally check if a file is excluded directly
        for each in self.exclude_files:
            if os.path.basename(each) == os.path.basename(file_name):
                if os.stat(each) == os.stat(file_name):
                    return True
        return False 
        
class DirectoryReader():
    
    def run(self, plugin, directory):
        
        IS_TEST_MODE = False
        if 'METRIXPLUSPLUS_TEST_MODE' in list(os.environ.keys()):
            IS_TEST_MODE = True

        def run_per_file(plugin, fname, full_path):
            exit_code = 0
            norm_path = re.sub(r'''[\\]''', "/", full_path)
            if os.path.isabs(norm_path) == False and norm_path.startswith('./') == False:
                norm_path = './' + norm_path
            if plugin.is_file_excluded(norm_path) == False:
                if os.path.isdir(full_path):
                    if plugin.non_recursively == False:
                        exit_code += run_recursively(plugin, full_path)
                else:
                    parser = plugin.get_parser(full_path)
                    if parser == None:
                        logging.info("Skipping: " + norm_path)
                    else:
                        logging.info("Processing: " + norm_path)
                        ts = time.time()
                        f = open(full_path, 'rU');
                        text = f.read();
                        # getting along with the different string handling of python 2 and 3
                        # trying to get along with different encodings to get the tests running
                        # on windows and linux
                        try:
                            text = text.encode(f.encoding)
                        except:
                            pass
                        try:
                            text = text.decode('utf-8')
                        except:
                            pass
                        f.close()
                        checksum = binascii.crc32(text.encode('utf8')) & 0xffffffff # to match python 3
                        
                        db_loader = plugin.get_plugin('metrixpp.mpp.dbf').get_loader()
                        (data, is_updated) = db_loader.create_file_data(norm_path, checksum, text)
                        procerrors = parser.process(plugin, data, is_updated)
                        if plugin.is_proctime_enabled == True:
                            data.set_data('std.general', 'proctime',
                                          (time.time() - ts) if IS_TEST_MODE == False else 0.01)
                        if plugin.is_procerrors_enabled == True and procerrors != None and procerrors != 0:
                            data.set_data('std.general', 'procerrors', procerrors)
                        if plugin.is_size_enabled == True:
                            data.set_data('std.general', 'size', len(text))
                        db_loader.save_file_data(data)
                        #logging.debug("-" * 60)
                        exit_code += procerrors
            else:
                logging.info("Excluding: " + norm_path)
            return exit_code
        

        #thread_pool = multiprocessing.pool.ThreadPool()
        #def mp_worker(args):
        #    run_per_file(args[0], args[1], args[2])
        def run_recursively(plugin, directory):
            exit_code = 0
            #thread_pool.map(mp_worker,
            #    [(plugin, f, os.path.join(subdir, f))
            #        for subdir, dirs, files in os.walk(directory) for f in files])
            for fname in sorted(os.listdir(directory)):
                full_path = os.path.join(directory, fname)
                exit_code += run_per_file(plugin, fname, full_path)
            
            return exit_code
        
        if os.path.exists(directory) == False:
            logging.error("Skipping (does not exist): " + directory)
            return 1
        
        if os.path.isdir(directory):
            total_errors = run_recursively(plugin, directory)
        else:
            total_errors = run_per_file(plugin, os.path.basename(directory), directory)
        total_errors = total_errors # used, warnings are per file if not zero
        return 0 # ignore errors, collection is successful anyway
