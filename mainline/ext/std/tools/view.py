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
import mpp.cout

class Plugin(mpp.api.Plugin, mpp.api.IConfigurable, mpp.api.IRunable):
    
    def declare_configuration(self, parser):
        parser.add_option("--format", "--ft", default='txt', choices=['txt', 'xml', 'python'],
                          help="Format of the output data. "
                          "Possible values are 'xml', 'txt' or 'python' [default: %default]")
        parser.add_option("--nest-regions", "--nr", action="store_true", default=False,
                          help="If the option is set (True), data for regions is exported in the form of a tree. "
                          "Otherwise, all regions are exported in plain list. [default: %default]")
        parser.add_option("--max-distribution-rows", "--mdr", type=int, default=20,
                          help="Maximum number of rows in distribution tables. "
                               "If it is set to 0, the tool does not optimize the size of distribution tables [default: %default]")
    
    def configure(self, options):
        self.out_format = options.__dict__['format']
        self.nest_regions = options.__dict__['nest_regions']
        self.dist_columns = options.__dict__['max_distribution_rows']

    def run(self, args):
        loader_prev = self.get_plugin_loader().get_plugin('mpp.dbf').get_loader_prev()
        loader = self.get_plugin_loader().get_plugin('mpp.dbf').get_loader()
    
        paths = None
        if len(args) == 0:
            paths = [""]
        else:
            paths = args
        
        (result, exit_code) = export_to_str(self.out_format,
                                            paths,
                                            loader,
                                            loader_prev,
                                            self.nest_regions,
                                            self.dist_columns)
        print result
        return exit_code

def export_to_str(out_format, paths, loader, loader_prev, nest_regions, dist_columns):
    exit_code = 0
    result = ""
    if out_format == 'xml':
        result += "<export>\n"
    elif out_format == 'python':
        result += "{'export': ["

    for (ind, path) in enumerate(paths):
        path = mpp.utils.preprocess_path(path)
        
        aggregated_data = loader.load_aggregated_data(path)
        aggregated_data_tree = {}
        subdirs = []
        subfiles = []
        if aggregated_data != None:
            aggregated_data_tree = aggregated_data.get_data_tree()
            subdirs = aggregated_data.get_subdirs()
            subfiles = aggregated_data.get_subfiles()
        else:
            mpp.utils.report_bad_path(path)
            exit_code += 1
        aggregated_data_prev = loader_prev.load_aggregated_data(path)
        if aggregated_data_prev != None:
            aggregated_data_tree = append_diff(aggregated_data_tree,
                                           aggregated_data_prev.get_data_tree())
        aggregated_data_tree = compress_dist(aggregated_data_tree, dist_columns)
        
        file_data = loader.load_file_data(path)
        file_data_tree = {}
        if file_data != None:
            file_data_tree = file_data.get_data_tree() 
            file_data_prev = loader_prev.load_file_data(path)
            append_regions(file_data_tree, file_data, file_data_prev, nest_regions)
        
        data = {"info": {"path": path, "id": ind + 1},
                "aggregated-data": aggregated_data_tree,
                "file-data": file_data_tree,
                "subdirs": subdirs,
                "subfiles": subfiles}

        if out_format == 'txt':
            cout_txt(data, loader)
        elif out_format == 'xml':
            result += mpp.utils.serialize_to_xml(data, root_name = "data") + "\n"
        elif out_format == 'python':
            postfix = ""
            if ind < len(paths) - 1:
                postfix = ", "
            result += mpp.utils.serialize_to_python(data, root_name = "data") + postfix

    if out_format == 'xml':
        result += "</export>"
    elif out_format == 'python':
        result += "]}"
        
    return (result, exit_code)

