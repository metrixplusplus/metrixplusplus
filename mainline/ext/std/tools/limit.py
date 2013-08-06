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

import mpp.api
import mpp.utils
import mpp.cout

class Plugin(mpp.api.Plugin, mpp.api.IConfigurable, mpp.api.IRunable):
    
    def declare_configuration(self, parser):
        parser.add_option("--hotspots", "--hs", default=None, help="If not set (none), all exceeded limits are printed."
                          " If set, exceeded limits are sorted (the worst is the first) and only first HOTSPOTS limits are printed."
                          " [default: %default]", type=int)
        parser.add_option("--disable-suppressions", "--ds", action="store_true", default=False,
                          help = "If not set (none), all suppressions are ignored"
                                 " and associated warnings are printed. [default: %default]")
    
    def configure(self, options):
        self.hotspots = options.__dict__['hotspots']
        self.no_suppress = options.__dict__['disable_suppressions']

    def run(self, args):
        return main(self, args)

def main(plugin, args):
    
    exit_code = 0

    loader_prev = plugin.get_plugin_loader().get_plugin('mpp.dbf').get_loader_prev()
    loader = plugin.get_plugin_loader().get_plugin('mpp.dbf').get_loader()
    warn_plugin = plugin.get_plugin_loader().get_plugin('mpp.warn')
    
    paths = None
    if len(args) == 0:
        paths = [""]
    else:
        paths = args

    # Try to optimise iterative change scans
    modified_file_ids = None
    if warn_plugin.mode != warn_plugin.MODE_ALL:
        modified_file_ids = get_list_of_modified_files(loader, loader_prev)
        
    for path in paths:
        path = mpp.utils.preprocess_path(path)
        
        for limit in warn_plugin.iterate_limits():
            logging.info("Applying limit: " + str(limit))
            filters = [limit.filter]
            if modified_file_ids != None:
                filters.append(('file_id', 'IN', modified_file_ids))
            sort_by = None
            limit_by = None
            limit_warnings = None
            if plugin.hotspots != None:
                sort_by = limit.field
                if limit.type == "max":
                    sort_by = "-" + sort_by
                if warn_plugin.mode == warn_plugin.MODE_ALL:
                    # if it is not ALL mode, the tool counts number of printed warnings below
                    limit_by = plugin.hotspots
                limit_warnings = plugin.hotspots
            selected_data = loader.load_selected_data(limit.namespace,
                                                   fields = [limit.field],
                                                   path=path,
                                                   filters = filters,
                                                   sort_by=sort_by,
                                                   limit_by=limit_by)
            if selected_data == None:
                mpp.utils.report_bad_path(path)
                exit_code += 1
                continue
            
            for select_data in selected_data:
                if limit_warnings != None and limit_warnings <= 0:
                    break
                
                is_modified = None
                diff = None
                file_data = loader.load_file_data(select_data.get_path())
                file_data_prev = loader_prev.load_file_data(select_data.get_path())
                if file_data_prev != None:
                    if file_data.get_checksum() == file_data_prev.get_checksum():
                        diff = 0
                        is_modified = False
                    else:
                        matcher = mpp.utils.FileRegionsMatcher(file_data, file_data_prev)
                        prev_id = matcher.get_prev_id(select_data.get_region().get_id())
                        if matcher.is_matched(select_data.get_region().get_id()):
                            if matcher.is_modified(select_data.get_region().get_id()):
                                is_modified = True
                            else:
                                is_modified = False
                            diff = mpp.api.DiffData(select_data,
                                                           file_data_prev.get_region(prev_id)).get_data(limit.namespace, limit.field)

                if (warn_plugin.is_mode_matched(limit.limit,
                                                select_data.get_data(limit.namespace, limit.field),
                                                diff,
                                                is_modified) == False):
                    continue
                
                is_sup = is_metric_suppressed(limit.namespace, limit.field, loader, select_data)
                if is_sup == True and plugin.no_suppress == False:
                    continue    
                
                exit_code += 1
                region_cursor = 0
                region_name = None
                if select_data.get_region() != None:
                    region_cursor = select_data.get_region().cursor
                    region_name = select_data.get_region().name
                report_limit_exceeded(select_data.get_path(),
                                  region_cursor,
                                  limit.namespace,
                                  limit.field,
                                  region_name,
                                  select_data.get_data(limit.namespace, limit.field),
                                  diff,
                                  limit.limit,
                                  is_modified,
                                  is_sup)
                if limit_warnings != None:
                    limit_warnings -= 1
    return exit_code


def get_list_of_modified_files(loader, loader_prev):
    logging.info("Identifying changed files...")
    
    old_files_map = {}
    for each in loader_prev.iterate_file_data():
        old_files_map[each.get_path()] = each.get_checksum()
    if len(old_files_map) == 0:
        return None
    
    modified_file_ids = []
    for each in loader.iterate_file_data():
        if len(modified_file_ids) > 1000: # If more than 1000 files changed, skip optimisation
            return None
        if (each.get_path() not in old_files_map.keys()) or old_files_map[each.get_path()] != each.get_checksum():
            modified_file_ids.append(str(each.get_id()))

    old_files_map = None
            
    if len(modified_file_ids) != 0:
        modified_file_ids = " , ".join(modified_file_ids)
        modified_file_ids = "(" + modified_file_ids + ")"
        return modified_file_ids
    
    return None

def is_metric_suppressed(metric_namespace, metric_field, loader, select_data):
    data = loader.load_file_data(select_data.get_path())
    if select_data.get_region() != None:
        data = data.get_region(select_data.get_region().get_id())
        sup_data = data.get_data('std.suppress', 'list')
    else:
        sup_data = data.get_data('std.suppress.file', 'list')
    if sup_data != None and sup_data.find('[' + metric_namespace + ':' + metric_field + ']') != -1:
        return True
    return False

def report_limit_exceeded(path, cursor, namespace, field, region_name,
                          stat_level, trend_value, stat_limit,
                          is_modified, is_suppressed):
    if region_name != None:
        message = "Metric '" + namespace + ":" + field + "' for region '" + region_name + "' exceeds the limit."
    else:
        message = "Metric '" + namespace + ":" + field + "' exceeds the limit."
    details = [("Metric name", namespace + ":" + field),
               ("Region name", region_name),
               ("Metric value", stat_level),
               ("Modified", is_modified),
               ("Change trend", '{0:{1}}'.format(trend_value, '+' if trend_value else '')),
               ("Limit", stat_limit),
               ("Suppressed", is_suppressed)]
    mpp.cout.notify(path, cursor, mpp.cout.SEVERITY_WARNING, message, details)

    
    
  
