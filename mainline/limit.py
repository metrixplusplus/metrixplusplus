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

import core.log
import core.db.loader
import core.db.post
import core.db.utils
import core.export.cout
import core.warn
import core.cmdparser


def main():
    
    exit_code = 0
    log_plugin = core.log.Plugin()
    db_plugin = core.db.post.Plugin()
    warn_plugin = core.warn.Plugin()

    parser = core.cmdparser.MultiOptionParser(usage="Usage: %prog [options] -- <path 1> ... <path N>")
    log_plugin.declare_configuration(parser)
    db_plugin.declare_configuration(parser)
    warn_plugin.declare_configuration(parser)

    (options, args) = parser.parse_args()
    log_plugin.configure(options)
    db_plugin.configure(options)
    warn_plugin.configure(options)

    loader_prev = core.db.loader.Loader()
    if db_plugin.dbfile_prev != None:
        loader_prev.open_database(db_plugin.dbfile_prev)

    loader = core.db.loader.Loader()
    loader.open_database(db_plugin.dbfile)
    
    warn_plugin.verify_namespaces(loader.iterate_namespace_names())
    for each in loader.iterate_namespace_names():
        warn_plugin.verify_fields(each, loader.get_namespace(each).iterate_field_names())
    
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
        logging.info("Processing: " + path)
        
        for limit in warn_plugin.iterate_limits():
            logging.info("Applying limit: " + str(limit))
            filters = [limit.filter]
            if modified_file_ids != None:
                filters.append(('file_id', 'IN', modified_file_ids))
            selected_data = loader.load_selected_data(limit.namespace,
                                                   fields = [limit.field],
                                                   path=path,
                                                   filters = filters)
            if selected_data == None:
                logging.error("Specified path '" + path + "' is invalid (not found in the database records)")
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
                        matcher = core.db.utils.FileRegionsMatcher(file_data, file_data_prev)
                        prev_id = matcher.get_prev_id(select_data.get_region().get_id())
                        if matcher.is_matched(select_data.get_region().get_id()):
                            if matcher.is_modified(select_data.get_region().get_id()):
                                is_modified = True
                            else:
                                is_modified = False
                            diff = core.db.loader.DiffData(select_data,
                                                           file_data_prev.get_region(prev_id)).get_data(limit.namespace, limit.field)
                            # TODO if diff is None, probably need to warn about this
                            # a user may expect data available

                if warn_plugin.is_mode_matched(limit.limit, select_data.get_data(limit.namespace, limit.field), diff, is_modified):
                    exit_code += 1
                    region_cursor = 0
                    region_name = ""
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
                                      is_modified)
    return exit_code


def get_list_of_modified_files(loader, loader_prev):
    modified_file_ids = []
    logging.info("Identifying changed files...")
    
    old_files_map = {}
    for each in loader_prev.iterate_file_data():
        old_files_map[each.get_path()] = each.get_checksum()
    if len(old_files_map) == 0:
        return None
    
    for each in loader.iterate_file_data():
        if len(modified_file_ids) > 1000: # If more than 1000 files changed, skip optimisation
            modified_file_ids = None
            break
        if (each.get_path() not in old_files_map.keys()) or old_files_map[each.get_path()] != each.get_checksum():
            modified_file_ids.append(each.get_id())
            
    if modified_file_ids != None:
        modified_file_ids = " , ".join(modified_file_ids)
        modified_file_ids = "(" + modified_file_ids + ")"
    old_files_map = None
    
    return modified_file_ids
    

def report_limit_exceeded(path, cursor, namespace, field, region_name, stat_level, trend_value, stat_limit, is_modified):
    message = "Metric '" + namespace + "/" + field + "' for region '" + region_name + "' exceeds the limit."
    details = [("Metric name", namespace + "/" + field),
               ("Region name", region_name),
               ("Metric value", stat_level),
               ("Modified", is_modified),
               ("Change trend", '{0:{1}}'.format(trend_value, '+' if trend_value else '')),
               ("Limit", stat_limit)]
    core.export.cout.cout(path, cursor, core.export.cout.SEVERITY_WARNING, message, details)

if __name__ == '__main__':
    ts = time.time()
    core.log.set_default_format()
    exit_code = main()
    logging.warning("Exit code: " + str(exit_code) + ". Time spent: " + str(round((time.time() - ts), 2)) + " seconds. Done")
    exit(exit_code)
    
    
  
