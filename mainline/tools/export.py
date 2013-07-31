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



import logging
import csv

import core.api
import core.log
import core.db.post
import core.cmdparser

import tools.utils

class Tool(core.api.ITool):
    def run(self, tool_args):
        return main(tool_args)

def main(tool_args):
    
    log_plugin = core.log.Plugin()
    db_plugin = core.db.post.Plugin()

    parser = core.cmdparser.MultiOptionParser(usage="Usage: %prog export [options] -- [path 1] ... [path N]")
    log_plugin.declare_configuration(parser)
    db_plugin.declare_configuration(parser)
    parser.add_option("--format", "--ft", default='csv', choices=['csv', 'xml'], help="Format of the output data. "
                      "Possible values are 'xml' and 'csv' [default: %default]")

    (options, args) = parser.parse_args(tool_args)
    log_plugin.configure(options)
    db_plugin.configure(options)
    out_format = options.__dict__['format']

    loader_prev = core.api.Loader()
    if db_plugin.dbfile_prev != None:
        if loader_prev.open_database(db_plugin.dbfile_prev) == False:
            parser.error("Can not open file: " + db_plugin.dbfile_prev)


    loader = core.api.Loader()
    if loader.open_database(db_plugin.dbfile) == False:
        parser.error("Can not open file: " + db_plugin.dbfile)
    
    # Check for versions consistency
    for each in loader.iterate_properties():
        if db_plugin.dbfile_prev != None:
            prev = loader_prev.get_property(each.name)
            if prev != each.value:
                logging.warn("Previous data has got different metadata:")
                logging.warn(" - identification of change trends can be not reliable")
                logging.warn(" - use 'info' tool to get more details")
                break
    
    paths = None
    if len(args) == 0:
        paths = [""]
    else:
        paths = args
        
    exit_code = export_to_stdout(out_format, paths, loader, loader_prev)
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
        path = tools.utils.preprocess_path(path)
        
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
            tools.utils.report_bad_path(path)
            exit_code += 1

    if out_format == 'xml':
        print "XML"
    return 0