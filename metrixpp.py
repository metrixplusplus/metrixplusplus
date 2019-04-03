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
import subprocess
import itertools

import mpp.log
import mpp.internal.loader

def main():
    
    os.environ['METRIXPLUSPLUS_INSTALL_DIR'] = os.path.dirname(os.path.abspath(__file__))
    
    exemode = None
    if len(sys.argv[1:]) != 0:
        exemode = sys.argv[1]
    if exemode != "-R" and exemode != "-D":
        exemode = '-D' # TODO implement install and release mode
        # inject '-D' or '-R' option
        #profile_args = ['-m', 'cProfile']
        profile_args = []
        exit(subprocess.call(itertools.chain([sys.executable], profile_args, [sys.argv[0], '-D'], sys.argv[1:])))

    command = ""
    if len(sys.argv[1:]) > 1:
        command = sys.argv[2]

    loader = mpp.internal.loader.Loader()
    mpp_paths = []
    if 'METRIXPLUSPLUS_PATH' in os.environ.keys():
        mpp_paths = os.environ['METRIXPLUSPLUS_PATH'].split(os.pathsep)
    args = loader.load(command, mpp_paths, sys.argv[3:])
    exit_code = loader.run(args)
    loader.unload()
    return exit_code
    
def start():
    ts = time.time()
    mpp.log.set_default_format()

    exit_code = main()
    time_spent = round((time.time() - ts), 2)
    if 'METRIXPLUSPLUS_TEST_GENERATE_GOLDS' in os.environ.keys() and \
        os.environ['METRIXPLUSPLUS_TEST_GENERATE_GOLDS'] == "True":
        time_spent = 1 # Constant value if under tests
    logging.warning("Done (" + str(time_spent) +" seconds). Exit code: " + str(exit_code))
    exit(exit_code)

if __name__ == '__main__':
    start()