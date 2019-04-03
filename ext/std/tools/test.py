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

import subprocess
import os.path
import itertools

class Plugin(mpp.api.Plugin, mpp.api.IConfigurable, mpp.api.IRunable):
    
    def declare_configuration(self, parser):
        parser.add_option("-g", "--generate-golds", "--gg", action="store_true", default=False,
                         help="If the option is set (True), new gold files are generated (replacing existing) [default: %default]")
    
    def configure(self, options):
        self.generate_golds = options.__dict__['generate_golds']

    def run(self, args):
        exit_code = 0
    
        os.environ['METRIXPLUSPLUS_TEST_GENERATE_GOLDS'] = str(self.generate_golds)
        os.environ['METRIXPLUSPLUS_TEST_MODE'] = str("True")
        
        tests_dir = os.path.join(os.environ['METRIXPLUSPLUS_INSTALL_DIR'], 'tests')
        process_data= ["python", "-m", "unittest", "discover", "-v", "-s"]
        if len(args) == 0 or tests_dir == os.path.abspath(args[0]):
            for fname in os.listdir(tests_dir):
                full_path = os.path.join(tests_dir, fname)
                if os.path.isdir(full_path) and fname != "sources":
                    exit_code += subprocess.call(itertools.chain(process_data, [full_path]),
                                                 cwd=os.environ['METRIXPLUSPLUS_INSTALL_DIR'])
        else:
            for arg in args:
                if os.path.isdir(arg):
                    exit_code += subprocess.call(itertools.chain(process_data, [arg]),
                                                 cwd=os.environ['METRIXPLUSPLUS_INSTALL_DIR'])
                else:
                    dir_name = os.path.dirname(arg)
                    file_name = os.path.basename(arg)
                    exit_code += subprocess.call(itertools.chain(process_data, [dir_name, "-p", file_name]),
                                                 cwd=os.environ['METRIXPLUSPLUS_INSTALL_DIR'])
        return exit_code
