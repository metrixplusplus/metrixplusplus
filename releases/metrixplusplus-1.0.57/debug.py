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
import cgi

import core.log
import core.cmdparser
import core.db.post
import core.db.loader

def main():
    log_plugin = core.log.Plugin()
    db_plugin = core.db.post.Plugin()

    parser = core.cmdparser.MultiOptionParser(usage="Usage: %prog [options] -- [path 1] ... [path N]")
    log_plugin.declare_configuration(parser)
    db_plugin.declare_configuration(parser)
    parser.add_option("-m", "--general.mode", default='dumphtml', choices=['dumphtml'],
                         help="'dumphtml' - prints html code with code highlights for each given path [default: %default]")

    (options, args) = parser.parse_args()
    log_plugin.configure(options)
    db_plugin.configure(options)

    loader = core.db.loader.Loader()
    loader.open_database(db_plugin.dbfile)

    if options.__dict__['general.mode'] == 'dumphtml':
        return dumphtml(args, loader)
    
    assert(False)    
    
def dumphtml(args, loader):
    exit_code = 0
    result = ""
    result += '<html><body>'
    for path in args:
        data = loader.load_file_data(path)
        if data == None:
            logging.error("Specified path '" + path + "' is invalid (not found in the database records)")
            exit_code += 1
            continue
        
        file_name = data.get_path()
        fh = open(file_name, 'r')
        if fh == None:
            logging.error("can not open file '" + path + "' for reading")
            exit_code += 1
            continue
        text = fh.read()
        fh.close()
        
        result += '<table><tr><td><pre>'
        last_pos = 0
        for marker in data.iterate_markers():
            result += (cgi.escape(text[last_pos:marker.begin]))
            if marker.get_type() == data.get_marker_types().STRING:
                result += ('<span style="color:#0000FF">')
            elif marker.get_type() == data.get_marker_types().COMMENT:
                result += ('<span style="color:#009900">')
            elif marker.get_type() == data.get_marker_types().PREPROCESSOR:
                result += ('<span style="color:#990000">')
            result += (cgi.escape(text[marker.begin:marker.end]))
            result += ('</span>')
            last_pos = marker.end
        result += (cgi.escape(text[last_pos:]))
        last_pos = 0
        result += ('</pre></td><td><pre>')
        styles = ['<span style="background-color:#ffff80">', '<span style="background-color:#ff80ff">']
        for item in enumerate(data.iterate_regions(filter_group=data.get_region_types().FUNCTION)):
            reg = item[1]
            result += (cgi.escape(text[last_pos:reg.get_offset_begin()]))
            result += (styles[item[0] % 2])
            result += ('<a href="#line' + str(reg.get_cursor()) + '" id=line"' + str(reg.get_cursor()) + '"></a>')
            result += (cgi.escape(text[reg.get_offset_begin():reg.get_offset_end()]))
            result += ('</span>')
            last_pos = reg.get_offset_end()
        result += (cgi.escape(text[last_pos:]))
        result += ('</pre></td></tr></table>')
    result += ('</body></html>')
    print result
    return exit_code
            
if __name__ == '__main__':
    ts = time.time()
    core.log.set_default_format()
    exit_code = main()
    logging.warning("Exit code: " + str(exit_code) + ". Time spent: " + str(round((time.time() - ts), 2)) + " seconds. Done")
    exit(exit_code) # number of reported messages, errors are reported as non-handled exceptions