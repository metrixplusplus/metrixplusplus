#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

import logging
import sys

from metrixpp.mpp import api
from metrixpp.mpp import utils
from metrixpp.mpp import cout
from metrixpp.mpp import promout

DIGIT_COUNT = 8

class Plugin(api.Plugin, api.IConfigurable, api.IRunable):
    
    MODE_NEW     = 0x01
    MODE_TOUCHED = 0x03
    MODE_ALL     = 0x07

    def declare_configuration(self, parser):
        self.parser = parser
        parser.add_option("--format", "--ft", default='txt', choices=['txt', 'xml', 'python', 'prometheus'],
                          help="Format of the output data. "
                          "Possible values are 'xml', 'txt', 'python' or 'prometheus' [default: %default]")
        parser.add_option("--nest-regions", "--nr", action="store_true", default=False,
                          help="If the option is set (True), data for regions is exported in the form of a tree. "
                          "Otherwise, all regions are exported in plain list. [default: %default]")
        parser.add_option("--max-distribution-rows", "--mdr", type=int, default=20,
                          help="Maximum number of rows in distribution tables. "
                               "If it is set to 0, the tool does not optimize the size of distribution tables [default: %default]")
        parser.add_option("--scope-mode", "--sm", default='all', choices=['new', 'touched', 'all'],
                         help="Defines the analysis scope mode. "
                         "'all' - all available regions and files are taken into account, "
                         "'new' - only new regions and files are taken into account, "
                         "'touched' - only new and modified regions and files are taken into account. "
                         "Modes 'new' and 'touched' may require more time for processing than mode 'all' "
                         "[default: %default]")
    
    def configure(self, options):
        self.out_format = options.__dict__['format']
        self.nest_regions = options.__dict__['nest_regions']
        self.dist_columns = options.__dict__['max_distribution_rows']

        if options.__dict__['scope_mode'] == 'new':
            self.mode = self.MODE_NEW
        elif options.__dict__['scope_mode'] == 'touched':
            self.mode = self.MODE_TOUCHED
        elif options.__dict__['scope_mode'] == 'all':
            self.mode = self.MODE_ALL

        if self.mode != self.MODE_ALL and options.__dict__['db_file_prev'] == None:
            self.parser.error("option --scope-mode: The mode '" + options.__dict__['scope_mode'] + "' requires '--db-file-prev' option set")

    def run(self, args):
        loader_prev = self.get_plugin('metrixpp.mpp.dbf').get_loader_prev()
        loader = self.get_plugin('metrixpp.mpp.dbf').get_loader()
    
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
                                            self.dist_columns,
                                            self.mode)
        print(result)
        return exit_code

def export_to_str(out_format, paths, loader, loader_prev, nest_regions, dist_columns, mode):
    exit_code = 0
    result = ""
    if out_format == 'xml':
        result += "<view>\n"
    elif out_format == 'python':
        result += "{'view': ["

    for (ind, path) in enumerate(paths):
        path = utils.preprocess_path(path)
        
        aggregated_data, aggregated_data_prev = load_aggregated_data_with_mode(loader, loader_prev, path , mode)
        
        aggregated_data_tree = {}
        subdirs = []
        subfiles = []
        if aggregated_data != None:
            aggregated_data_tree = aggregated_data.get_data_tree()
            subdirs = sorted(aggregated_data.get_subdirs())
            subfiles = sorted(aggregated_data.get_subfiles())
        else:
            utils.report_bad_path(path)
            exit_code += 1
        aggregated_data_tree = append_suppressions(path, aggregated_data_tree, loader, mode)

        if aggregated_data_prev != None:
            aggregated_data_prev_tree = aggregated_data_prev.get_data_tree()
            aggregated_data_prev_tree = append_suppressions(path, aggregated_data_prev_tree, loader_prev, mode)
            aggregated_data_tree = append_diff(aggregated_data_tree,
                                               aggregated_data_prev_tree)
            
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
        elif out_format == 'prometheus':
            cout_prom(data, loader)
        elif out_format == 'xml':
            result += utils.serialize_to_xml(data, root_name = "data", digitCount = DIGIT_COUNT) + "\n"
        elif out_format == 'python':
            postfix = ""
            if ind < len(paths) - 1:
                postfix = ", "
            result += utils.serialize_to_python(data, root_name = "data") + postfix

    if out_format == 'xml':
        result += "</view>"
    elif out_format == 'python':
        result += "]}"
        
    return (result, exit_code)

