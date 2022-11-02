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

    def readtextfile(self,filename):
        """ Read a text file and try to detect the coding
        """

        # Subroutine - Check for UTF8:
        # "a" is the textfile represented as a simple byte array!
        # Find first char with code > 127:
        # 1 nothing found: all bytes in range(0..127); in this case "a" only consists
        #   of ASCII chars but this may also be treated as valid UTF8 coding
        # 2 Code is a valid UTF8 leading byte: range(176,271)
        #   then check subsequent bytes to be UTF8 extension bytes: range(128,175)
        #   Does also do some plausibility checks: If a valid UTF8 byte sequence is found
        #   - the subsequent byte (after the UTF8 sequence) must be an ASCII or
        #     another UTF8 leading byte (in the latter case we assume that there
        #     are following the appropriate number of UTF8 extension bytes..)
        #   Note that this checks don't guarantee the text is really UTF8 encoded:
        #   If a valid UTF8 sequence is found but in fact the text is some sort
        #   of 8 bit OEM coding this may be coincidentally a sequence of 8 bit
        #   OEM chars. This indeed seems very unlikely but may happen...
        #   Otherwise the whole text has to be examined for UTF8 sequences.
        # 3 Code is not a valid UTF8 leading byte: range(128,175) or range(272,255)
        #   In this case coding is some sort of 8 bit OEM coding. Since we don't
        #   know the OEM code page the file was written with, we assume "latin_1"
        #   (is mostly the same as ANSI but "ansi" isn't available on Python 2)
        #
        # return  suggested text coding: "ascii","utf_8" or "latin_1"
        def checkforUTF8(a,default="latin_1"):
            L = len(a)
            n = 0
            while ( (n < L) and (a[n] < 128) ):
                n = n+1
            if ( n >= L ):                          # all chars < 128: ASCII coding
                return "ascii"                      # but may also be treated as UTF8!

            w = a[n]

            if w in range(176,207):                 # UTF8 two byte sequence: leading byte + 1 extension byte
                if ( (n+1 < L)
                 and (a[n+1] in range(128,175))     # valid UTF8 extension byte
                ):
                    if ((n+2 == L)                  # w is last UTF8 character
                     or (a[n+2] < 128)              # or next byte is an ASCII char
                     or (a[n+2] in range(176,271))  # or next byte is an UTF8 leading byte
                    ):
                        return "utf_8"
                return default

            if w in range(208,239):                 # UTF8 three byte sequence: leading byte + 2 extension bytes
                if ( (n+2 < L)
                 and (a[n+1] in range(128,175))     # 2 valid UTF8 extension bytes
                 and (a[n+2] in range(128,175))
                ):
                    if ((n+3 == L)                  # w is last UTF8 character
                     or (a[n+3] < 128)              # or next byte is ASCII char
                     or (a[n+3] in range(176,271))  # or next byte is UTF8 leading byte
                    ):
                        return "utf_8"
                return default

            if w in range(240,271):                 # UTF8 four byte sequence: leading byte + 3 extension bytes
                if ( (n+3 < L)
                 and (a[n+1] in range(128,175))     # 3 valid UTF8 extension bytes
                 and (a[n+2] in range(128,175))
                 and (a[n+3] in range(128,175))
                ):
                    if ((n+4 == L)                  # w is last UTF8 character
                     or (a[n+4] < 128)              # or next byte is ASCII char
                     or (a[n+4] in range(176,271))  # or next byte is UTF8 leading byte
                    ):
                        return "utf_8"
                return default
          # end of checkforUTF8 ------------------------------------------------

        # Subroutine readtextfile
        # open as binary and try to guess the encoding:
        f = open(filename, 'rb');
        a = f.read();
        f.close()

        # check for codings with BOM:
        if a.startswith(b'\xff\xfe'):
            coding = "utf_16_le"
        elif a.startswith(b'\xfe\xff'):
            coding = "utf_16_be"
        elif a.startswith(b'\xff\xfe\x00\x00'):
            coding = "utf_32_le"
        elif a.startswith(b'\x00\x00\xfe\xff'):
            coding = "utf_32_be"
        elif a.startswith(b'\xef\xbb\xbf'):
            coding = "utf_8_sig"
        # elif: there are some other codings with BOM - feel free to add them here

        # elif: check UTF variants without BOM:
        # at this point one may try to determine UTF16 or UTF32 codings without BOM
        # but this should not happen since these codings strictly require a BOM.
        # So finally we only have to look for UTF8 without BOM:
        else:
            coding = checkforUTF8(a)

        # decode to text with found coding; since our guess may be wrong
        # we replace unknown chars to avoid errors. Cause we examine program code
        # files (i.e. true program code should only consist of ASCII chars) these
        # replacements only should affect string literals and comments and should
        # have no effect to metric analysis.
        text = a.decode(coding,'replace')

        # Finally replace possible line break variants with \n:
        # todo: replace with a regex
        text = text.replace("\r\n","\n")
        text = text.replace("\r","\n")

        # debug:
        #print(filename+" - Coding found = "+coding+" len: "+str(len(text)))
        #f = open(filename+"."+asCoding,'wb')
        #f.write(text.encode(coding))
        #f.close

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
