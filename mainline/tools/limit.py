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

import core.log
import core.db.post
import core.utils
import core.cout
import core.warn
import core.cmdparser

import core.utils

import core.api
class Tool(core.api.ITool):
    def run(self, tool_args):
        return main(tool_args)

def main(tool_args):
    
    exit_code = 0
    log_plugin = core.log.Plugin()
    db_plugin = core.db.post.Plugin()
    warn_plugin = core.warn.Plugin()

    parser = core.cmdparser.MultiOptionParser(usage="Usage: %prog limit [options] -- [path 1] ... [path N]")
    log_plugin.declare_configuration(parser)
    db_plugin.declare_configuration(parser)
    warn_plugin.declare_configuration(parser)
    parser.add_option("--hotspots", "--hs", default=None, help="If not set (none), all exceeded limits are printed."
                      " If set, exceeded limits are sorted (the worst is the first) and only first HOTSPOTS limits are printed."
                      " [default: %default]", type=int)
    parser.add_option("--disable-suppressions", "--ds", action="store_true", default=False,
                      help = "If not set (none), all suppressions are ignored"
                             " and associated warnings are printed. [default: %default]")

    (options, args) = parser.parse_args(tool_args)
    log_plugin.configure(options)
    db_plugin.configure(options)
    warn_plugin.configure(options)
    hotspots = options.__dict__['hotspots']
    no_suppress = options.__dict__['disable_suppressions']

    loader_prev = core.api.Loader()
    if db_plugin.dbfile_prev != None:
        if loader_prev.open_database(db_plugin.dbfile_prev) == False:
            parser.error("Can not open file: " + db_plugin.dbfile_prev)

    loader = core.api.Loader()
    if loader.open_database(db_plugin.dbfile) == False:
        parser.error("Can not open file: " + db_plugin.dbfile)
    
    warn_plugin.verify_namespaces(loader.iterate_namespace_names())
    for each in loader.iterate_namespace_names():
        warn_plugin.verify_fields(each, loader.get_namespace(each).iterate_field_names())
    
    # Check for versions consistency
    if db_plugin.dbfile_prev != None:
        core.utils.check_db_metadata(loader, loader_prev)
    
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
        path = core.utils.preprocess_path(path)
        
        for limit in warn_plugin.iterate_limits():
            logging.info("Applying limit: " + str(limit))
            filters = [limit.filter]
            if modified_file_ids != None:
                filters.append(('file_id', 'IN', modified_file_ids))
            sort_by = None
            limit_by = None
            if hotspots != None:
                sort_by = limit.field
                if limit.type == "max":
                    sort_by = "-" + sort_by
                limit_by = hotspots
            selected_data = loader.load_selected_data(limit.namespace,
                                                   fields = [limit.field],
                                                   path=path,
                                                   filters = filters,
                                                   sort_by=sort_by,
                                                   limit_by=limit_by)
            if selected_data == None:
                core.utils.report_bad_path(path)
                exit_code += 1
                continue
            
            for select_data in selected_data:
                is_modified = None
                diff = None
                file_data = loader.load_file_data(select_data.get_path())
                file_data_prev = loader_prev.load_file_data(select_data.get_path())
                if file_data_prev != None:
                    if file_data.get_checksum() == file_data_prev.get_checksum():
                        diff = 0
                        is_modified = False
                    else:
                        matcher = core.utils.FileRegionsMatcher(file_data, file_data_prev)
                        prev_id = matcher.get_prev_id(select_data.get_region().get_id())
                        if matcher.is_matched(select_data.get_region().get_id()):
                            if matcher.is_modified(select_data.get_region().get_id()):
                                is_modified = True
                            else:
                                is_modified = False
                            diff = core.api.DiffData(select_data,
                                                           file_data_prev.get_region(prev_id)).get_data(limit.namespace, limit.field)

                if (warn_plugin.is_mode_matched(limit.limit,
                                                select_data.get_data(limit.namespace, limit.field),
                                                diff,
                                                is_modified) == False):
                    continue
                
                is_sup = is_metric_suppressed(limit.namespace, limit.field, loader, select_data)
                if is_sup == True and no_suppress == False:
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
    core.cout.notify(path, cursor, core.cout.SEVERITY_WARNING, message, details)

    
    
  
