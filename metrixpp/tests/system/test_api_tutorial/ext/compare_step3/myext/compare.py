#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

from metrixpp.mpp import api
from metrixpp.mpp import utils
from metrixpp.mpp import cout

class Plugin(api.Plugin, api.IRunable):
    
    def run(self, args):
        loader = self.get_plugin('metrixpp.mpp.dbf').get_loader()
        # get previous db file loader
        loader_prev = self.get_plugin('metrixpp.mpp.dbf').get_loader_prev()
        
        exit_code = 0
        for path in (args if len(args) > 0 else [""]):
            added_lines = 0
            file_iterator = loader.iterate_file_data(path)
            if file_iterator == None:
                utils.report_bad_path(path)
                exit_code += 1
                continue
            for file_data in file_iterator:
                added_lines += self._compare_file(file_data, loader, loader_prev)
            cout.notify(path, '', cout.SEVERITY_INFO,
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
        matcher = utils.FileRegionsMatcher(file_data, file_data_prev)
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
