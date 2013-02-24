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
import subprocess
import os.path
import itertools

import core.log
import core.cmdparser

def main():
    exit_code = 0
    log_plugin = core.log.Plugin()

    parser = core.cmdparser.MultiOptionParser(usage="Usage: %prog [options] -- [testgroup-dir-path-1[/testsuite-file-path-1]] ... [...path-N]")
    log_plugin.declare_configuration(parser, default_value='ERROR')

    (options, args) = parser.parse_args()
    log_plugin.configure(options)
    
    install_dir = os.path.dirname(os.path.abspath(__file__))
    tests_dir = os.path.join(install_dir, 'tests')
    os.environ['METRIXPLUSPLUS_INSTALL_DIR'] = install_dir
    process_data= ["python", "-m", "unittest", "discover", "-v", "-s"]
    if len(args) == 0 or tests_dir == os.path.abspath(args[0]):
        for fname in os.listdir(tests_dir):
            full_path = os.path.join(tests_dir, fname)
            if os.path.isdir(full_path):
                exit_code += subprocess.call(itertools.chain(process_data, [full_path]))
    else:
        for arg in args:
            if os.path.isdir(arg):
                exit_code += subprocess.call(itertools.chain(process_data, [arg]))
            else:
                dir_name = os.path.dirname(arg)
                file_name = os.path.basename(arg)
                exit_code += subprocess.call(itertools.chain(process_data, [dir_name, "-p", file_name]))
    return exit_code
            
if __name__ == '__main__':
    ts = time.time()
    core.log.set_default_format()
    exit_code = main()
    logging.warning("Exit code: " + str(exit_code) + ". Time spent: " + str(round((time.time() - ts), 2)) + " seconds. Done")
    exit(exit_code) # number of reported messages, errors are reported as non-handled exceptions