def load_aggregated_data_with_mode(loader, loader_prev, path, mode):
    if mode == Plugin.MODE_ALL:
        aggregated_data = loader.load_aggregated_data(path)
        aggregated_data_prev = loader_prev.load_aggregated_data(path)
    else:
        assert(mode == Plugin.MODE_NEW or mode == Plugin.MODE_TOUCHED)
        
        class AggregatedFilteredData(api.AggregatedData):
            
            def __init__(self, loader, path):
                super(AggregatedFilteredData, self).__init__(loader, path)
                self.in_processing_mode = True
                for name in loader.iterate_namespace_names():
                    namespace = loader.get_namespace(name)
                    for field in namespace.iterate_field_names():
                        if namespace.get_field_python_type(field) == str:
                            # skip string type fields
                            continue
                        self.set_data(name, field, {
                            'count': 0,
                            'nonzero': namespace.is_field_non_zero(field),
                            'min': None,
                            'max': None,
                            'total': 0.0,
                            'avg': None,
                            'distribution-bars': {},
                            'sup': 0
                        })
                        
            def get_data_tree(self, namespaces=None):
                self.in_processing_mode = False
                # need to convert distribution map to a list and calculate average
                for name in loader.iterate_namespace_names():
                    namespace = loader.get_namespace(name)
                    for field in namespace.iterate_field_names():
                        if namespace.get_field_python_type(field) == str:
                            # skip string type fields
                            continue
                        data = self.get_data(name, field)
                        bars_list = []
                        for metric_value in sorted(data['distribution-bars'].keys()):
                            bars_list.append({'metric': metric_value,
                                              'count': data['distribution-bars'][metric_value],
                                              'ratio': ((float(data['distribution-bars'][metric_value]) /
                                                          float(data['count'])))})
                        data['distribution-bars'] = bars_list
                        if data['count'] != 0:
                            data['avg'] = float(data['total']) / float(data['count'])
                        self.set_data(name, field, data)
                return super(AggregatedFilteredData, self).get_data_tree(namespaces=namespaces)
            
            def _append_data(self, orig_data):
                # flag to protect ourselves from getting incomplete data
                # the workflow in this tool: append data first and after get it using get_data_tree()
                assert(self.in_processing_mode == True)
                sup_data = orig_data.get_data('std.suppress', 'list')
                data = orig_data.get_data_tree()
                for namespace in list(data.keys()):
                    for field in list(data[namespace].keys()):
                        aggr_data = self.get_data(namespace, field)
                        metric_value = data[namespace][field]
                        if isinstance(metric_value, str):
                            # skip string type fields
                            continue
                        if aggr_data['min'] == None or aggr_data['min'] > metric_value:
                            aggr_data['min'] = metric_value
                        if aggr_data['max'] == None or aggr_data['max'] < metric_value:
                            aggr_data['max'] = metric_value
                        aggr_data['count'] += 1
                        aggr_data['total'] += metric_value
                        # average is calculated later on get_data_tree
                        if metric_value not in list(aggr_data['distribution-bars'].keys()):
                            aggr_data['distribution-bars'][metric_value] = 0
                        aggr_data['distribution-bars'][metric_value] += 1
                        if sup_data != None:
                            if sup_data.find('[{0}:{1}]'.format(namespace, field)) != -1:
                                aggr_data['sup'] += 1
                        self.set_data(namespace, field, aggr_data)
            
            def _append_file_data(self, file_data):
                self._append_data(file_data)
                for region in file_data.iterate_regions():
                    self._append_data(region)
                
        result = AggregatedFilteredData(loader, path)
        result_prev = AggregatedFilteredData(loader_prev, path)
        
        prev_file_ids = set()
        file_data_iterator = loader.iterate_file_data(path)
        if file_data_iterator != None:
            for file_data in file_data_iterator:
                file_data_prev = loader_prev.load_file_data(file_data.get_path())
                if file_data_prev != None:
                    prev_file_ids.add(file_data_prev.get_id())
                    
                if (file_data_prev == None and (mode == Plugin.MODE_NEW or mode == Plugin.MODE_TOUCHED)):
                    # new file and required mode matched
                    logging.info("Processing: " + file_data.get_path() + " [new]")
                    result._append_file_data(file_data)
                elif (file_data.get_checksum() != file_data_prev.get_checksum()):
                    # modified file and required mode matched
                    logging.info("Processing: " + file_data.get_path() + " [modified]")
                    # append file data without appending regions...
                    if (mode == Plugin.MODE_TOUCHED):
                        # if required mode matched
                        result._append_data(file_data)
                        result_prev._append_data(file_data_prev)
                    # process regions separately
                    matcher = utils.FileRegionsMatcher(file_data, file_data_prev)
                    prev_reg_ids = set()
                    for region in file_data.iterate_regions():
                        prev_id = matcher.get_prev_id(region.get_id())
                        if prev_id != None:
                            prev_reg_ids.add(prev_id)
                        if (matcher.is_matched(region.get_id()) == False and
                            (mode == Plugin.MODE_NEW or mode == Plugin.MODE_TOUCHED)):
                            # new region
                            logging.debug("Processing region: " + region.get_name() + " [new]")
                            result._append_data(region)
                        elif matcher.is_modified(region.get_id()) and mode == Plugin.MODE_TOUCHED:
                            # modified region
                            logging.debug("Processing region: " + region.get_name() + " [modified]")
                            result._append_data(region)
                            result_prev._append_data(file_data_prev.get_region(prev_id))
                            
                    if mode == Plugin.MODE_TOUCHED:
                        for region_prev in file_data_prev.iterate_regions():
                            if region_prev.get_id() not in prev_reg_ids:
                                # deleted region
                                logging.debug("Processing region: " + region_prev.get_name() + " [deleted]")
                                result_prev._append_data(region_prev)
                
        if mode == Plugin.MODE_TOUCHED:
            file_data_prev_iterator = loader_prev.iterate_file_data(path)
            if file_data_prev_iterator != None:
                for file_data_prev in file_data_prev_iterator:
                    if file_data_prev.get_id() not in prev_file_ids:
                        # deleted file and required mode matched
                        logging.info("Processing: " + file_data_prev.get_path() + " [deleted]")
                        result_prev._append_file_data(file_data_prev)

        return (result, result_prev)
            
    return (aggregated_data, aggregated_data_prev)




