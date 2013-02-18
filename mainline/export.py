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
import time
import re

import core.log
import core.db.loader
import core.db.post
import core.db.utils
import core.cmdparser
import core.export.convert

def main():
    
    exit_code = 0
    log_plugin = core.log.Plugin()
    db_plugin = core.db.post.Plugin()

    parser = core.cmdparser.MultiOptionParser(usage="Usage: %prog [options] -- <path 1> ... <path N>")
    log_plugin.declare_configuration(parser)
    db_plugin.declare_configuration(parser)
    parser.add_option("--general.format", default='xml', choices=['txt', 'xml', 'python'], help="Format of the output data [default: %default]")
    parser.add_option("--general.namespaces", default=None, help="Allows to enumerate namespaces of interest."
                      " If not defined all namespaces available in database file will be processed."
                      " Separate several namespaces by comma, for example 'general,std.code.complexity'"
                      " [default: %default]")

    (options, args) = parser.parse_args()
    log_plugin.configure(options)
    db_plugin.configure(options)
    out_format = options.__dict__['general.format']
    namespaces = None
    if options.__dict__['general.namespaces'] != None:
        namespaces = re.split(',', options.__dict__['general.namespaces'])

    loader_prev = core.db.loader.Loader()
    if db_plugin.dbfile_prev != None:
        loader_prev.open_database(db_plugin.dbfile_prev)

    loader = core.db.loader.Loader()
    loader.open_database(db_plugin.dbfile)
    
    paths = None
    if len(args) == 0:
        paths = [""]
    else:
        paths = args
        
    if out_format == 'txt':
        print "=" * 80 + "\n" + "Export" + "\n" + "_" * 80 + "\n"
    elif out_format == 'xml':
        print "<export>"
    elif out_format == 'python':
        print "{'export': ["

    for (ind, path) in enumerate(paths):
        logging.info("Processing: " + path)
        
        aggregated_data = loader.load_aggregated_data(path, namespaces=namespaces)
        aggregated_data_tree = {}
        subdirs = []
        subfiles = []
        if aggregated_data != None:
            aggregated_data_tree = aggregated_data.get_data_tree(namespaces=namespaces)
            subdirs = aggregated_data.get_subdirs()
            subfiles = aggregated_data.get_subfiles()
        else:
            logging.error("Specified path '" + path + "' is invalid (not found in the database records)")
            exit_code += 1
        aggregated_data_prev = loader_prev.load_aggregated_data(path, namespaces=namespaces)
        if aggregated_data_prev != None:
            aggregated_data_tree = append_diff(aggregated_data_tree,
                                           aggregated_data_prev.get_data_tree(namespaces=namespaces))
        
        file_data = loader.load_file_data(path)
        file_data_tree = {}
        if file_data != None:
            file_data_tree = file_data.get_data_tree(namespaces=namespaces) 
            file_data_prev = loader_prev.load_file_data(path)
            regions_matcher = None
            if file_data_prev != None:
                file_data_tree = append_diff(file_data_tree,
                                             file_data_prev.get_data_tree(namespaces=namespaces))
                regions_matcher = core.db.utils.FileRegionsMatcher(file_data, file_data_prev)
            
            regions = []
            for each in file_data.iterate_regions():
                region_data_tree = each.get_data_tree(namespaces=namespaces)
                if regions_matcher != None and regions_matcher.is_matched(each.id):
                    region_data_prev = file_data_prev.get_region(regions_matcher.get_prev_id(each.id))
                    region_data_tree = append_diff(region_data_tree,
                                                   region_data_prev.get_data_tree(namespaces=namespaces))
                regions.append({"info": {"name" : each.name,
                                         'type' : file_data.get_region_types()().to_str(each.get_type()),
                                         "cursor" : each.cursor,
                                         'line_begin': each.line_begin,
                                         'line_end': each.line_end,
                                         'offset_begin': each.begin,
                                         'offset_end': each.end},
                                "data": region_data_tree})
                
            file_data_tree['regions'] = regions
        
        data = {"info": {"path": path, "id": ind + 1},
                "aggregated-data": aggregated_data_tree,
                "file-data": file_data_tree,
                "subdirs": subdirs,
                "subfiles": subfiles}

        if out_format == 'txt':
            print core.export.convert.to_txt(data, root_name = "data")
        elif out_format == 'xml':
            print core.export.convert.to_xml(data, root_name = "data")
        elif out_format == 'python':
            postfix = ""
            if ind < len(paths) - 1:
                postfix = ", "
            print core.export.convert.to_python(data, root_name = "data") + postfix

    if out_format == 'txt':
        print "\n"
    elif out_format == 'xml':
        print "</export>"
    elif out_format == 'python':
        print "]}"


    return exit_code

def append_diff(main_tree, prev_tree):
    assert(main_tree != None)
    assert(prev_tree != None)
    
    for name in main_tree.keys():
        if name not in prev_tree.keys():
            continue
        for field in main_tree[name].keys():
            if field not in prev_tree[name].keys():
                continue
            if isinstance(main_tree[name][field], dict) and isinstance(prev_tree[name][field], dict):
                diff = {}
                for key in main_tree[name][field].keys():
                    if key not in prev_tree[name][field].keys():
                        continue
                    diff[key] = main_tree[name][field][key] - prev_tree[name][field][key]
                main_tree[name][field]['__diff__'] = diff
            elif (not isinstance(main_tree[name][field], dict)) and (not isinstance(prev_tree[name][field], dict)):
                if '__diff__' not in main_tree[name]:
                    main_tree[name]['__diff__'] = {}
                main_tree[name]['__diff__'][field] = main_tree[name][field] - prev_tree[name][field]
    return main_tree

if __name__ == '__main__':
    ts = time.time()
    core.log.set_default_format()
    exit_code = main()
    logging.warning("Exit code: " + str(exit_code) + ". Time spent: " + str(round((time.time() - ts), 2)) + " seconds. Done")
    exit(exit_code)
    
    
  
