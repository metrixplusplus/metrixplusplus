#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

import logging
import re
import pytablewriter

import mpp.api
import mpp.utils
import mpp.cout

DIGIT_COUNT = 8

class Plugin(mpp.api.Plugin, mpp.api.IConfigurable, mpp.api.IRunable):

    MODE_NEW = 0x01
    MODE_TREND = 0x03
    MODE_TOUCHED = 0x07
    MODE_ALL = 0x15

    def declare_configuration(self, parser):
        self.parser = parser
        parser.add_option("--output-dir", "--od", default='./metrixpp/',
                           help="Set the output folder. [default: %default].")
        parser.add_option("--format", "--ft", default='txt', choices=['txt', 'md', 'html', 'rst', 'latex'],
                          help="Format of the output data. "
                          "Possible values are 'txt', 'md', 'html' or 'rst' [default: %default]")
        parser.add_option("--disable-suppressions", "--ds", action="store_true", default=False,
                          help = "If not set (none), all suppressions are ignored"
                                 " and associated warnings are printed. [default: %default]")
        parser.add_option("--warn-mode", "--wm", default='all', choices=['new', 'trend', 'touched', 'all'],
                         help="Defines the warnings mode. "
                         "'all' - all warnings active, "
                         "'new' - warnings for new regions/files only, "
                         "'trend' - warnings for new regions/files and for bad trend of modified regions/files, "
                         "'touched' - warnings for new and modified regions/files "
                         "[default: %default]")
        parser.add_option("--min-limit", "--min", action="multiopt",
                          help="A threshold per 'namespace:field' metric in order to select regions, "
                          "which have got metric value less than the specified limit. "
                          "This option can be specified multiple times, if it is necessary to apply several limits. "
                          "Should be in the format: <namespace>:<field>:<limit-value>[:region_type[,region_type]], for example: "
                          "'std.code.lines:comments:1', or 'std.code.lines:comments:1:function,class'. "
                          "Region types is optional specifier, and if not defined the limit is applied to regions of all types.")
        parser.add_option("--max-limit", "--max", action="multiopt",
                          help="A threshold per 'namespace:field' metric in order to select regions, "
                          "which have got metric value more than the specified limit. "
                          "This option can be specified multiple times, if it is necessary to apply several limits. "
                          "Should be in the format: <namespace>:<field>:<limit-value>[:region_type[,region_type]], for example: "
                          "'std.code.complexity:cyclomatic:7', or 'std.code.complexity:maxdepth:5:function'. "
                          "Region types is optional specifier, and if not defined the limit is applied to regions of all types.")

    def configure(self, options):
        self.out_dir = options.__dict__['output_dir']
        self.out_format = options.__dict__['format']
        self.no_suppress = options.__dict__['disable_suppressions']

        if options.__dict__['warn_mode'] == 'new':
            self.mode = self.MODE_NEW
        elif options.__dict__['warn_mode'] == 'trend':
            self.mode = self.MODE_TREND
        elif options.__dict__['warn_mode'] == 'touched':
            self.mode = self.MODE_TOUCHED
        elif options.__dict__['warn_mode'] == 'all':
            self.mode = self.MODE_ALL

        if self.mode != self.MODE_ALL and options.__dict__['db_file_prev'] == None:
            self.parser.error("option --warn-mode: The mode '" + options.__dict__['warn_mode'] + "' requires '--db-file-prev' option set")

        class Limit(object):
            def __init__(self, limit_type, limit, namespace, field, db_filter, region_types, original):
                self.type = limit_type
                self.limit = limit
                self.namespace = namespace
                self.field = field
                self.filter = db_filter
                self.region_types = region_types
                self.original = original

            def __repr__(self):
                return "'{0}:{1}' {2} {3} [applied to '{4}' region type(s)]".format(
                    self.namespace, self.field, self.filter[1], self.limit,
                    mpp.api.Region.T().to_str(self.region_types))

        self.limits = []
        pattern = re.compile(r'''([^:]+)[:]([^:]+)[:]([-+]?[0-9]+(?:[.][0-9]+)?)(?:[:](.+))?''')
        if options.__dict__['max_limit'] != None:
            for each in options.__dict__['max_limit']:
                match = re.match(pattern, each)
                if match == None:
                    self.parser.error("option --max-limit: Invalid format: " + each)
                region_types = 0x00
                if match.group(4) != None:
                    for region_type in match.group(4).split(','):
                        region_type = region_type.strip()
                        group_id = mpp.api.Region.T().from_str(region_type)
                        if group_id == None:
                            self.parser.error(
                                "option --max-limit: uknown region type (allowed: global, class, struct, namespace, function, interface, any): " + region_type)
                        region_types |= group_id
                else:
                    region_types = mpp.api.Region.T().ANY
                limit = Limit("max", float(match.group(3)), match.group(1), match.group(2),
                              (match.group(2), '>', float(match.group(3))), region_types, each)
                self.limits.append(limit)
        if options.__dict__['min_limit'] != None:
            for each in options.__dict__['min_limit']:
                match = re.match(pattern, each)
                if match == None:
                    self.parser.error("option --min-limit: Invalid format: " + each)
                region_types = 0x00
                if match.group(4) != None:
                    for region_type in match.group(4).split(','):
                        region_type = region_type.strip()
                        group_id = mpp.api.Region.T().from_str(region_type)
                        if group_id == None:
                            self.parser.error(
                                "option --max-limit: uknown region type (allowed: global, class, struct, namespace, function, interface, any): " + region_type)
                        region_types |= group_id
                else:
                    region_types = mpp.api.Region.T().ANY
                limit = Limit("min", float(match.group(3)), match.group(1), match.group(2),
                              (match.group(2), '<', float(match.group(3))), region_types, each)
                self.limits.append(limit)

    def initialize(self):
        super(Plugin, self).initialize()
        db_loader = self.get_plugin('mpp.dbf').get_loader()
        self._verify_namespaces(db_loader.iterate_namespace_names())
        for each in db_loader.iterate_namespace_names():
            self._verify_fields(each, db_loader.get_namespace(each).iterate_field_names())

    def _verify_namespaces(self, valid_namespaces):
        valid = []
        for each in valid_namespaces:
            valid.append(each)
        for each in self.limits:
            if each.namespace not in valid:
                self.parser.error("option --{0}-limit: metric '{1}:{2}' is not available in the database file.".
                                  format(each.type, each.namespace, each.field))

    def _verify_fields(self, namespace, valid_fields):
        valid = []
        for each in valid_fields:
            valid.append(each)
        for each in self.limits:
            if each.namespace == namespace:
                if each.field not in valid:
                    self.parser.error("option --{0}-limit: metric '{1}:{2}' is not available in the database file.".
                                      format(each.type, each.namespace, each.field))

    def iterate_limits(self):
        for each in self.limits:
            yield each

    def is_mode_matched(self, limit, value, diff, is_modified):
        if is_modified == None:
            # means new region, True in all modes
            return True
        if self.mode == self.MODE_ALL:
            return True
        if self.mode == self.MODE_TOUCHED and is_modified == True:
            return True
        if self.mode == self.MODE_TREND and is_modified == True:
            if limit < value and diff > 0:
                return True
            if limit > value and diff < 0:
                return True
        return False

    def run(self, args):
        return main(self, args)

        def run(self, args):
            return main(self, args)