def append_regions(file_data_tree, file_data, file_data_prev, nest_regions):
    regions_matcher = None
    if file_data_prev != None:
        file_data_tree = append_diff(file_data_tree,
                                     file_data_prev.get_data_tree())
        regions_matcher = mpp.utils.FileRegionsMatcher(file_data, file_data_prev)
    
    if nest_regions == False:
        regions = []
        for region in file_data.iterate_regions():
            region_data_tree = region.get_data_tree()
            if regions_matcher != None and regions_matcher.is_matched(region.get_id()):
                region_data_prev = file_data_prev.get_region(regions_matcher.get_prev_id(region.get_id()))
                region_data_tree = append_diff(region_data_tree,
                                               region_data_prev.get_data_tree())
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
        def append_rec(region_id, file_data_tree, file_data, file_data_prev):
            region = file_data.get_region(region_id)
            region_data_tree = region.get_data_tree()
            if regions_matcher != None and regions_matcher.is_matched(region.get_id()):
                region_data_prev = file_data_prev.get_region(regions_matcher.get_prev_id(region.get_id()))
                region_data_tree = append_diff(region_data_tree,
                                               region_data_prev.get_data_tree())
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
                result['subregions'].append(append_rec(sub_id, file_data_tree, file_data, file_data_prev))
            return result
        file_data_tree['regions'] = []
        file_data_tree['regions'].append(append_rec(1, file_data_tree, file_data, file_data_prev))

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
        merged_list[bar['metric']] = {'count': bar['count'], '__diff__':0, 'ratio': bar['ratio']}
    for bar in prev_list:
        if bar['metric'] in merged_list.keys():
            merged_list[bar['metric']]['__diff__'] = \
                merged_list[bar['metric']]['count'] - bar['count']
        else:
            merged_list[bar['metric']] = {'count': 0, '__diff__':-bar['count'], 'ratio': 0}
    result = []
    for metric in sorted(merged_list.keys()):
        result.append({'metric':metric,
                       'count':merged_list[metric]['count'],
                       'ratio':merged_list[metric]['ratio'],
                       '__diff__':merged_list[metric]['__diff__']})
    return result

