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
        self.exclude_dir_rules = []
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
                         help="Adds a regular expression pattern to exclude files or directories by name from processing")
        parser.add_option("--exclude-directories", "--ed", action='append',
                         help="Adds a regular expression pattern to exclude directories by path from processing")
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

        # check if any exclude dir rule is given
        if options.__dict__['exclude_directories']:
            try:
                for exclude_dir_rule in options.__dict__['exclude_directories']:
                    self.add_exclude_dir_rule(re.compile(exclude_dir_rule))
            except Exception as e:
                self.optparser.error("option --exclude-directories: " + str(e))
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

    def add_exclude_dir_rule(self, re_compiled_pattern):
        self.exclude_dir_rules.append(re_compiled_pattern)

    def add_exclude_file(self, file_path):
        if file_path == None:
            return
        self.exclude_files.append(file_path)

    def is_file_excluded(self, file_name):
        # only apply the include rules to files - skip directories
        if os.path.isfile(file_name):
            for each in self.include_rules:
                if re.match(each, os.path.basename(file_name)) != None:
                    break
            # file is excluded if no include rule matches
            else:
                logging.info("Excluding: " + file_name + " - not included by any rule")
                return True
        # check exclude dir rules for directories
        if os.path.isdir(file_name):
            for each in self.exclude_dir_rules:
                if re.match(each, file_name) != None:
                    logging.info("Excluding: " + file_name + " - excluded by rule '" + each.pattern + "'")
                    return True
        # check exclude rules for both, files and directories
        for each in self.exclude_rules:
            if re.match(each, os.path.basename(file_name)) != None:
                logging.info("Excluding: " + file_name + " - excluded by rule '" + each.pattern + "'")
                return True
        # finally check if a file is excluded directly
        for each in self.exclude_files:
            if os.path.basename(each) == os.path.basename(file_name):
                if os.stat(each) == os.stat(file_name):
                    return True
        return False

