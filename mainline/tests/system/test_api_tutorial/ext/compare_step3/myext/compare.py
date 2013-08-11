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
import mpp.utils
# load standard routines to print to stdout
import mpp.cout

class Plugin(mpp.api.Plugin, mpp.api.IRunable):
    
    def run(self, args):
        loader = self.get_plugin('mpp.dbf').get_loader()
        # get previous db file loader
        loader_prev = self.get_plugin('mpp.dbf').get_loader_prev()
        
        paths = None
        if len(args) == 0:
            paths = [""]
        else:
            paths = args

        exit_code = 0
        for path in paths:
            file_iterator = loader.iterate_file_data(path)
            if file_iterator == None:
                mpp.utils.report_bad_path(path)
                exit_code += 1
                continue
            for file_data in file_iterator:
                # compare here with previous and notify about changes
                file_data_prev = loader_prev.load_file_data(file_data.get_path())
                if file_data_prev == None:
                    mpp.cout.notify(file_data.get_path(), '', mpp.cout.SEVERITY_INFO,
                                    'File has been added',
                                    [('Checksum', file_data.get_checksum())])
                elif file_data.get_checksum() != file_data_prev.get_checksum():
                    mpp.cout.notify(file_data.get_path(), '', mpp.cout.SEVERITY_INFO,
                                    'File has been changed',
                                    [('New checksum', file_data.get_checksum()),
                                     ('Old checksum', file_data_prev.get_checksum())])
                else:
                    mpp.cout.notify(file_data.get_path(), '', mpp.cout.SEVERITY_INFO,
                                    'File has not been changed',
                                    [('Checksum', file_data.get_checksum())])
        return exit_code

