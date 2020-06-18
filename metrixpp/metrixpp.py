#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

import time
import sys
import logging
import os
import itertools

from .mpp import log
from .mpp.internal import loader as plugin_loader

def main():
    
    os.environ['METRIXPLUSPLUS_INSTALL_DIR'] = os.path.dirname(os.path.abspath(__file__))

    command = ""
    if len(sys.argv) > 1:
        command = sys.argv[1]

    loader = plugin_loader.Loader()
    mpp_paths = []
    if 'METRIXPLUSPLUS_PATH' in list(os.environ.keys()):
        mpp_paths = os.environ['METRIXPLUSPLUS_PATH'].split(os.pathsep)
    args = loader.load(command, mpp_paths, sys.argv[2:])
    exit_code = loader.run(args)
    loader.unload()
    return exit_code
    
def start():
    ts = time.time()
    log.set_default_format()

    exit_code = main()
    time_spent = round((time.time() - ts), 2)
    if 'METRIXPLUSPLUS_TEST_GENERATE_GOLDS' in list(os.environ.keys()) and \
        os.environ['METRIXPLUSPLUS_TEST_GENERATE_GOLDS'] == "True":
        time_spent = 1 # Constant value if under tests
    logging.warning("Done (" + str(time_spent) +" seconds). Exit code: " + str(exit_code))
    exit(exit_code)

if __name__ == '__main__':
    start()
