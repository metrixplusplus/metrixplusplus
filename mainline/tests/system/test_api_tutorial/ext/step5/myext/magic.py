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

import mpp.api
import re

class Plugin(mpp.api.Plugin,
             mpp.api.IConfigurable,
             mpp.api.Child,
             mpp.api.MetricPluginMixin):
    
    def declare_configuration(self, parser):
        parser.add_option("--myext.magic.numbers", "--mmn",
            action="store_true", default=False,
            help="Enables collection of magic numbers metric [default: %default]")
    
    def configure(self, options):
        self.is_active_numbers = options.__dict__['myext.magic.numbers']
    
    def initialize(self):
        # improve pattern to find declarations of constants
        pattern_to_search = re.compile(
            r'''((const\s+([_a-zA-Z][_a-zA-Z0-9]*\s+)+[=]\s*)[-+]?[0-9]+\b)|(\b[0-9]+\b)''')
        self.declare_metric(self.is_active_numbers,
                            self.Field('numbers', int),
                            # give a pair of pattern + custom counter logic class
                            (pattern_to_search, self.NumbersCounter),
                            marker_type_mask=mpp.api.Marker.T.CODE,
                            region_type_mask=mpp.api.Region.T.ANY)
        
        super(Plugin, self).initialize(fields=self.get_fields())
        
        if self.is_active() == True:
            self.subscribe_by_parents_interface(mpp.api.ICode)
    
    # implement custom counter behavior:
    # increments counter by 1 only if single number spotted,
    # but not declaration of a constant
    class NumbersCounter(mpp.api.MetricPluginMixin.IterIncrementCounter):
        def increment(self, match):
            if match.group(0).startswith('const'):
                return 0
            return 1
