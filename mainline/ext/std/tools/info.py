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


import mpp.api
import mpp.cout
import mpp.utils

import os

class Plugin(mpp.api.Plugin, mpp.api.IRunable):
    
    def run(self, args):
        exit_code = 0
    
        loader_prev = self.get_plugin('mpp.dbf').get_loader_prev(none_if_empty=True)
        loader = self.get_plugin('mpp.dbf').get_loader()
    
        details = []
        for each in loader.iterate_properties():
            prev_value_str = ""
            if loader_prev != None:
                prev = loader_prev.get_property(each.name)
                if prev == None:
                    prev_value_str = " [new]"
                elif prev != each.value:
                    prev_value_str = " [modified (was: " + loader_prev.get_property(each.name) + ")]"
            details.append((each.name, each.value + prev_value_str))
        path = self.get_plugin('mpp.dbf').get_dbfile_path()
        if ('METRIXPLUSPLUS_TEST_MODE' in os.environ.keys() and
             os.environ['METRIXPLUSPLUS_TEST_MODE'] == "True"):
            # in tests, paths come as full paths, strip it for consistent gold files
            # TODO: if there are other path-like arguments, it is better to think about other solution
            path = os.path.basename(path)
        mpp.cout.notify(path, '', mpp.cout.SEVERITY_INFO, 'Created using plugins and settings:', details)
    
        details = []
        for each in sorted(loader.iterate_namespace_names()):
            for field in sorted(loader.get_namespace(each).iterate_field_names()):
                prev_value_str = ""
                if loader_prev != None:
                    prev = False
                    prev_namespace = loader_prev.get_namespace(each)
                    if prev_namespace != None:
                        prev = prev_namespace.check_field(field)
                    if prev == False:
                        prev_value_str = " [new]"
                details.append((each + ':' + field,  prev_value_str))
        mpp.cout.notify(path, '', mpp.cout.SEVERITY_INFO, 'Collected metrics:', details)
    
        paths = None
        if len(args) == 0:
            paths = [""]
        else:
            paths = args
        for path in paths:
            details = []
            path = mpp.utils.preprocess_path(path)
    
            file_iterator = loader.iterate_file_data(path=path)
            if file_iterator == None:
                mpp.utils.report_bad_path(path)
                exit_code += 1
                continue
            for each in file_iterator:
                prev_value_str = ""
                if loader_prev != None:
                    prev = loader_prev.load_file_data(each.get_path())
                    if prev == None:
                        prev_value_str = " [new]"
                    elif prev.get_checksum() != each.get_checksum():
                        prev_value_str = " [modified]"
                details.append((each.get_path(), '{0:#x}'.format(each.get_checksum()) + prev_value_str))
            mpp.cout.notify(path, '', mpp.cout.SEVERITY_INFO, 'Processed files and checksums:', details)
            
        return exit_code


