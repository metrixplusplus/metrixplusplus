#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#
#    This file is a part of Metrix++ Tool.
#

import logging

from metrixpp.mpp import api
from metrixpp.mpp import utils
from metrixpp.mpp import cout

class Plugin(api.Plugin, api.IRunable):

    def print_warnings(self, args):
        exit_code = 0
        warnings = []

        limit_backend = self.get_plugin('std.tools.limit_backend')

        paths = None
        if len(args) == 0:
            paths = [""]
        else:
            paths = args

        for path in paths:
            path = utils.preprocess_path(path)

            for limit in limit_backend.iterate_limits():
                warns_count = 0
                logging.info("Applying limit: " + str(limit))

                warnings = limit_backend.get_warnings(path, limit)
                if warnings == None:
                    exit_code += 1
                else:
                    for warning in warnings:
                        report_limit_exceeded(warning.path,
                                            warning.cursor,
                                            warning.namespace,
                                            warning.field,
                                            warning.region_name,
                                            warning.stat_level,
                                            warning.trend_value,
                                            warning.stat_limit,
                                            warning.is_modified,
                                            warning.is_suppressed)
                    exit_code += len(warnings)

                cout.notify(path, None, cout.SEVERITY_INFO, "{0} regions exceeded the limit {1}".format(len(warnings), str(limit)))

        return exit_code

    def run(self, args):
        return self.print_warnings(args)

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
    cout.notify(path, cursor, cout.SEVERITY_WARNING, message, details)
