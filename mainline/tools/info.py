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
import mpp.db.post
import mpp.log
import mpp.cmdparser

import mpp.utils

class Tool(mpp.api.ITool):
    def run(self, tool_args):
        return main(tool_args)

def main(tool_args):
    exit_code = 0
    log_plugin = mpp.log.Plugin()
    db_plugin = mpp.db.post.Plugin()

    parser = mpp.cmdparser.MultiOptionParser(usage="Usage: %prog info [options] -- [path 1] ... [path N]")
    log_plugin.declare_configuration(parser)
    db_plugin.declare_configuration(parser)

    (options, args) = parser.parse_args(tool_args)
    log_plugin.configure(options)
    db_plugin.configure(options)
    
    log_plugin.initialize()
    db_plugin.initialize()

    loader_prev = db_plugin.get_loader_prev(none_if_empty=True)
    loader = db_plugin.get_loader()

    print "Properties:"
    for each in loader.iterate_properties():
        prev_value_str = ""
        if loader_prev != None:
            prev = loader_prev.get_property(each.name)
            if prev == None:
                prev_value_str = " [new]"
                print "(!)",
            elif prev != each.value:
                prev_value_str = " [modified (was: " + loader_prev.get_property(each.name) + ")]"
                print "(!)",
        print "\t" + each.name + "\t=>\t" + each.value + prev_value_str

    print "\nMetrics:"
    for each in sorted(loader.iterate_namespace_names()):
        for field in sorted(loader.get_namespace(each).iterate_field_names()):
            prev_value_str = ""
            if loader_prev != None:
                prev = None
                prev_namespace = loader_prev.get_namespace(each)
                if prev_namespace != None:
                    prev = prev_namespace.get_field_packager(field)
                if prev == None:
                    prev_value_str = " [new]"
                    print "(!)",
            print "\t" + each + ":" + field + prev_value_str

    print "\nFiles:"
    paths = None
    if len(args) == 0:
        paths = [""]
    else:
        paths = args
    for path in paths:
        path = mpp.utils.preprocess_path(path)

        file_iterator = loader.iterate_file_data(path=path)
        if file_iterator == None:
            mpp.utils.report_bad_path(path)
            exit_code += 1
            continue
        for each in file_iterator:
            prev_value_str = ""
            if loader_prev != None:
                prev = loader_prev.load_file_data(each.get_path())
                if prev == None:
                    prev_value_str = " [new]"
                    print "(!)",
                elif prev.get_checksum() != each.get_checksum():
                    prev_value_str = " [modified]"
                    print "(!)",
            print "\t" + each.get_path() + prev_value_str
        
    return exit_code
            
