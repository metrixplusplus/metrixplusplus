'''
Created on 26/06/2012

@author: konstaa
'''


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