class DirectoryReader():

    def readtextfile(self,filename):
        """ Read a text file and try to detect the coding

            Since we examine program code text files we can assume the following:
            - There are no NUL characters, i.e. no 0x00 sequences of 1, 2 or 4
              byte, starting on 1, 2 or 4 byte boundaries (depending on
              1, 2 or 4 byte coding)
            - There should at least one space (ASCII 0x20) char
              of the respective length (1,2 or 4 byte))
            - Program code consists of only ASCII chars, i.e. code < 128
            - Non ASCII chars should appear in string literals and comments only

            Though especially in the case of an 8 bit coding it does not matter
            which code page to use: Metric analysis is done on program code
            which is pure ASCII; string literals and comments are only recognized
            as such but not interpreted, though it doesn't matter if they contain
            non-ASCII chars whichever code page is used.

            Note the decoder's different behavior for the "utf_nn" identifiers:
            - .decode("utf_32") / .decode("utf_16"):       preceding BOM is skipped
            - with suffix ".._be" or ".._le" respectively: preceding BOM is preserved
            but
            - .decode("utf_8"):     preceding BOM is preserved
            - .decode("utf_8_sig"): preceding BOM is skipped
        """
        # Methods to check for various UTF variants without BOM:
        # Since UTF16/32 codings are recommended to use a BOM these methods
        # shouldn't be necessary but may be useful in certain cases.
        def checkforUTF32_BE(a):
            if ( (len(a) % 4) != 0 ): return False
            n = a.find(b'\x00\x00\x00\x20')
            return (n >= 0) and ((n % 4) == 0)
        def checkforUTF32_LE(a):
            if ( (len(a) % 4) != 0 ): return False
            n = a.find(b'\x20\x00\x00\x00')
            return (n >= 0) and ((n % 4) == 0)
        def checkforUTF16_BE(a):
            if ( (len(a) % 2) != 0 ): return False
            n = a.find(b'\x00\x20')
            return (n >= 0) and ((n % 2) == 0)
        def checkforUTF16_LE(a):
            if ( (len(a) % 2) != 0 ): return False
            n = a.find(b'\x20\x00')
            return (n >= 0) and ((n % 2) == 0)

        # Method to check for UTF8 without BOM:
        # "a" is the textfile represented as a simple byte array!
        # Find first char with code > 127:
        #
        # 1 nothing found: all bytes 0..127; in this case "a" only consists
        #   of ASCII chars but this may also be treated as valid UTF8 coding
        #
        # 2 Code is a valid UTF8 leading byte: 176..271
        #   then check subsequent bytes to be UTF8 extension bytes: 128..175
        #   Does also do some additional plausibility checks:
        #   If a valid UTF8 byte sequence is found
        #   - the subsequent byte (after the UTF8 sequence) must be an ASCII
        #   - or another UTF8 leading byte (in the latter case we assume that there
        #     are following the appropriate number of UTF8 extension bytes..)
        #   Note that these checks don't guarantee the text is really UTF8 encoded:
        #   If a valid UTF8 sequence is found but in fact the text is some sort
        #   of 8 bit OEM coding this may be coincidentally a sequence of 8 bit
        #   OEM chars. This indeed seems very unlikely but may happen...
        #   Even though the whole text would examined for UTF8 sequences: every
        #   valid UTF8 sequence found may also be a sequence of OEM chars!
        #
        # 3 Code is not a valid UTF8 leading byte: 128..175 or 272..255
        #   In this case coding is some sort of 8 bit OEM coding. Since we don't
        #   know the OEM code page the file was written with, we assume "latin_1"
        #   (is mostly the same as ANSI but "ansi" isn't available on Python 2)
        #
        # return  suggested text coding: "ascii","utf_8" or "latin_1" (resp. default)
        def checkforUTF8(a,default="latin_1"):

            # Since "a" is a string array on Python 2 we use a special ORD function:
            # Convert c to its byte representation if it is a character
            # Works for Python 2+3
            def ORD(c): return ord(c) if (type(c) == str) else c

            L = len(a)
            n = 0
            while ( (n < L) and (ORD(a[n]) < 128) ): # (a[n] < ExtASCII) ):
                n = n+1
            if ( n >= L ):                          # all chars < 128: ASCII coding
                return "ascii"                      # but may also be treated as UTF8!
            w = a[n]

            # UTF8 two byte sequence: leading byte + 1 extension byte
            if ORD(w) in range(192,224):
                if ( (n+1 < L)
                 and (ORD(a[n+1]) in range(128,192))     # valid UTF8 extension byte
                ):
                    if ((n+2 == L)                  # w is last character
                     or (ORD(a[n+2]) < 128)              # or next byte is an ASCII char
                     or (ORD(a[n+2]) in range(192,244))  # or next byte is an UTF8 leading byte
                    ):
                        return "utf_8"
                return default

            # UTF8 three byte sequence: leading byte + 2 extension bytes
            if ORD(w) in range(224,240):
                if ( (n+2 < L)
                 and (ORD(a[n+1]) in range(128,192))     # 2 valid UTF8 extension bytes
                 and (ORD(a[n+2]) in range(128,192))
                ):
                    if ((n+3 == L)                  # w is last character
                     or (ORD(a[n+3]) < 128)              # or next byte is ASCII char
                     or (ORD(a[n+3]) in range(192,244))  # or next byte is UTF8 leading byte
                    ):
                        return "utf_8"
                return default

            # UTF8 four byte sequence: leading byte + 3 extension bytes
            if ORD(w) in range(240,244):
                if ( (n+3 < L)
                 and (ORD(a[n+1]) in range(128,192))     # 3 valid UTF8 extension bytes
                 and (ORD(a[n+2]) in range(128,192))
                 and (ORD(a[n+3]) in range(128,192))
                ):
                    if ((n+4 == L)                  # w is last character
                     or (ORD(a[n+4]) < 128)              # or next byte is ASCII char
                     or (ORD(a[n+4]) in range(192,244))  # or next byte is UTF8 leading byte
                    ):
                        return "utf_8"
                return default

            # no valid UTF8 byte sequence:
            return default
          # end of checkforUTF8 ------------------------------------------------

        # ----------------------------------------------------------------------
        # Subroutine readtextfile
        # open as binary and try to guess the encoding
        # attention:
        # - Phyton 3: "a" is a binary array
        # - Python 2: "a" is string array!
        # ----------------------------------------------------------------------
        f = open(filename, 'rb')
        a = f.read()
        f.close()

        # check for codings with BOM:
        # Consider the order: Check for UTF32 first!
        if  (a.startswith(b'\xff\xfe\x00\x00')
          or a.startswith(b'\x00\x00\xfe\xff')):
            coding = "utf_32"       # no suffix _be/_le --> decoder skips the BOM
        elif (a.startswith(b'\xff\xfe')
           or a.startswith(b'\xfe\xff')):
            coding = "utf_16"       # no suffix _be/_le --> decoder skips the BOM
        elif a.startswith(b'\xef\xbb\xbf'):
            coding = "utf_8_sig"

        # elif: there are some other codings with BOM - feel free to add them here

        # check for UTF variants without BOM:
        # Consider the order: Check for UTF32 first!
        elif checkforUTF32_BE(a):
            coding = "utf_32_be"
        elif checkforUTF32_LE(a):
            coding = "utf_32_le"
        elif checkforUTF16_BE(a):
            coding = "utf_16_be"
        elif checkforUTF16_LE(a):
            coding = "utf_16_le"

        # So finally we only have to look for UTF8 without BOM:
        else:
            coding = checkforUTF8(a)

        # decode to text with found coding; since our guess may be wrong
        # we replace unknown chars to avoid errors. Cause we examine program code
        # files (i.e. true program code should only consist of ASCII chars) these
        # replacements only should affect string literals and comments and should
        # have no effect on metric analysis.
        text = a.decode(coding,'replace')

        # Finally replace possible line break variants with \n:
        # todo: replace with a regex
        text = text.replace("\r\n","\n")
        text = text.replace("\r","\n")

        return text

        # end of readtextfile --------------------------------------------------

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

                        text = self.readtextfile(full_path)
                        #text = self.readfile_org(full_path)
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