def compress_dist(data, columns):
    if columns == 0:
        return data
    
    for namespace in data.keys():
        for field in data[namespace].keys():
            metric_data = data[namespace][field]
            distr = metric_data['distribution-bars']
            columns = float(columns) # to trigger floating calculations
            
            if metric_data['count'] == 0:
                continue
            
            new_dist = []
            remaining_count = metric_data['count']
            next_consume = None
            next_bar = None
            max_count = 0
            min_count = 0xFFFFFFFF
            sum_ratio = 0
            for (ind, bar) in enumerate(distr):
                if next_bar == None:
                    # start new bar
                    next_bar = {'count': bar['count'],
                                'ratio': bar['ratio'],
                                'metric_s': bar['metric'],
                                'metric_f': bar['metric']}
                    if '__diff__' in bar.keys():
                        next_bar['__diff__'] = bar['__diff__']
                    next_consume = int(round(remaining_count/ (columns - len(new_dist))))
                else:
                    # merge to existing bar
                    next_bar['count'] += bar['count']
                    next_bar['ratio'] += bar['ratio']
                    next_bar['metric_f'] = bar['metric']
                    if '__diff__' in bar.keys():
                        next_bar['__diff__'] += bar['__diff__']
                
                next_consume -= bar['count']
                if (next_consume <= 0 # consumed enough
                    or (ind + 1) == len(distr)): # or the last bar
                    # append to new distribution
                    if isinstance(next_bar['metric_s'], float):
                        next_bar['metric_s'] = "{0:.4f}".format(next_bar['metric_s'])
                        next_bar['metric_f'] = "{0:.4f}".format(next_bar['metric_f'])
                    else:
                        next_bar['metric_s'] = str(next_bar['metric_s'])
                        next_bar['metric_f'] = str(next_bar['metric_f'])
                    if next_bar['metric_s'] == next_bar['metric_f']:
                        next_bar['metric'] = next_bar['metric_s']
                    else:
                        next_bar['metric'] = next_bar['metric_s'] + "-" + next_bar['metric_f']
                    del next_bar['metric_s']
                    del next_bar['metric_f']
                    new_dist.append(next_bar)
                    sum_ratio += next_bar['ratio']
                    if max_count < next_bar['count']:
                        max_count = next_bar['count']
                    if min_count > next_bar['count'] and next_bar['count'] != 0:
                        min_count = next_bar['count']
                    remaining_count -= next_bar['count']
                    next_bar = None
                    # check that consumed all
                    assert((ind + 1) != len(distr) or remaining_count == 0)

            if (float(max_count - min_count) / metric_data['count'] < 0.05 and
                metric_data['count'] > 1 and
                len(new_dist) > 1):
                # trick here: if all bars are even in the new distribution
                # it is better to do linear compression instead
                new_dist = []
                step = int(round(float(metric_data['max'] - metric_data['min']) / columns))
                next_end_limit = metric_data['min']
                next_bar = None
                for (ind, bar) in enumerate(distr):
                    if next_bar == None:
                        # start new bar
                        next_bar = {'count': bar['count'],
                                    'ratio': bar['ratio'],
                                    'metric_s': next_end_limit,
                                    'metric_f': bar['metric']}
                        if '__diff__' in bar.keys():
                            next_bar['__diff__'] = bar['__diff__']
                        next_end_limit += step
                    else:
                        # merge to existing bar
                        next_bar['count'] += bar['count']
                        next_bar['ratio'] += bar['ratio']
                        next_bar['metric_f'] = bar['metric']
                        if '__diff__' in bar.keys():
                            next_bar['__diff__'] += bar['__diff__']
                    
                    if (next_bar['metric_f'] >= next_end_limit # consumed enough
                        or (ind + 1) == len(distr)): # or the last bar
                        if (ind + 1) != len(distr):
                            next_bar['metric_f'] = next_end_limit
                        # append to new distribution
                        if isinstance(next_bar['metric_s'], float):
                            next_bar['metric_s'] = "{0:.4f}".format(next_bar['metric_s'])
                            next_bar['metric_f'] = "{0:.4f}".format(next_bar['metric_f'])
                        else:
                            next_bar['metric_s'] = str(next_bar['metric_s'])
                            next_bar['metric_f'] = str(next_bar['metric_f'])
                        next_bar['metric'] = next_bar['metric_s'] + "-" + next_bar['metric_f']
                        del next_bar['metric_s']
                        del next_bar['metric_f']
                        new_dist.append(next_bar)
                        next_bar = None

            data[namespace][field]['distribution-bars'] = new_dist
    return data

def cout_txt_regions(path, regions, indent = 0):
    for region in regions:
        details = [
            ('Region name', region['info']['name']),
            ('Region type', region['info']['type']),
            ('Offsets', str(region['info']['offset_begin']) + "-" + str(region['info']['offset_end'])),
            ('Line numbers', str(region['info']['line_begin']) + "-" + str(region['info']['line_end']))
        ]
        for namespace in region['data'].keys():
            diff_data = {}
            if '__diff__' in region['data'][namespace].keys():
                diff_data = region['data'][namespace]['__diff__']
            for field in region['data'][namespace].keys():
                diff_str = ""
                if field == '__diff__':
                    continue
                if field in diff_data.keys():
                    diff_str = " [" + ("+" if diff_data[field] >= 0 else "") + str(diff_data[field]) + "]"
                details.append((namespace + ":" + field, str(region['data'][namespace][field]) + diff_str))
        mpp.cout.notify(path,
                        region['info']['cursor'],
                        mpp.cout.SEVERITY_INFO,
                        "Metrics per '" + region['info']['name']+ "' region",
                        details,
                        indent=indent)
        if 'subregions' in region.keys():
            cout_txt_regions(path, region['subregions'], indent=indent+1)