def loadSubdirs(loader, path, subdirs, subfiles):

    aggregated_data = loader.load_aggregated_data(path)

    if not aggregated_data:
        return subdirs, subfiles

    for subfile in aggregated_data.get_subfiles():
        subfiles.append(aggregated_data.path + "/" + subfile)

    for subdir in aggregated_data.get_subdirs():
        subdir = aggregated_data.path + "/" + subdir
        subdirs.append(subdir)
        subdirs, subfiles = loadSubdirs(loader, subdir, subdirs, subfiles)
    return subdirs, subfiles

def main(plugin, args):

    exit_code = 0

    data = {"fileMetrixList" : [],
            "regionMetrixList" : [],
            "files" : []}

    loader_prev = plugin.get_plugin('mpp.dbf').get_loader_prev()
    loader = plugin.get_plugin('mpp.dbf').get_loader()

    paths = None
    if len(args) == 0:
        subdirs, paths = loadSubdirs(loader, ".", [], [])
    else:
        paths = args

    # Try to optimise iterative change scans
    modified_file_ids = None
    if plugin.mode != plugin.MODE_ALL:
        modified_file_ids = get_list_of_modified_files(loader, loader_prev)

    for path in paths:
        path = mpp.utils.preprocess_path(path)

        aggregated_data = loader.load_aggregated_data(path)
        file_data = loader.load_file_data(path)

        for key in aggregated_data.data:
            if not key in data["fileMetrixList"]:
                data["fileMetrixList"].append(key)

        file = {"path" : path,
                "file_id" : file_data.file_id,
                "regions" : [],
                "data" : aggregated_data.data}

        data["files"].append(file)

        for reg in file_data.iterate_regions():
            region = {"name" : reg.name,
                      "region_id" : reg.region_id,
                      "line_begin" : reg.line_begin,
                      "data" : reg.get_data_tree()}

            file["regions"].append(region)

            for key in region["data"]:
                if not key in data["regionMetrixList"]:
                    data["regionMetrixList"].append(key)

        for limit in plugin.iterate_limits():
            warns_count = 0
            logging.info("Applying limit: " + str(limit))
            filters = [limit.filter]
            if modified_file_ids != None:
                filters.append(('file_id', 'IN', modified_file_ids))
            sort_by = None
            limit_by = None

            selected_data = loader.load_selected_data(limit.namespace,
                                                      fields=[limit.field],
                                                      path=path,
                                                      filters=filters,
                                                      sort_by=sort_by,
                                                      limit_by=limit_by)
            if selected_data == None:
                mpp.utils.report_bad_path(path)
                exit_code += 1
                continue

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
                                                    file_data_prev.get_region(prev_id)).get_data(limit.namespace,
                                                                                                 limit.field)

                if (plugin.is_mode_matched(limit.limit,
                                           select_data.get_data(limit.namespace, limit.field),
                                           diff,
                                           is_modified) == False):
                    continue

                is_sup = is_metric_suppressed(limit.namespace, limit.field, loader, select_data)

                #  add a warning flag to the metric
                for file in data["files"]:
                    if file["path"] == select_data.get_path():
                        for region in file["regions"]:
                            if region["region_id"] == select_data.region_id:
                                for metric in region["data"]:
                                    if metric == limit.namespace:
                                        region["data"][metric]["warning"] = True
                                        region["data"][metric]["suppressed"] = is_sup

                if is_sup == True and plugin.no_suppress == False:
                    continue

                warns_count += 1
                exit_code += 1

    writer = pytablewriter.SpaceAlignedTableWriter()
    writer.headers = ["file"] + data["fileMetrixList"]

    matrix = [];

    for file in data["files"]:
        line = []
        line.append(file["path"])
        for metric in data["fileMetrixList"]:
            if metric in file["data"]:
                for value in file["data"][metric].values():
                    values = []
                    values.append(value["min"])
                    values.append(value["max"])
                    values.append(value["avg"])
                    values.append(value["total"])
                    values.append(value["count"])
                    line.append(values)
                    break
            else:
                line.append("---")
        matrix.append(line)

        writer.table_name = file["path"]
        writer.value_matrix = matrix
        writer.write_table()

    writer = pytablewriter.SpaceAlignedTableWriter()
    writer.headers = ["line", "name"] + data["regionMetrixList"]

    matrix = [];

    for file in data["files"]:
        for region in file["regions"]:
            line =  []
            line.append(str(region["line_begin"]))
            line.append(region["name"])
            for metric in data["regionMetrixList"]:
                if metric in region["data"]:
                    for value in region["data"][metric].values():
                        line.append(str(value))
                        break
                else:
                    line.append("---")
            matrix.append(line)

        writer.table_name = file["path"]
        writer.value_matrix = matrix
        writer.write_table()

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
        if len(modified_file_ids) > 1000:  # If more than 1000 files changed, skip optimisation
            return None
        if (each.get_path() not in list(old_files_map.keys())) or old_files_map[
            each.get_path()] != each.get_checksum():
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