def append_regions(file_data_tree, file_data, file_data_prev, nest_regions):
    regions_matcher = None
    if file_data_prev != None:
        file_data_tree = append_diff(file_data_tree,
                                     file_data_prev.get_data_tree())
        regions_matcher = utils.FileRegionsMatcher(file_data, file_data_prev)
    
    if nest_regions == False:
        regions = []
        for region in file_data.iterate_regions():
            region_data_tree = region.get_data_tree()
            is_modified = None
            if regions_matcher != None and regions_matcher.is_matched(region.get_id()):
                region_data_prev = file_data_prev.get_region(regions_matcher.get_prev_id(region.get_id()))
                region_data_tree = append_diff(region_data_tree,
                                               region_data_prev.get_data_tree())
                is_modified = regions_matcher.is_modified(region.get_id())
            regions.append({"info": {"name" : region.name,
                                     'type': api.Region.T().to_str(region.get_type()),
                                     'modified': is_modified,
                                     'cursor' : region.cursor,
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
            is_modified = None
            if regions_matcher != None and regions_matcher.is_matched(region.get_id()):
                region_data_prev = file_data_prev.get_region(regions_matcher.get_prev_id(region.get_id()))
                region_data_tree = append_diff(region_data_tree,
                                               region_data_prev.get_data_tree())
                is_modified = regions_matcher.is_modified(region.get_id())
            result = {"info": {"name" : region.name,
                               'type' : api.Region.T().to_str(region.get_type()),
                               'modified': is_modified,
                               'cursor' : region.cursor,
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
    
    for name in list(main_tree.keys()):
        if name not in list(prev_tree.keys()):
            continue
        for field in list(main_tree[name].keys()):
            if field not in list(prev_tree[name].keys()):
                continue
            if isinstance(main_tree[name][field], dict) and isinstance(prev_tree[name][field], dict):
                diff = {}
                for key in list(main_tree[name][field].keys()):
                    if key not in list(prev_tree[name][field].keys()):
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
        merged_list[bar['metric']] = {'count': bar['count'], '__diff__':bar['count'], 'ratio': bar['ratio']}
    for bar in prev_list:
        if bar['metric'] in list(merged_list.keys()):
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

def append_suppressions(path, data, loader, mode):
    if mode == Plugin.MODE_ALL:
        # in other modes, suppressions are appended during data loading
        for namespace in list(data.keys()):
            for field in list(data[namespace].keys()):
                selected_data = loader.load_selected_data('std.suppress',
                                           fields = ['list'],
                                           path=path,
                                           filters = [('list', 'LIKE', '%[{0}:{1}]%'.format(namespace, field))])
                if selected_data == None:
                    data[namespace][field]['sup'] = 0
                else:
                    count = 0
                    for each in selected_data:
                        each = each # used
                        count += 1
                    data[namespace][field]['sup'] = count
    return data

def compress_dist(data, columns):
    if columns == 0:
        return data
    
    for namespace in list(data.keys()):
        for field in list(data[namespace].keys()):
            metric_data = data[namespace][field]
            distr = metric_data['distribution-bars']
            columns = float(columns) # to trigger floating calculations
            
            if metric_data['count'] == 0:
                continue
            
            new_dist = []
            remaining_count = metric_data['count']
            next_consume = None
            next_bar = None
            max_count = -sys.maxsize - 1
            min_count = sys.maxsize
            sum_ratio = 0
            for (ind, bar) in enumerate(distr):
                if next_bar == None:
                    # start new bar
                    next_bar = {'count': bar['count'],
                                'ratio': bar['ratio'],
                                'metric_s': bar['metric'],
                                'metric_f': bar['metric']}
                    if '__diff__' in list(bar.keys()):
                        next_bar['__diff__'] = bar['__diff__']
                    next_consume = int(remaining_count/ (columns - len(new_dist)))
                else:
                    # merge to existing bar
                    next_bar['count'] += bar['count']
                    next_bar['ratio'] += bar['ratio']
                    next_bar['metric_f'] = bar['metric']
                    if '__diff__' in list(bar.keys()):
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
                    if remaining_count == 0:
                        break

            if (float(max_count - min_count) / metric_data['count'] < 0.05 and
                metric_data['count'] > columns and
                len(new_dist) > 1):
                # trick here:
                # if all bars are even in the new distribution AND
                # there are many items in the distribution (> max distribution rows),
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
                        if '__diff__' in list(bar.keys()):
                            next_bar['__diff__'] = bar['__diff__']
                        next_end_limit += step
                    else:
                        # merge to existing bar
                        next_bar['count'] += bar['count']
                        next_bar['ratio'] += bar['ratio']
                        next_bar['metric_f'] = bar['metric']
                        if '__diff__' in list(bar.keys()):
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
            ('Line numbers', str(region['info']['line_begin']) + "-" + str(region['info']['line_end'])),
            ('Modified', str(region['info']['modified']))
        ]
        for namespace in sorted(list(region['data'].keys())):
            diff_data = {}
            if '__diff__' in list(region['data'][namespace].keys()):
                diff_data = region['data'][namespace]['__diff__']
            for field in sorted(list(region['data'][namespace].keys())):
                diff_str = ""
                if field == '__diff__':
                    continue
                if field in list(diff_data.keys()):
                    diff_str = " [" + ("+" if diff_data[field] >= 0 else "") + str(diff_data[field]) + "]"
                details.append((namespace + ":" + field, str(region['data'][namespace][field]) + diff_str))
        cout.notify(path,
                        region['info']['cursor'],
                        cout.SEVERITY_INFO,
                        "Metrics per '" + region['info']['name']+ "' region",
                        details,
                        indent=indent)
        if 'subregions' in list(region.keys()):
            cout_txt_regions(path, region['subregions'], indent=indent+1)

def cout_txt(data, loader):
    
    details = []
    for key in list(data['file-data'].keys()):
        if key == 'regions':
            cout_txt_regions(data['info']['path'], data['file-data'][key])
        else:
            namespace = key
            diff_data = {}
            if '__diff__' in list(data['file-data'][namespace].keys()):
                diff_data = data['file-data'][namespace]['__diff__']
            for field in sorted(list(data['file-data'][namespace].keys())):
                diff_str = ""
                if field == '__diff__':
                    continue
                if field in list(diff_data.keys()):
                    diff_str = " [" + ("+" if diff_data[field] >= 0 else "") + str(diff_data[field]) + "]"
                details.append((namespace + ":" + field, str(data['file-data'][namespace][field]) + diff_str))
    if len(details) > 0:
        cout.notify(data['info']['path'],
                    0,
                    cout.SEVERITY_INFO,
                    "Metrics per file",
                    details)

    attr_map = {'total': 'Total',
                'avg': 'Average',
                'min': 'Minimum',
                'max': 'Maximum',
    }
    for namespace in sorted(list(data['aggregated-data'].keys())):
        for field in sorted(list(data['aggregated-data'][namespace].keys())):
            details = []
            diff_data = {}
            if '__diff__' in list(data['aggregated-data'][namespace][field].keys()):
                diff_data = data['aggregated-data'][namespace][field]['__diff__']
            for attr in ['avg', 'min', 'max', 'total']:
                diff_str = ""
                if attr in list(diff_data.keys()):
                    if isinstance(diff_data[attr], float):
                        diff_str = " [" + ("+" if diff_data[attr] >= 0 else "") + str(round(diff_data[attr], DIGIT_COUNT)) + "]"
                    else:
                        diff_str = " [" + ("+" if diff_data[attr] >= 0 else "") + str(diff_data[attr]) + "]"
                if attr == 'avg' and data['aggregated-data'][namespace][field]['nonzero'] == True:
                    diff_str += " (excluding zero metric values)"
                if isinstance(data['aggregated-data'][namespace][field][attr], float):
                    # round the data to reach same results on platforms with different precision
                    details.append((attr_map[attr], str(round(data['aggregated-data'][namespace][field][attr], DIGIT_COUNT)) + diff_str))
                else:
                    details.append((attr_map[attr], str(data['aggregated-data'][namespace][field][attr]) + diff_str))

            measured = data['aggregated-data'][namespace][field]['count']
            if 'count' in list(diff_data.keys()):
                diff_str = ' [{0:{1}}]'.format(diff_data['count'], '+' if diff_data['count'] >= 0 else '')
            sup_diff_str = ""
            if 'sup' in list(diff_data.keys()):
                sup_diff_str = ' [{0:{1}}]'.format(diff_data['sup'], '+' if diff_data['sup'] >= 0 else '')
            elem_name = 'regions'
            if loader.get_namespace(namespace).are_regions_supported() == False:
                elem_name = 'files'
            details.append(('Distribution',
                            '{0}{1} {2} in total (including {3}{4} suppressed)'.format(measured,
                                                                                   diff_str,
                                                                                   elem_name,
                                                                                   data['aggregated-data'][namespace][field]['sup'],
                                                                                   sup_diff_str)))
            details.append(('  Metric value', 'Ratio : R-sum : Number of ' + elem_name))
            count_str_len  = len(str(measured))
            sum_ratio = 0
            for bar in data['aggregated-data'][namespace][field]['distribution-bars']:
                sum_ratio += bar['ratio']
                diff_str = ""
                if '__diff__' in list(bar.keys()):
                    if bar['__diff__'] >= 0:
                        diff_str = ' [+{0:<{1}}]'.format(bar['__diff__'], count_str_len)
                    else:
                        diff_str = ' [{0:<{1}}]'.format(bar['__diff__'], count_str_len+1)
                if isinstance(bar['metric'], float):
                    metric_str = "{0:.4f}".format(bar['metric'])
                else:
                    metric_str = str(bar['metric'])
                
                metric_str = (" " * (cout.DETAILS_OFFSET - len(metric_str) - 1)) + metric_str
                count_str = str(bar['count'])
                count_str = ((" " * (count_str_len - len(count_str))) + count_str + diff_str + "\t")
                details.append((metric_str,
                                "{0:.3f}".format(bar['ratio']) + " : " + "{0:.3f}".format(sum_ratio) +  " : " +
                                count_str + ('|' * int(bar['ratio']*100))))
            cout.notify(data['info']['path'],
                    '', # no line number
                    cout.SEVERITY_INFO,
                    "Overall metrics for '" + namespace + ":" + field + "' metric",
                    details)
    details = []
    for each in sorted(data['subdirs']):
        details.append(('Directory', each))
    for each in sorted(data['subfiles']):
        details.append(('File', each))
    if len(details) > 0: 
        cout.notify(data['info']['path'],
                '', # no line number
                cout.SEVERITY_INFO,
                "Directory content:",
                details)
    
def cout_prom_regions(path, regions, indent = 0):
    for region in regions:
        details = []
        for namespace in sorted(list(region['data'].keys())):
            diff_data = {}
            if '__diff__' in list(region['data'][namespace].keys()):
                diff_data = region['data'][namespace]['__diff__']
            for field in sorted(list(region['data'][namespace].keys())):
                diff_str = ""
                if field == '__diff__':
                    continue
                if field in list(diff_data.keys()):
                    diff_str = " [" + ("+" if diff_data[field] >= 0 else "") + str(diff_data[field]) + "]"
                details.append((namespace + ":" + field, str(region['data'][namespace][field]) + diff_str))
        promout.notify(path = path,
                        region = region['info']['name'],
                        metric = "",
                        details = details)
        if 'subregions' in list(region.keys()):
            cout_txt_regions(path, region['subregions'], indent=indent+1)
            
def cout_prom(data, loader):
    
    for key in list(data['file-data'].keys()):
        if key == 'regions':
            cout_prom_regions(data['info']['path'], data['file-data'][key])

    for namespace in sorted(list(data['aggregated-data'].keys())):
        for field in sorted(list(data['aggregated-data'][namespace].keys())):
            details = []
            for attr in ['avg', 'min', 'max', 'total']:
                if isinstance(data['aggregated-data'][namespace][field][attr], float):
                    # round the data to reach same results on platforms with different precision
                    details.append((attr, str(round(data['aggregated-data'][namespace][field][attr], DIGIT_COUNT))))
                else:
                    details.append((attr, str(data['aggregated-data'][namespace][field][attr])))

            promout.notify(path = data['info']['path'],
                    metric = namespace + "." + field,
                    details = details)
