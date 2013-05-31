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
    parser.add_option("--general.format", default='xml', choices=['txt', 'xml', 'python'], help="Format of the output data. "
                      "Possible values are 'xml', 'txt' or 'python' [default: %default]")
    parser.add_option("--general.namespaces", default=None, help="Allows to enumerate namespaces of interest."
                      " If not defined all namespaces available in database file will be processed."
                      " Separate several namespaces by comma, for example 'general,std.code.complexity'"
                      " [default: %default]")
    parser.add_option("--general.nest-regions", action="store_true", default=False,
                      help="If the option is set (True), data for regions is exported in the form of a tree. "
                      "Otherwise, all regions are exported in plain list. [default: %default]")

    (options, args) = parser.parse_args(tool_args)
    log_plugin.configure(options)
    db_plugin.configure(options)
    out_format = options.__dict__['general.format']
    nest_regions = options.__dict__['general.nest_regions']
    namespaces = None
    if options.__dict__['general.namespaces'] != None:
        namespaces = re.split(',', options.__dict__['general.namespaces'])

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
        
    (result, exit_code) = export_to_str(out_format, paths, loader, loader_prev, namespaces, nest_regions)
    print result
    return exit_code

def export_to_str(out_format, paths, loader, loader_prev, namespaces, nest_regions):
    exit_code = 0
    result = ""
    if out_format == 'txt':
        result += "=" * 80 + "\n" + "Export" + "\n" + "_" * 80 + "\n\n"
    elif out_format == 'xml':
        result += "<export>\n"
    elif out_format == 'python':
        result += "{'export': ["

    for (ind, path) in enumerate(paths):
        logging.info("Processing: " + re.sub(r'''[\\]''', "/", path))
        
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
            append_regions(file_data_tree, file_data, file_data_prev, namespaces, nest_regions)
        
        data = {"info": {"path": path, "id": ind + 1},
                "aggregated-data": aggregated_data_tree,
                "file-data": file_data_tree,
                "subdirs": subdirs,
                "subfiles": subfiles}

        if out_format == 'txt':
            result += core.export.convert.to_txt(data, root_name = "data") + "\n"
        elif out_format == 'xml':
            result += core.export.convert.to_xml(data, root_name = "data") + "\n"
        elif out_format == 'python':
            postfix = ""
            if ind < len(paths) - 1:
                postfix = ", "
            result += core.export.convert.to_python(data, root_name = "data") + postfix

    if out_format == 'txt':
        result += "\n"
    elif out_format == 'xml':
        result += "</export>"
    elif out_format == 'python':
        result += "]}"
        
    return (result, exit_code)

def append_regions(file_data_tree, file_data, file_data_prev, namespaces, nest_regions):
    regions_matcher = None
    if file_data_prev != None:
        file_data_tree = append_diff(file_data_tree,
                                     file_data_prev.get_data_tree(namespaces=namespaces))
        regions_matcher = core.db.utils.FileRegionsMatcher(file_data, file_data_prev)
    
    if nest_regions == False:
        regions = []
        for region in file_data.iterate_regions():
            region_data_tree = region.get_data_tree(namespaces=namespaces)
            if regions_matcher != None and regions_matcher.is_matched(region.get_id()):
                region_data_prev = file_data_prev.get_region(regions_matcher.get_prev_id(region.get_id()))
                region_data_tree = append_diff(region_data_tree,
                                               region_data_prev.get_data_tree(namespaces=namespaces))
            regions.append({"info": {"name" : region.name,
                                     'type' : file_data.get_region_types()().to_str(region.get_type()),
                                     "cursor" : region.cursor,
                                     'line_begin': region.line_begin,
                                     'line_end': region.line_end,
                                     'offset_begin': region.begin,
                                     'offset_end': region.end},
                            "data": region_data_tree})
        file_data_tree['regions'] = regions
    else:
        def append_rec(region_id, file_data_tree, file_data, file_data_prev, namespaces):
            region = file_data.get_region(region_id)
            region_data_tree = region.get_data_tree(namespaces=namespaces)
            if regions_matcher != None and regions_matcher.is_matched(region.get_id()):
                region_data_prev = file_data_prev.get_region(regions_matcher.get_prev_id(region.get_id()))
                region_data_tree = append_diff(region_data_tree,
                                               region_data_prev.get_data_tree(namespaces=namespaces))
            result = {"info": {"name" : region.name,
                               'type' : file_data.get_region_types()().to_str(region.get_type()),
                               "cursor" : region.cursor,
                               'line_begin': region.line_begin,
                               'line_end': region.line_end,
                               'offset_begin': region.begin,
                               'offset_end': region.end},
                      "data": region_data_tree,
                      "subregions": []}
            for sub_id in file_data.get_region(region_id).iterate_subregion_ids():
                result['subregions'].append(append_rec(sub_id, file_data_tree, file_data, file_data_prev, namespaces))
            return result
        file_data_tree['regions'] = []
        file_data_tree['regions'].append(append_rec(1, file_data_tree, file_data, file_data_prev, namespaces))

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
                    main_val = main_tree[name][field][key]
                    prev_val = prev_tree[name][field][key]
                    if main_val == None:
                        main_val = 0
                    if prev_val == None:
                        prev_val = 0
                    if isinstance(main_val, list) and isinstance(prev_val, list):
                        main_tree[name][field][key] = append_diff_list(main_val, prev_val)
                    else:
                        diff[key] = main_val - prev_val
                main_tree[name][field]['__diff__'] = diff
            elif (not isinstance(main_tree[name][field], dict)) and (not isinstance(prev_tree[name][field], dict)):
                if '__diff__' not in main_tree[name]:
                    main_tree[name]['__diff__'] = {}
                main_tree[name]['__diff__'][field] = main_tree[name][field] - prev_tree[name][field]
    return main_tree

def append_diff_list(main_list, prev_list):
    merged_list = {}
    for bar in main_list:
        merged_list[bar['metric']] = {'count': bar['count'], '__diff__':0}
    for bar in prev_list:
        if bar['metric'] in merged_list.keys():
            merged_list[bar['metric']]['__diff__'] = \
                merged_list[bar['metric']]['count'] - bar['count']
        else:
            merged_list[bar['metric']] = {'count': 0, '__diff__':-bar['count']}
    result = []
    for metric in sorted(merged_list.keys()):
        result.append({'metric':metric, 'count':merged_list[metric]['count'], '__diff__':merged_list[metric]['__diff__']})
    return result