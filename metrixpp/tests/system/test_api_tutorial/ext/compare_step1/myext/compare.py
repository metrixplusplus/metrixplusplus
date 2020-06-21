#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

from metrixpp.mpp import api

class Plugin(api.Plugin, api.IRunable):
    
    def run(self, args):
        print(args)
        return 0

