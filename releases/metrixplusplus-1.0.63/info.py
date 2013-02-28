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

import core.db.loader
import core.db.post
import core.log
import core.cmdparser


def main():
    exit_code = 0
    log_plugin = core.log.Plugin()
    db_plugin = core.db.post.Plugin()

    parser = core.cmdparser.MultiOptionParser(usage="Usage: %prog [options]")
    log_plugin.declare_configuration(parser)
    db_plugin.declare_configuration(parser)

    (options, args) = parser.parse_args()
    log_plugin.configure(options)
    db_plugin.configure(options)
    
    args = args # used

    loader = core.db.loader.Loader()
    loader.open_database(db_plugin.dbfile)
    loader_prev = None
    if db_plugin.dbfile_prev != None:
        loader_prev = core.db.loader.Loader()
        loader_prev.open_database(db_plugin.dbfile_prev)

    print "Properties:"
    for each in loader.iterate_properties():
        prev_value_str = ""
        if loader_prev != None:
            prev = loader_prev.get_property(each.name)
            if prev != each.value:
                prev_value_str = " [previous file: " + loader_prev.get_property(each.name) + "]"
                print "(!)",
        print "\t" + each.name + "\t=>\t" + each.value + prev_value_str

    print "Namespaces:"
    for each in loader.iterate_namespace_names():
        prev_value_str = ""
        if loader_prev != None:
            prev = loader_prev.get_namespace(each)
            if prev == None:
                prev_value_str = " [previous file: missed]"
                print "(!)",
        print "\t" + each + prev_value_str
        for field in loader.get_namespace(each).iterate_field_names():
            prev_value_str = ""
            if loader_prev != None:
                prev = loader_prev.get_namespace(each).get_field_packager(field)
                if prev == None:
                    prev_value_str = " [previous file: missed]"
                    print "(!)",
            print "\t\t- " + field + prev_value_str
        
    return exit_code
            
if __name__ == '__main__':
    ts = time.time()
    core.log.set_default_format()
    exit_code = main()
    logging.warning("Exit code: " + str(exit_code) + ". Time spent: " + str(round((time.time() - ts), 2)) + " seconds. Done")
    exit(exit_code) # number of reported messages, errors are reported as non-handled exceptions