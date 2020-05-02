#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

import logging
import re
import os
import pytablewriter

import mpp.api
import mpp.utils
import mpp.cout

DIGIT_COUNT = 8

class Plugin(mpp.api.Plugin, mpp.api.IConfigurable, mpp.api.IRunable):

    def declare_configuration(self, parser):
        self.parser = parser
        parser.add_option("--output-dir", "--od", default='./metrixpp/',
                           help="Set the output folder. [default: %default].")
        parser.add_option("--format", "--ft", default='txt', choices=['txt', 'md', 'html', 'rst', 'latex', 'xlsx', 'doxygen'],
                          help="Format of the output data. "
                          "Possible values are 'txt', 'md', 'html', 'rst', 'latex', 'xlsx' or 'doxygen' [default: %default]")

    def configure(self, options):
        self.out_dir = options.__dict__['output_dir']
        self.out_format = options.__dict__['format']

    def initialize(self):
        super(Plugin, self).initialize()

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

    data = {"fileMetrixList" : {},
            "regionMetrixList" : [],
            "files" : []}

    loader_prev = plugin.get_plugin('mpp.dbf').get_loader_prev()
    loader = plugin.get_plugin('mpp.dbf').get_loader()

    paths = None
    if len(args) == 0:
        subdirs, paths = loadSubdirs(loader, ".", [], [])
    else:
        paths = args

    for path in paths:
        path = mpp.utils.preprocess_path(path)

        aggregated_data = loader.load_aggregated_data(path)
        file_data = loader.load_file_data(path)

        for namespace in aggregated_data.iterate_namespaces():
            for field in aggregated_data.iterate_fields(namespace):
                print(field)

        for key in aggregated_data.data:
            if not key in data["fileMetrixList"]:
                metric = {  "name" : key,
                            "submetrics" : []}
                data["fileMetrixList"][key] = metric
            for subkey in aggregated_data.data[key]:
                if not subkey in data["fileMetrixList"][key]:
                    data["fileMetrixList"][key]["submetrics"].append(subkey)

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
                for subkey in key:
                    if not subkey in data["regionMetrixList"][key]:
                        data["regionMetrixList"][key].append(subkey)

    writer = pytablewriter.ExcelXlsxTableWriter()
    writer.open("index.xlsx")
    writer.make_worksheet("files")
    writer.headers = ["file"] + data["fileMetrixList"]

    matrix = [];

    for file in data["files"]:
        line = []
        line.append("=HYPERLINK(\"#{0}!A1\",\"{0}\")".format(os.path.basename(file["path"])))
        for metric in data["fileMetrixList"]:
            if metric in file["data"]:
                for value in file["data"][metric].values():
                    line.append(value["total"])
                    break
            else:
                line.append("---")
        matrix.append(line)

    #writer.table_name = file["path"]
    #writer.value_matrix = matrix
    #writer.write_table()

    #writer = pytablewriter.ExcelXlsxTableWriter()
    writer.headers = ["file", "line", "name"] + data["regionMetrixList"]

    for file in data["files"]:
        writer.make_worksheet(os.path.basename(file["path"]))
        matrix = [];
        for region in file["regions"]:
            line =  []
            line.append(file["path"])
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

    writer.close()

    return exit_code
