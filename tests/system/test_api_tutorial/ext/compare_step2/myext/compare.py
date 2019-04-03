#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
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

