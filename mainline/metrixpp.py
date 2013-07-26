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
    
    this_file = os.path.basename(sys.argv[0])
    
    available_tools = []
    excluded_tools = ['utils']
    internal_tools = ['debug', 'test', 'export']
    for fname in os.listdir(os.path.join(os.environ['METRIXPLUSPLUS_INSTALL_DIR'], 'tools')):
        tool_name = os.path.splitext(fname)[0]
        if tool_name == '__init__':
            continue
        if tool_name not in available_tools:
            if tool_name not in excluded_tools + internal_tools:
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
        
    if command == '--help' or command == '-h' or command == '--h':
        print "Usage: python {prog} <action> --help".format(prog=this_file)
        print "   or: python {prog} <action> [options] -- [path 1] ... [path N]".format(prog=this_file)
        print "where: actions are:"
        for each in sorted(available_tools):
            print "\t" + each
        if exemode == '-D':
            for each in sorted(internal_tools):
                print "\t" + each + "\t[internal]"
        exit(0)
        
    if command not in available_tools + internal_tools:
        print >> sys.stderr, "Usage: python {prog} --help\n".format(prog=this_file)
        print >> sys.stderr, "{prog}: error: no such action: {action}".format(prog=this_file, action=command)
        exit(1)

    tool = __import__('tools', globals(), locals(), [command], -1)
    module_attr = tool.__getattribute__(command)
    class_attr = module_attr.__getattribute__('Tool')
    instance = class_attr.__new__(class_attr)
    instance.__init__()
    return instance.run(sys.argv[3:])

def start():
    ts = time.time()
    core.log.set_default_format()
    exit_code = main()
    time_spent = round((time.time() - ts), 2)
    if 'METRIXPLUSPLUS_TEST_GENERATE_GOLDS' in os.environ.keys() and \
        os.environ['METRIXPLUSPLUS_TEST_GENERATE_GOLDS'] == "True":
        time_spent = 1 # Constant value if under tests
    logging.warning("Done (" + str(time_spent) +" seconds). Exit code: " + str(exit_code))
    exit(exit_code)

if __name__ == '__main__':
    start()