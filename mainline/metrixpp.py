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


import time
import sys
import logging
import os
import subprocess
import itertools

import core.log

def main():
    
    os.environ['METRIXPLUSPLUS_INSTALL_DIR'] = os.path.dirname(os.path.abspath(__file__))
    
    available_tools = []
    for fname in os.listdir(os.path.join(os.environ['METRIXPLUSPLUS_INSTALL_DIR'], 'tools')):
        tool_name = os.path.splitext(fname)[0]
        if tool_name == '__init__':
            continue
        if tool_name not in available_tools:
            available_tools.append(tool_name)

    exemode = None
    if len(sys.argv[1:]) != 0:
        exemode = sys.argv[1]
    if exemode != "-R" and exemode != "-D":
        exemode = '-D' # TODO implement install and release mode
        # inject '-D' or '-R' option
        exit(subprocess.call(itertools.chain([sys.executable, sys.argv[0], '-D'], sys.argv[1:])))

    command = ""
    if len(sys.argv[1:]) > 1:
        command = sys.argv[2]
        
    if command not in available_tools:
        logging.error("Unknown action: " + str(command))
        print "Usage: %prog <action> --help"
        print "   or: %prog <action> [options] -- [path 1] ... [path N]"
        print "where: actions are:"
        for each in available_tools:
            print "\t" + each
        return 1

    tool = __import__('tools', globals(), locals(), [command], -1)
    module_attr = tool.__getattribute__(command)
    class_attr = module_attr.__getattribute__('Tool')
    instance = class_attr.__new__(class_attr)
    instance.__init__()
    return instance.run(sys.argv[3:])
            
if __name__ == '__main__':
    ts = time.time()
    core.log.set_default_format()
    exit_code = main()
    logging.warning("Exit code: " + str(exit_code) + ". Time spent: " + str(round((time.time() - ts), 2)) + " seconds. Done")
    exit(exit_code)