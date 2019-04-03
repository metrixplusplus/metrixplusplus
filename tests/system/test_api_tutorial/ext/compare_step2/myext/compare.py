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
# load common utils for post processing tools
import mpp.utils

class Plugin(mpp.api.Plugin, mpp.api.IRunable):
    
    def run(self, args):
        # get data file reader using standard metrix++ plugin
        loader = self.get_plugin('mpp.dbf').get_loader()
        
        # iterate and print file length for every path in args
        exit_code = 0
        for path in (args if len(args) > 0 else [""]):
            file_iterator = loader.iterate_file_data(path)
            if file_iterator == None:
                mpp.utils.report_bad_path(path)
                exit_code += 1
                continue
            for file_data in file_iterator:
                print file_data.get_path()
        return exit_code

