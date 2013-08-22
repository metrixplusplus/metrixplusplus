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
import mpp.cout

class Plugin(mpp.api.Plugin, mpp.api.IRunable):
    
    def run(self, args):
        loader = self.get_plugin('mpp.dbf').get_loader()
        # get previous db file loader
        loader_prev = self.get_plugin('mpp.dbf').get_loader_prev()
        
        exit_code = 0
        for path in (args if len(args) > 0 else [""]):
            added_lines = 0
            file_iterator = loader.iterate_file_data(path)
            if file_iterator == None:
                mpp.utils.report_bad_path(path)
                exit_code += 1
                continue
            for file_data in file_iterator:
                added_lines += self._compare_file(file_data, loader, loader_prev)
            mpp.cout.notify(path, '', mpp.cout.SEVERITY_INFO,
                            "Change trend report",
                            [('Added lines', added_lines)])
        return exit_code

    def _compare_file(self, file_data, loader, loader_prev):
        # compare file with previous and return number of new lines
        file_data_prev = loader_prev.load_file_data(file_data.get_path())
        if file_data_prev == None:
            return self._sum_file_regions_lines(file_data)
        elif file_data.get_checksum() != file_data_prev.get_checksum():
            return self._compare_file_regions(file_data, file_data_prev)

    def _sum_file_regions_lines(self, file_data):
        # just sum up the metric for all regions
        result = 0
        for region in file_data.iterate_regions():
            result += region.get_data('std.code.lines', 'total')
    
    def _compare_file_regions(self, file_data, file_data_prev):
        # compare every region with previous and return number of new lines
        matcher = mpp.utils.FileRegionsMatcher(file_data, file_data_prev)
        result = 0
        for region in file_data.iterate_regions():
            if matcher.is_matched(region.get_id()) == False:
                # if added region, just add the lines
                result += region.get_data('std.code.lines', 'total')
            elif matcher.is_modified(region.get_id()):
                # if modified, add the difference in lines
                region_prev = file_data_prev.get_region(
                    matcher.get_prev_id(region.get_id()))
                result += (region.get_data('std.code.lines', 'total') -
                           region_prev.get_data('std.code.lines', 'total'))
        return result
