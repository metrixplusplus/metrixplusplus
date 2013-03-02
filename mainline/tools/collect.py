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
import os.path

import core.loader
import core.cmdparser

import core.api
class Tool(core.api.ITool):
    def run(self, tool_args):
        return main(tool_args)

def main(tool_args):
    loader = core.loader.Loader()
    parser =core.cmdparser.MultiOptionParser(usage="Usage: %prog [options] collect -- [path 1] ... [path N]")
    args = loader.load(os.path.join(os.environ['METRIXPLUSPLUS_INSTALL_DIR'], 'ext'), parser, tool_args)
    logging.debug("Registered plugins:")
    logging.debug(loader)
    exit_code = loader.run(args)
    loader.unload()
    return exit_code
    