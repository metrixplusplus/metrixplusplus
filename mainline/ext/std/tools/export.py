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

class Plugin(mpp.api.Plugin, mpp.api.IConfigurable, mpp.api.IRunable):
    
    def declare_configuration(self, parser):
        parser.add_option("--format", "--ft", default='csv', choices=['csv', 'xml'], help="Format of the output data. "
                          "Possible values are 'xml' and 'csv' [default: %default]")
    
    def configure(self, options):
        self.out_format = options.__dict__['format']

    def run(self, args):
        loader_prev = self.get_plugin_loader().get_plugin('mpp.dbf').get_loader_prev()
        loader = self.get_plugin_loader().get_plugin('mpp.dbf').get_loader()
    
        paths = None
        if len(args) == 0:
            paths = [""]
        else:
            paths = args
            
        exit_code = export_to_stdout(self.out_format, paths, loader, loader_prev)
        return exit_code

def export_to_stdout(out_format, paths, loader, loader_prev):
    class StdoutWriter(object):
        def write(self, *args, **kwargs):
            print args[0],
    
    exit_code = 0


    columnNames = ["file", "region", ]
    columns = []
    for name in loader.iterate_namespace_names():
        namespace = loader.get_namespace(name)
        for field in namespace.iterate_field_names():
            columns.append((name, field, namespace.are_regions_supported()))
            columnNames.append(name + ":" + field)

    writer = StdoutWriter()
    csvWriter = csv.writer(writer)
    csvWriter.writerow(columnNames)
    
    if out_format == 'xml':
        print "<export>\n"
    elif out_format == 'csv':
        print "CSV"
    else:
        assert False, "Unknown output format " + out_format

    for path in paths:
        path = mpp.utils.preprocess_path(path)
        
        files = loader.iterate_file_data(path)
        if files != None:
            for file_data in files:
                for reg in file_data.iterate_regions():
                    per_reg_data = []
                    for column in columns:
                        per_reg_data.append(reg.get_data(column[0], column[1]))
                    csvWriter.writerow([file_data.get_path(), reg.get_name()] + per_reg_data)
                per_file_data = []
                for column in columns:
                    per_file_data.append(file_data.get_data(column[0], column[1]))
                csvWriter.writerow([file_data.get_path(), None] + per_file_data)
        else:
            mpp.utils.report_bad_path(path)
            exit_code += 1

    if out_format == 'xml':
        print "XML"
    return 0