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

import re

import core.api

class Plugin(core.api.Plugin, core.api.IConfigurable):
    
    MODE_NEW     = 0x01
    MODE_TREND   = 0x03
    MODE_TOUCHED = 0x07
    MODE_ALL     = 0x15
    
    
    def declare_configuration(self, parser):
        self.parser = parser
        parser.add_option("--warn-mode", "--wm", default='all', choices=['new', 'trend', 'touched', 'all'],
                         help="Defines the warnings mode. "
                         "'new' - warnings for new regions only, "
                         "'trend' - warnings for new regions and for bad trend of modified regions, "
                         "'touched' - warnings for new regions and modified regions, "
                         "'all' - all warnings active "
                         "[default: %default]")

        parser.add_option("--min-limit", "--min", action="multiopt",
                          help="A threshold per 'namespace:field' metric in order to select regions, "
                          "which have got metric value less than the specified limit. "
                          "This option can be specified multiple times, if it is necessary to apply several limits. "
                          "Should be in the format: <namespace>:<field>:<limit-value>, for example: "
                          "'std.code.lines:comments:1'.")
        parser.add_option("--max-limit", "--max", action="multiopt",
                          help="A threshold per 'namespace:field' metric in order to select regions, "
                          "which have got metric value more than the specified limit. "
                          "This option can be specified multiple times, if it is necessary to apply several limits. "
                          "Should be in the format: <namespace>:<field>:<limit-value>, for example: "
                          "'std.code.complexity:cyclomatic:7'.")
        
    def configure(self, options):
        if options.__dict__['warn_mode'] == 'new':
            self.mode = self.MODE_NEW
        elif options.__dict__['warn_mode'] == 'trend':
            self.mode = self.MODE_TREND
        elif options.__dict__['warn_mode'] == 'touched':
            self.mode = self.MODE_TOUCHED
        elif options.__dict__['warn_mode'] == 'all':
            self.mode = self.MODE_ALL
            
        if self.mode != self.MODE_ALL and options.__dict__['db_file_prev'] == None:
            self.parser.error("The mode '" + options.__dict__['warn_mode'] + "' for 'general.warn' option requires '--db-file-prev' option set")

        class Limit(object):
            def __init__(self, limit_type, limit, namespace, field, db_filter):
                self.type = limit_type
                self.limit = limit
                self.namespace = namespace
                self.field = field
                self.filter = db_filter
                
            def __repr__(self):
                return "namespace '" + self.namespace + "', filter '" + str(self.filter) + "'"
        
        self.limits = []
        pattern = re.compile(r'''([^:]+)[:]([^:]+)[:]([-+]?[0-9]+(?:[.][0-9]+)?)''')
        if options.__dict__['max_limit'] != None:
            for each in options.__dict__['max_limit']:
                match = re.match(pattern, each)
                if match == None:
                    self.parser.error("Invalid format of the '--max-limit' option: " + each)
                limit = Limit("max", float(match.group(3)), match.group(1), match.group(2), (match.group(2), '>', float(match.group(3))))
                self.limits.append(limit)
        if options.__dict__['min_limit'] != None:
            for each in options.__dict__['min_limit']:  
                match = re.match(pattern, each)
                if match == None:
                    self.parser.error("Invalid format of the '--min-limit' option: " + each)
                limit = Limit("min", float(match.group(3)), match.group(1), match.group(2), (match.group(2), '<', float(match.group(3))))
                self.limits.append(limit)
                
    def verify_namespaces(self, valid_namespaces):
        valid = []
        for each in valid_namespaces:
            valid.append(each)
        for each in self.limits:
            if each.namespace not in valid:
                self.parser.error("Invalid limit option (namespace does not exist): " + each.namespace)

    def verify_fields(self, namespace, valid_fields):
        valid = []
        for each in valid_fields:
            valid.append(each)
        for each in self.limits:
            if each.namespace == namespace:
                if each.field not in valid:
                    self.parser.error("Invalid limit option (field does not exist): " + each.namespace + ":" + each.field)
                    
    def iterate_limits(self):
        for each in self.limits:
            yield each   

    def is_mode_matched(self, limit, value, diff, is_modified):
        if is_modified == None:
            return True
        if self.mode == self.MODE_ALL:
            return True 
        if self.mode == self.MODE_TOUCHED and is_modified == True:
            return True 
        if self.mode == self.MODE_TREND and is_modified == True:
            if limit < value and diff > 0:
                return True
            if limit > value and diff < 0:
                return True
        return False
        