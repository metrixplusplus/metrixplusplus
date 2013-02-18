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
import time

import core.loader
import core.log
import core.cmdparser


def main():
    loader = core.loader.Loader()
    parser =core.cmdparser.MultiOptionParser(usage="Usage: %prog [options] -- <path 1> ... <path N>")
    args = loader.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ext'), parser)
    logging.debug("Registered plugins:")
    logging.debug(loader)
    exit_code = loader.run(args)
    loader.unload()
    return exit_code
            
if __name__ == '__main__':
    ts = time.time()
    core.log.set_default_format()
    exit_code = main()
    logging.warning("Exit code: " + str(exit_code) + ". Time spent: " + str(round((time.time() - ts), 2)) + " seconds. Done")
    exit(exit_code) # number of reported messages, errors are reported as non-handled exceptions