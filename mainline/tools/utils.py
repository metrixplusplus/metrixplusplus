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
import re

def check_db_metadata(loader, loader_prev):
    for each in loader.iterate_properties():
        prev = loader_prev.get_property(each.name)
        if prev != each.value:
            logging.warn("Previous data file has got different metadata:")
            logging.warn(" - identification of change trends can be not reliable")
            logging.warn(" - use 'info' tool to view more details")
            return 1
    return 0

def preprocess_path(path):
    path = re.sub(r'''[\\]+''', "/", path)
    logging.info("Processing: " + path)
    return path

def report_bad_path(path):
    logging.error("Specified path '" + path + "' is invalid: not found in the database records.")
    
    