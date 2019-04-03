#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

import mpp.api

class Plugin(mpp.api.Plugin, mpp.api.IRunable):
    
    def run(self, args):
        print args
        return 0

