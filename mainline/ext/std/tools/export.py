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
import mpp.utils

import csv

class Plugin(mpp.api.Plugin, mpp.api.IRunable):

    def run(self, args):
        self.loader_prev = self.get_plugin('mpp.dbf').get_loader_prev()
        self.loader = self.get_plugin('mpp.dbf').get_loader()
    
        paths = None
        if len(args) == 0:
            paths = [""]
        else:
            paths = args
            
        return self._export_to_stdout(paths)

    def _export_to_stdout(self, paths):
        class StdoutWriter(object):
            def write(self, *args, **kwargs):
                print args[0].strip()
        
        exit_code = 0
    
        columns = []
        columnNames = ["file", "region", "type", "modified", "line start", "line end"]
        for name in self.loader.iterate_namespace_names():
            namespace = self.loader.get_namespace(name)
            for field in namespace.iterate_field_names():
                columns.append((name, field))
                columnNames.append(name + ":" + field)
    
        writer = StdoutWriter()
        csvWriter = csv.writer(writer)
        csvWriter.writerow(columnNames)
        
        for path in paths:
            path = mpp.utils.preprocess_path(path)
            
            files = self.loader.iterate_file_data(path)
            if files == None:
                mpp.utils.report_bad_path(path)
                exit_code += 1
                continue
                
            for file_data in files:
                matcher = None
                file_data_prev = self.loader_prev.load_file_data(file_data.get_path())
                if file_data_prev != None:
                    matcher = mpp.utils.FileRegionsMatcher(file_data, file_data_prev)
                for reg in file_data.iterate_regions():
                    per_reg_data = []
                    per_reg_data.append(mpp.api.Region.T().to_str(reg.get_type()))
                    if matcher != None and matcher.is_matched(reg.get_id()):
                        per_reg_data.append(matcher.is_modified(reg.get_id()))
                    else:
                        per_reg_data.append(None)
                    per_reg_data.append(reg.get_line_begin())
                    per_reg_data.append(reg.get_line_end())
                    for column in columns:
                        per_reg_data.append(reg.get_data(column[0], column[1]))
                    csvWriter.writerow([file_data.get_path(), reg.get_name()] + per_reg_data)
                per_file_data = []
                per_file_data.append('file')
                if file_data_prev != None:
                    per_file_data.append(file_data.get_checksum() != file_data_prev.get_checksum()) 
                else:
                    per_file_data.append(None)
                per_file_data.append(file_data.get_region(1).get_line_begin())
                per_file_data.append(file_data.get_region(1).get_line_end())
                for column in columns:
                    per_file_data.append(file_data.get_data(column[0], column[1]))
                csvWriter.writerow([file_data.get_path(), None] + per_file_data)
    
        return exit_code
