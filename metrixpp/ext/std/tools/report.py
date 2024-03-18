#
#    Metrix++, Copyright 2009-2024, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#
#    This file is a part of Metrix++ Tool.
#

import logging
import os
import pytablewriter

from metrixpp.mpp import api
from metrixpp.mpp import utils

DIGIT_COUNT = 8

class Plugin(api.Plugin, api.IConfigurable, api.IRunable):

    def declare_configuration(self, parser):
        self.parser = parser
        parser.add_option("--output-dir", "--od", default='./metrixpp/',
                           help="Set the output folder. [default: %default].")
        parser.add_option("--format", "--ft", default='txt', choices=['txt', 'doxygen'],
                          help="Format of the output data. "
                          "Possible values are 'txt' or 'doxygen' [default: %default]")

    def configure(self, options):
        self.out_dir = options.__dict__['output_dir']
        self.out_format = options.__dict__['format']

    def initialize(self):
        super(Plugin, self).initialize()

    def loadSubdirs(self, loader, path, subdirs, subfiles):
        aggregated_data = loader.load_aggregated_data(path)

        if not aggregated_data:
            return subdirs, subfiles

        for subfile in aggregated_data.get_subfiles():
            subfiles.append(aggregated_data.path + "/" + subfile)

        for subdir in aggregated_data.get_subdirs():
            subdir = aggregated_data.path + "/" + subdir
            subdirs.append(subdir)
            # recurse for all subdirs and subfiles
            subdirs, subfiles = self.loadSubdirs(loader, subdir, subdirs, subfiles)
        return subdirs, subfiles

    def create_doxygen_report(self, paths, output_dir, overview_data, data):
        exit_code = 1

        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            with open(os.path.join(output_dir, "metrixpp.dox"), mode="w+") as file:
                file.write("/* this file is autogenerated by metrix++ - changes will be overwritten */\n")
                file.write("/*!\n")

                file.write("\\page metrix_overview Metrix overview\n\n")

                file.write("\\section metrix_sec Metrix Warnings\n\n")
                file.write("Metrix Limits exceeded {} times.\n\n".format(len(overview_data["warnings"])))

                if len(overview_data["warnings"]) > 0:
                    file.write("Warning list: \\ref metrix_warnings\n\n")

                for file_data in overview_data["matrix"]:
                    file_data[0] = str(file_data[0]).replace("\\", "/")

                writer = pytablewriter.MarkdownTableWriter()
                writer.table_name = "metrix overview"
                writer.headers = overview_data["fields"]
                writer.value_matrix = overview_data["matrix"]
                writer.margin = 1
                writer.stream = file
                writer.write_table()

                file.write("\n\n")

                for path in paths:

                    file.write("\\file {}\n\n".format(path))

                    writer = pytablewriter.MarkdownTableWriter()
                    writer.table_name = "metrix"
                    writer.headers = data[path]["file_fields"]
                    writer.value_matrix = data[path]["file_matrix"]
                    writer.margin = 1
                    writer.stream = file
                    writer.write_table()

                    file.write("\n")

                    for region in data[path]["region_matrix"]:
                        if region[0] != "-" and region[0] != "__global__":
                            region[0] = "\\ref " + region[0]

                    writer = pytablewriter.MarkdownTableWriter()
                    writer.table_name = "region metrix"
                    writer.headers = data[path]["region_fields"]
                    writer.value_matrix = data[path]["region_matrix"]
                    writer.margin = 1
                    writer.stream = file
                    writer.write_table()

                    file.write("\n")

                    # add warnings as list items
                    for warning in data[path]["warnings"]:
                        warning_text = "Metric '" + warning.namespace + ":" + warning.field + "'"

                        if warning.region_name and warning.region_name != "__global__":
                            warning_text = warning_text + " for region \\ref " + warning.region_name
                        elif warning.region_name == "__global__":
                            warning_text = warning_text + " for region " + warning.region_name
                        else:
                            warning_text = warning_text + " for the file \\ref " + warning.path

                        warning_text = warning_text + " exceeds the limit."

                        if warning.type == "max":
                            warning_comp = ">"
                        else:
                            warning_comp = "<"
                        warning_text = warning_text + " (value: {} {} limit: {})".format(warning.stat_level,
                                                                                         warning_comp,
                                                                                         warning.stat_limit)

                        file.write("\\xrefitem metrix_warnings \"Metrix Warning\" \"Metrix Warnings\" {}\n".format(warning_text))


                    file.write("\n\n")

                file.write("*/\n")
                exit_code = 0
        else:
            logging.error("no output directory set")

        return exit_code

    def run(self, args):
        exit_code = 0

        data = {}
        overview_data = {}

        loader = self.get_plugin('metrixpp.mpp.dbf').get_loader()
        limit_backend = self.get_plugin('std.tools.limit_backend')

        paths = None
        if len(args) == 0:
            subdirs, paths = self.loadSubdirs(loader, ".", [], [])
        else:
            paths = args

        for path in paths:
            path = utils.preprocess_path(path)
            data[path] = {}
            data[path]["file_data"] = {}
            data[path]["file_fields"] = ["warnings"]
            data[path]["file_matrix"] = [[]]
            data[path]["regions"] = {}
            data[path]["region_fields"] = ["region", "warnings"]
            data[path]["region_matrix"] = []
            data[path]["warnings"] = []

            file_data = loader.load_file_data(path)

            # get warnings from limit plugin
            data[path]["warnings"] = limit_backend.get_all_warnings(path)
            # convert paths to increase readability
            for warning in data[path]["warnings"]:
                warning.path = os.path.relpath(warning.path)

            # load file based data
            data_tree = file_data.get_data_tree()
            for namespace in file_data.iterate_namespaces():
                for field in file_data.iterate_fields(namespace):
                    data[path]["file_data"][namespace + "." +  field[0]] = field[1]
                    data[path]["file_fields"].append(namespace + "." +  field[0])

            for field in data[path]["file_fields"]:
                if field == "warnings":
                    data[path]["file_matrix"][0].append(len(data[path]["warnings"]))
                else:
                    data[path]["file_matrix"][0].append(data[path]["file_data"][field])

            # load region based data
            file_data.load_regions()
            for region in file_data.regions:
                data[path]["regions"][region.name] = {}
                data_tree = region.get_data_tree()
                for namespace in region.iterate_namespaces():
                    for field in region.iterate_fields(namespace):
                        data[path]["regions"][region.name][namespace + "." +  field[0]] = field[1]

                        if not (namespace + "." +  field[0]) in data[path]["region_fields"]:
                            data[path]["region_fields"].append(namespace + "." +  field[0])

            # iterate over all found regions in the file
            for region in data[path]["regions"]:
                # add static columns with region name and warning count
                warning_count = sum(warning.region_name == region for warning in data[path]["warnings"])
                region_row = [region, str(warning_count)]

                # start iterating after the static fields
                for field in data[path]["region_fields"][2:]:
                    if field in data[path]["regions"][region]:
                        region_row.append(data[path]["regions"][region][field])
                    else:
                        region_row.append("-")

                data[path]["region_matrix"].append(region_row)

            # assemble overview table
            overview_data["warnings"] = []
            overview_data["fields"] = ["file", "warnings"]
            overview_data["matrix"] = []
            for key, value in data.items():
                for field in value["file_fields"]:
                    if not field in overview_data["fields"]:
                        overview_data["fields"].append(field)

            for key, value in data.items():
                overview_data["warnings"] = overview_data["warnings"] + value["warnings"]
                row = [os.path.relpath(key), len(value["warnings"])]
                for field in overview_data["fields"][2:]:
                    if field in value["file_data"]:
                        row.append(value["file_data"][field])
                    else:
                        row.append("-")

                overview_data["matrix"].append(row)


        if self.out_format == "doxygen":
            exit_code = self.create_doxygen_report(paths,
                                                   self.out_dir,
                                                   overview_data,
                                                   data)
        else:
            logging.error("unknown or no output format set")
            exit_code = 1
            # should default to simple text i guess

        return exit_code