def cout_txt(data, loader):
    
    details = []
    for key in data['file-data'].keys():
        if key == 'regions':
            cout_txt_regions(data['info']['path'], data['file-data'][key])
        else:
            namespace = key
            diff_data = {}
            if '__diff__' in data['file-data'][namespace].keys():
                diff_data = data['file-data'][namespace]['__diff__']
            for field in data['file-data'][namespace].keys():
                diff_str = ""
                if field == '__diff__':
                    continue
                if field in diff_data.keys():
                    diff_str = " [" + ("+" if diff_data[field] >= 0 else "") + str(diff_data[field]) + "]"
                details.append((namespace + ":" + field, str(data['file-data'][namespace][field]) + diff_str))
    if len(details) > 0:
        mpp.cout.notify(data['info']['path'],
                    0,
                    mpp.cout.SEVERITY_INFO,
                    "Metrics per file",
                    details)

    attr_map = {'count': 'Measured',
                'total': 'Total',
                'avg': 'Average',
                'min': 'Minimum',
                'max': 'Maximum'}
    for namespace in data['aggregated-data'].keys():
        for field in data['aggregated-data'][namespace].keys():
            details = []
            diff_data = {}
            if '__diff__' in data['aggregated-data'][namespace][field].keys():
                diff_data = data['aggregated-data'][namespace][field]['__diff__']
            for attr in data['aggregated-data'][namespace][field].keys():
                diff_str = ""
                if attr == 'distribution-bars' or attr == '__diff__' or attr == 'count':
                    continue
                if attr in diff_data.keys():
                    diff_str = " [" + ("+" if diff_data[attr] >= 0 else "") + str(diff_data[attr]) + "]"
                details.append((attr_map[attr], str(data['aggregated-data'][namespace][field][attr]) + diff_str))

            measured = data['aggregated-data'][namespace][field]['count']
            if 'count' in diff_data.keys():
                diff_str = ' [{0:{1}}]'.format(diff_data['count'], '+' if diff_data['count'] >= 0 else '')
            count_str_len  = len(str(measured))
            elem_name = 'regions'
            if loader.get_namespace(namespace).are_regions_supported() == False:
                elem_name = 'files'
            details.append(('Distribution', str(measured) + diff_str + ' ' + elem_name + ' measured'))
            details.append(('  Metric value', 'Ratio : R-sum : Number of ' + elem_name))
            sum_ratio = 0
            for bar in data['aggregated-data'][namespace][field]['distribution-bars']:
                sum_ratio += bar['ratio']
                diff_str = ""
                if '__diff__' in bar.keys():
                    diff_str = ' [{0:{1}}]'.format(bar['__diff__'], '+' if bar['__diff__'] >= 0 else '')
                if isinstance(bar['metric'], float):
                    metric_str = "{0:.4f}".format(bar['metric'])
                else:
                    metric_str = str(bar['metric'])
                
                metric_str = (" " * (mpp.cout.DETAILS_OFFSET - len(metric_str) - 1)) + metric_str
                count_str = str(bar['count'])
                count_str = ((" " * (count_str_len - len(count_str))) + count_str + diff_str + "\t")
                details.append((metric_str,
                                "{0:.3f}".format(bar['ratio']) + " : " + "{0:.3f}".format(sum_ratio) +  " : " +
                                count_str + ('|' * int(round(bar['ratio']*100)))))
            mpp.cout.notify(data['info']['path'],
                    '', # no line number
                    mpp.cout.SEVERITY_INFO,
                    "Overall metrics for '" + namespace + ":" + field + "' metric",
                    details)
    details = []
    for each in data['subdirs']:
        details.append(('Directory', each))
    for each in data['subfiles']:
        details.append(('File', each))
    if len(details) > 0: 
        mpp.cout.notify(data['info']['path'],
                '', # no line number
                mpp.cout.SEVERITY_INFO,
                "Directory content:",
                details)
    