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
import re

import core.log
import core.db.loader
import core.db.post
import core.db.utils
import core.cmdparser
import core.export.convert

import core.api
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

    loader_prev = core.db.loader.Loader()
    if db_plugin.dbfile_prev != None:
        loader_prev.open_database(db_plugin.dbfile_prev)

    loader = core.db.loader.Loader()
    loader.open_database(db_plugin.dbfile)
    
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
    exit_code = 0

    columns = []
    for name in loader.iterate_namespace_names():
        namespace = loader.get_namespace(name)
        for field in namespace.iterate_field_names():
            columns.append((name, field, namespace.are_regions_supported()))
    
    if out_format == 'xml':
        print "<export>\n"
    elif out_format == 'csv':
        print "CSV"
    else:
        assert False, "Unknown output format " + out_format

    for (ind, path) in enumerate(paths):
        logging.info("Processing: " + re.sub(r'''[\\]''', "/", path))
        
        files = loader.iterate_file_data(path)
        if files != None:
            for file_data in files:
                for column in columns:
                    print column[0], column[1], file_data.get_data(column[0], column[1])
        else:
            logging.error("Specified path '" + path + "' is invalid (not found in the database records)")
            exit_code += 1

    if out_format == 'xml':
        print "XML"
    return 0